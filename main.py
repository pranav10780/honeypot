import socket
import paramiko
import threading
import argparse
import json
import csv
import os
import time
import uuid
from datetime import datetime, timezone

SSH_BANNER = "SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.19"

parser = argparse.ArgumentParser(description="A sample CLI tool.")
parser.add_argument("-d", "--development", action="store_true",
                     help="Prevents the key change issue while developing")
parser.add_argument("-o", "--output", default=None,
                     help="Path to the output file. If omitted, events are only printed to the terminal.")
parser.add_argument("-f", "--format", choices=["json", "csv", "text", "all"], default="text",
                     help="Output file format. 'all' writes json+csv+text simultaneously. Ignored if -o is not given.")
args = parser.parse_args()


class EventLogger:
    """Writes captured events to file(s) in the chosen format(s). If no output
    path is given, this is a no-op and events are only ever seen via the
    print() calls already in SSHServer."""

    CSV_FIELDS = ["ts", "session_id", "src_ip", "src_port", "event",
                  "username", "password", "key_type", "key_fp", "key_full"]

    def __init__(self, output, fmt):
        self.enabled = output is not None
        self.lock = threading.Lock()

        if not self.enabled:
            return

        if fmt == "all":
            base, _ = os.path.splitext(output)
            self.paths = {
                "json": base + ".json",
                "csv": base + ".csv",
                "text": base + ".txt",
            }
        else:
            self.paths = {fmt: output}

        for kind, path in self.paths.items():
            dirpath = os.path.dirname(path)
            if dirpath:
                os.makedirs(dirpath, exist_ok=True)

            if kind == "csv" and not os.path.exists(path):
                with open(path, "w", newline="") as f:
                    csv.DictWriter(f, fieldnames=self.CSV_FIELDS).writeheader()

            if kind == "json" and not os.path.exists(path):
                with open(path, "w") as f:
                    json.dump([], f)

    def log_event(self, session_id, addr, event_type, **fields):
        if not self.enabled:
            return

        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "src_ip": addr[0],
            "src_port": addr[1],
            "event": event_type,
            **fields,
        }

        with self.lock:
            for kind, path in self.paths.items():
                if kind == "json":
                    self._write_json(path, record)
                elif kind == "csv":
                    self._write_csv(path, record)
                elif kind == "text":
                    self._write_text(path, record, fields)

    def _write_json(self, path, record):
        with open(path, "r+") as f:
            data = json.load(f)
            data.append(record)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

    def _write_csv(self, path, record):
        row = {k: record.get(k, "") for k in self.CSV_FIELDS}
        with open(path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=self.CSV_FIELDS).writerow(row)

    def _write_text(self, path, record, fields):
        detail = " ".join(f"{k}={v}" for k, v in fields.items())
        line = (f"[{record['ts']}] {record['src_ip']}:{record['src_port']} "
                f"session={record['session_id']} {record['event']} {detail}")
        with open(path, "a") as f:
            f.write(line + "\n")


event_logger = EventLogger(args.output, args.format)


class SSHServer(paramiko.ServerInterface):
    def __init__(self, addr):
        self.addr = addr
        self.session_id = f"{addr[0]}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        super().__init__()

    def get_allowed_auths(self, username):
        return 'password,publickey'

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        print(f"[!] CAPTURED LOGIN - Username: {username!r} | Password: {password!r}")
        event_logger.log_event(self.session_id, self.addr, "auth_password",
                                username=username, password=password)
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        key_type = key.get_name()
        key_fp = key.get_fingerprint().hex()
        key_full = f"{key_type} {key.get_base64()}"

        print(f"[!] CAPTURED KEY AUTH - Username: {username}")
        print(f"    Key: {key_full}")
        print(f"    Fingerprint: {key_fp}")
        event_logger.log_event(self.session_id, self.addr, "auth_pubkey",
                                username=username, key_type=key_type,
                                key_fp=key_fp, key_full=key_full)
        return paramiko.AUTH_FAILED

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        return True


def handle_client(client, addr, host_key):
    print(f"\n[*] Connection received from {addr[0]}:{addr[1]}")

    with paramiko.Transport(client) as transport:
        transport.local_version = SSH_BANNER
        transport.add_server_key(host_key)

        server = SSHServer(addr)
        event_logger.log_event(server.session_id, addr, "connection_received")

        try:
            transport.start_server(server=server)
        except paramiko.SSHException as e:
            print(f"[-] SSH negotiation failed: {e}")
            return
        except (EOFError, ConnectionResetError, socket.error) as e:
            print(f"[-] Connection dropped abruptly by client: {e}")
            return
        except Exception as e:
            print(f"[-] Unexpected error: {e}")
            return

        channel = transport.accept(20)
        if channel is None:
            print("[-] Attacker dropped connection before opening a channel.")
            return

        print("[+] Attacker successfully 'authenticated' and opened a channel.")
        event_logger.log_event(server.session_id, addr, "channel_opened")

        # add a shell here
        channel.close()
        time.sleep(0.2)
        transport.close()

def start_honeypot():
    if args.development:
        host_key = paramiko.RSAKey(filename='./testing/host_key')
    else:
        host_key = paramiko.RSAKey.generate(2048)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 4444))
    sock.listen(100)

    if args.output:
        print(f"[*] Honeypot listening on port 4444... (logging {args.format} to {args.output})")
    else:
        print("[*] Honeypot listening on port 4444... (no -o given, terminal output only)")

    try:
        while True:
            client, addr = sock.accept()
            threading.Thread(target=handle_client, args=(client, addr, host_key), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[*] Caught Ctrl+C. Shutting down gracefully...")
    finally:
        sock.close()
        print("[*] Honeypot offline.")


if __name__ == "__main__":
    start_honeypot()
