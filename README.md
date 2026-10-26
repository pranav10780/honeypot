# SSH Honeypot

A lightweight, low-interaction SSH honeypot written in Python with [Paramiko](https://www.paramiko.org/).  
It poses as an OpenSSH server on Ubuntu, accepts any password login, records every credential and public key that attackers try, and logs everything to JSON, CSV, and/or plain text.

## Features

- **Credential capture:** logs the username and password from every password attempt.
- **Public key capture:** logs key type, fingerprint, and the full public key for every key-auth attempt.
- **Customisable banner:** advertises `SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.19` by default.
- **Concurrent:** one thread per connection, so many bots can connect at once.
- **Flexible logging:** write JSON, CSV, text, or all three at once. If you give no output path, events only print to the terminal.
- **Session tracking:** each connection gets a unique session ID so you can group events from one attacker session.

## How it works

This honey pot always shows **failed** for any attempt using a public key which causes the ssh-agent to keep on trying until all the users keys are exhausted and finally asks for password which will always return **success**. This tool can also log when an attacker connects and opens an channel

No commands are ever executed and no real shell is exposed.

## Requirements

- Python 3
- [paramiko](https://pypi.org/project/paramiko/)

```bash
pip install paramiko
```

## Usage

```bash
python3 main.py [-d] [-o OUTPUT] [-f {json,csv,text,all}]
```

| Flag | Description |
|------|-------------|
| `-d`, `--development` | Load the host key from `./testing/host_key` instead of generating a new one. Stops SSH clients from warning about a changed host key between restarts. |
| `-o`, `--output PATH` | Where to write the log file. If omitted, events are only printed to the terminal. |
| `-f`, `--format` | `json`, `csv`, `text` (default), or `all`. Ignored if `-o` is not given. |

With `-f all`, the file extension in `-o` is replaced, so `-o logs/events.log -f all` writes `logs/events.json`, `logs/events.csv`, and `logs/events.txt`. Missing directories are created automatically.

>NOTE: The given keys in testing is empty.

>NOTE: Without `-d`, a fresh RSA key is generated on every start, so your SSH client will see a "host key changed" warning each time you restart. For local testing, create a persistent key once and use `-d`:

### Examples

```bash
# Terminal output only
python3 main.py

# Log to a JSON file
python3 main.py -o logs/events.json -f json

# Log to all three formats
python3 main.py -o logs/events -f all
```

### Test it

The honeypot listens on **port 4444**:

```bash
ssh -p 4444 root@localhost
```

Any password works. The connection closes right after login.

## Limitations

- No fake shell provided.
- The JSON log is rewritten in full on every event, which gets slow once the file is large. Prefer `csv` or `text` for busy deployments.
- Only RSA host keys are supported.

## Disclaimer

This is for educational purposes only. Only run this on systems and networks you own or are authorized to monitor. Captured passwords are real credentials that attackers have used elsewhere, so protect your log files and handle them responsibly.
