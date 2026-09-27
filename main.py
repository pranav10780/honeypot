import socket
import paramiko
import threading
import argparse
import json
import csv
import os

parser = argparse.ArgumentParser(description="A sample CLI tool.")
parser.add_argument("-d", "--development", action="store_true", help="Prevents the key change issue while developing")
parser.add_argument("-o", "--output", default="./honeypot.json", help="Path to the output file")
parser.add_argument("-f", "--format", choices=["json", "csv", "text"], default="jsonl", help="Output file format")
args = parser.parse_args()

class SSHServer(paramiko.ServerInterface):
    def get_allowed_auths(self, username):
        return 'password,publickey'

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        print(f"[!] CAPTURED LOGIN - Username: {username} | Password: {password}")
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        key_type = key.get_name()
        key_b64 = key.get_fingerprint().hex()

        full_key_string = f"{key_type} {key_b64}"
        
        print(f"[!] CAPTURED KEY AUTH - Username: {username}")
        print(f"    Key: {full_key_string}")
        
        return paramiko.AUTH_FAILED

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        return True

def handle_client(client, addr):
            print(f"\n[*] Connection received from {addr[0]}:{addr[1]}")
            transport = paramiko.Transport(client)
            transport.local_version = "SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.19"
            transport.add_server_key(host_key)
        
            server = SSHServer()
            try:
                transport.start_server(server=server)
            except paramiko.SSHException as e:
                print(f"[-] SSH negotiation failed: {e}")
                continue
            except (EOFError, ConnectionResetError, socket.error) as e:
                print(f"[-] Connection dropped abruptly by client: {e}")
                continue
            except Exception as e:
                print(f"[-] Unexpected error: {e}")
                continue

            channel = transport.accept(20)
            if channel is None:
                print("[-] Attacker dropped connection before opening a channel.")
                continue
            
            print("[+] Attacker successfully 'authenticated' and opened a channel.")
        
            #add a shell here
            channel.close()
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
    print("[*] Honeypot listening on port 4444...")

    try:
        while True:
            client, addr = sock.accept()
            threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()
        
    except KeyboardInterrupt:
        print("\n[*] Caught Ctrl+C. Shutting down gracefully...")
    finally:
        sock.close()
        print("[*] Honeypot offline.")

if __name__ == "__main__":
    start_honeypot()
