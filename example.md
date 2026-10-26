# Examples

This file is to show what the attacker and the honeypot sees on their respective sides

### Hacker/Attacker

```bash
pranav@server:~/honeypot$ ssh hacker@localhost -p 4444
hacker@localhost's password: 
Connection to localhost closed.
pranav@server:~/honeypot$
```

The attacker just see that the server closed the connection.

```bash
pranav@server:~/honeypot$ nmap -sV -p 4444 localhost -T5
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-10-26 12:43 IST
Nmap scan report for localhost (127.0.0.1)
Host is up (0.000058s latency).

PORT     STATE SERVICE VERSION
4444/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.19 (Ubuntu Linux; protocol 2.0)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.14 seconds
```

If the attacker decides to do a port scan the `SSH_BANNER` can spoof to make it look real

### Defender/Tester/Honeypot

```bash
(.venv) pranav@server:~/honeypot$ python3 ./main.py -f all -d -o hacker
[*] Honeypot listening on port 4444... (logging all to hacker)

[*] Connection received from 127.0.0.1:54494
[!] CAPTURED KEY AUTH - Username: hacker
    Key: ssh-ed25519 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    Fingerprint: xxxxxxxxxxxxxxxxxxxxxxx
[!] CAPTURED KEY AUTH - Username: hacker
    Key: ssh-ed25519 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    Fingerprint: xxxxxxxxxxxxxxxxxxxxxxxxx
[!] CAPTURED LOGIN - Username: 'hacker' | Password: 'hackerman123456789'
[+] Attacker successfully 'authenticated' and opened a channel.
^C
[*] Caught Ctrl+C. Shutting down gracefully...
[*] Honeypot offline.
```

>NOTE: I have 2 keys loaded inside `ssh-agent` which caused it to show both under the same user hacker.


## File examples

This is to show how different file formats look.

### Text

```bash
pranav@server:~/honeypot$ cat hacker.txt 
[2026-10-26T07:10:42.514374+00:00] 127.0.0.1:54494 session=127.0.0.1_1792998642_89329909 connection_received 
[2026-10-26T07:10:42.567890+00:00] 127.0.0.1:54494 session=127.0.0.1_1792998642_89329909 auth_pubkey username=hacker key_type=ssh-ed25519 key_fp=xxxxxxxxxxxxxxxxxxxxxxxx key_full=ssh-ed25519 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
[2026-10-26T07:10:42.568801+00:00] 127.0.0.1:54494 session=127.0.0.1_1792998642_89329909 auth_pubkey username=hacker key_type=ssh-ed25519 key_fp=xxxxxxxxxxxxxxxxxxxxxxxxx key_full=ssh-ed25519 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
[2026-10-26T07:10:47.131840+00:00] 127.0.0.1:54494 session=127.0.0.1_1792998642_89329909 auth_password username=hacker password=hackerman123456789
[2026-10-26T07:10:47.133692+00:00] 127.0.0.1:54494 session=127.0.0.1_1792998642_89329909 channel_opened
```

### JSON

```json
[
  {
    "ts": "2026-10-26T07:10:42.514374+00:00",
    "session_id": "127.0.0.1_1792998642_89329909",
    "src_ip": "127.0.0.1",
    "src_port": 54494,
    "event": "connection_received"
  },
  {
    "ts": "2026-10-26T07:10:42.567890+00:00",
    "session_id": "127.0.0.1_1792998642_89329909",
    "src_ip": "127.0.0.1",
    "src_port": 54494,
    "event": "auth_pubkey",
    "username": "hacker",
    "key_type": "ssh-ed25519",
    "key_fp": "xxxxxxxxxxxxxxxxxxxxxxx",
    "key_full": "ssh-ed25519 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  },
  {
    "ts": "2026-10-26T07:10:42.568801+00:00",
    "session_id": "127.0.0.1_1792998642_89329909",
    "src_ip": "127.0.0.1",
    "src_port": 54494,
    "event": "auth_pubkey",
    "username": "hacker",
    "key_type": "ssh-ed25519",
    "key_fp": "xxxxxxxxxxxxxxxxxxxxxx",
    "key_full": "ssh-ed25519 xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  },
  {
    "ts": "2026-10-26T07:10:47.131840+00:00",
    "session_id": "127.0.0.1_1792998642_89329909",
    "src_ip": "127.0.0.1",
    "src_port": 54494,
    "event": "auth_password",
    "username": "hacker",
    "password": "hackerman123456789"
  },
  {
    "ts": "2026-10-26T07:10:47.133692+00:00",
    "session_id": "127.0.0.1_1792998642_89329909",
    "src_ip": "127.0.0.1",
    "src_port": 54494,
    "event": "channel_opened"
  }
]
```

### CSV

```bash
pranav@server:~/honeypot$ cat hacker.csv 
ts,session_id,src_ip,src_port,event,username,password,key_type,key_fp,key_full
2026-10-26T07:10:42.514374+00:00,127.0.0.1_1792998642_89329909,127.0.0.1,54494,connection_received,,,,,
2026-10-26T07:10:42.567890+00:00,127.0.0.1_1792998642_89329909,127.0.0.1,54494,auth_pubkey,hacker,,ssh-ed25519,xxxxxxxxxxxxx,ssh-ed25519 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
2026-10-26T07:10:42.568801+00:00,127.0.0.1_1792998642_89329909,127.0.0.1,54494,auth_pubkey,hacker,,ssh-ed25519,xxxxxxxxxxxxxxxxxxxxx,ssh-ed25519 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
2026-10-26T07:10:47.131840+00:00,127.0.0.1_1792998642_89329909,127.0.0.1,54494,auth_password,hacker,hackerman123456789,,,
2026-10-26T07:10:47.133692+00:00,127.0.0.1_1792998642_89329909,127.0.0.1,54494,channel_opened,,,,,
```
