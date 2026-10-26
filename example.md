This file is to show what the attacker and the honeypot sees on their respective sides

### Hacker/Attacker

```bash
pranav@server:~/honeypot$ ssh hacker@localhost -p 4444
hacker@localhost's password: 
Connection to localhost closed.
pranav@server:~/honeypot$
```

The attacker just see that the server just closed the connection.

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

>NOTE: I have 2 keys loaded inside `ssh-agent` which caused it to show both undet the same user hacker.
