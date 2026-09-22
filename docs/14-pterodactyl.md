# Pterodactyl

Documentation for the Pterodactyl game-server infrastructure running on VM108 on `pve-2`.

---

## Overview

Pterodactyl provides the game-server management platform for the homelab.

The deployment consists of:

* Pterodactyl Panel
* Pterodactyl Wings
* Docker
* MariaDB
* Redis
* NetBird
* Minecraft game-server infrastructure

The Panel and Wings run together on a dedicated Debian VM rather than an LXC. This keeps Docker and Wings isolated from the Proxmox host and avoids the additional nesting considerations associated with running Docker inside an LXC.

The current deployment is operational.

---

## Host and VM

### Proxmox host

Pterodactyl runs on:

```text
Host: pve-2
IP:   192.168.20.101
```

`pve-2` is the Dell OptiPlex 9020 SFF.

The Pterodactyl VM is:

```text
VMID:       108
Hostname:   pterodactyl
LAN IP:     192.168.20.111
```

### VM resources

Current VM configuration:

| Resource              | Configuration   |
| --------------------- | --------------- |
| vCPU                  | 6               |
| RAM                   | 12 GB           |
| Disk                  | 40 GB local-lvm |
| Machine               | Q35             |
| Firmware              | OVMF / UEFI     |
| Network               | VirtIO          |
| QEMU Guest Agent      | Enabled         |
| NUMA                  | Disabled        |
| Ballooning            | Disabled        |
| Nested virtualisation | Disabled        |

The VM runs Debian 13 Trixie.

Current kernel:

```text
6.12.107+deb13-amd64
```

---

## Installed Software

The VM currently provides:

| Software          | Version / Configuration |
| ----------------- | ----------------------- |
| Docker Engine     | 29.8.0                  |
| PHP               | 8.3.33                  |
| MariaDB           | 11.8.6                  |
| Redis             | Installed               |
| Composer          | 2.10.3                  |
| Nginx             | Installed               |
| Pterodactyl Panel | Installed               |
| Wings             | 1.13.3                  |
| NetBird           | 0.78.1                  |

---

# Pterodactyl Panel

The Panel is installed at:

```text
/var/www/pterodactyl
```

The configured application URL is:

```text
https://panel.robynshomelab.dev
```

The Panel uses:

* MariaDB database: `panel`
* Redis for queue processing
* Nginx/PHP-FPM

The Panel itself is not directly exposed to the public internet from VM108.

---

## Panel Reverse Proxy

The public Panel hostname is handled by the existing Nginx reverse proxy on CT106.

```text
CT106
192.168.20.94
```

The traffic path is:

```text
Internet / LAN / NetBird
          │
          ▼
panel.robynshomelab.dev
          │
          ▼
CT106 Nginx
192.168.20.94
          │
          ▼
Pterodactyl VM
192.168.20.111
          │
          ▼
Pterodactyl Panel
```

The existing CT106 Nginx configuration should be preserved.

Minecraft traffic does **not** use this Nginx reverse proxy because Minecraft is a raw TCP service rather than an HTTP application.

---

# Pterodactyl Wings

Wings is installed at:

```text
/usr/local/bin/wings
```

Configuration:

```text
/etc/pterodactyl/config.yml
```

The configuration file is protected with mode `600`.

Wings runs as a systemd service:

```text
/etc/systemd/system/wings.service
```

Current service configuration includes:

```text
Daemon port: 8080
SFTP port:   2022
```

Game-server data is stored under:

```text
/var/lib/pterodactyl/volumes
```

Wings manages the game-server containers through Docker.

---

# Docker

Pterodactyl uses Docker to isolate individual game servers.

The Pterodactyl Docker network is managed by Wings/Pterodactyl rather than being manually recreated as part of normal administration.

Docker is therefore responsible for translating the Pterodactyl allocations into the corresponding container networking.

Do not manually modify Docker's generated NAT rules unless there is a specific networking problem requiring it.

---

# Storage

The Pterodactyl VM has its own local system disk for the operating system and Pterodactyl software.

Game-server storage is provided through the homelab's storage infrastructure.

The 4 TB WD Blue HDD is owned by `pve-2` and is mounted by the Proxmox host as:

```text
/mnt/homelab-data
```

The storage hierarchy includes:

```text
/mnt/homelab-data/
├── media/
├── downloads/
├── games/
├── backups/
└── shared/
```

The `games` storage is exported over NFS and is mounted by VM108 for game-server storage where required.

This keeps the large game-server storage separate from the VM's relatively small local system disk.

---

# NetBird

VM108 runs its own independent NetBird peer.

```text
NetBird IP:
100.113.229.169/16

NetBird hostname:
pterodactyl.netbird.cloud
```

NetBird version:

```text
0.78.1
```

The VM is an independent NetBird peer.

It should **not** be treated as being routed through CT101. CT101 and VM108 have separate NetBird identities and connections.

---

## NetBird connection persistence

The NetBird service runs through systemd:

```text
netbird.service
```

The service is enabled and intended to start automatically with the VM.

A systemd drop-in is configured with:

```ini
Environment="NB_LAZY_CONN=off"
```

This was part of the work performed to improve persistent connectivity.

---

# Minecraft Server

The first deployed game server on Pterodactyl is Minecraft Java Edition.

Current server:

```text
Minecraft: 1.21.1
Protocol: 767
```

The server uses port:

```text
25565
```

The Pterodactyl allocation includes:

```text
192.168.20.111:25565
100.113.229.169:25565
```

The Docker container is published on both addresses.

The final public Minecraft service does not require the home router to forward port `25565`.

---

# Minecraft Networking

The final Minecraft networking architecture uses NetBird Reverse Proxy.

The public endpoint is:

```text
minecraft.robynshomelab.dev:17161
```

The NetBird Reverse Proxy service forwards TCP traffic to:

```text
100.113.229.169:25565
```

The traffic is then DNATed from the NetBird interface to the VM's LAN address.

The final path is:

```text
Minecraft Client
      │
      ▼
minecraft.robynshomelab.dev:17161
      │
      ▼
NetBird Reverse Proxy
      │
      ▼
NetBird peer
pterodactyl
100.113.229.169:25565
      │
      ▼
wt0
      │
      ▼
iptables DNAT
      │
      ▼
192.168.20.111:25565
      │
      ▼
Docker / Pterodactyl
      │
      ▼
Minecraft 1.21.1
```

---

# Minecraft DNAT

The NetBird address is not the address where the Minecraft container ultimately listens on the LAN.

The following DNAT rule translates incoming TCP traffic from the NetBird interface:

```bash
/usr/sbin/iptables -t nat -I PREROUTING 1 \
  -i wt0 \
  -p tcp \
  -d 100.113.229.169 \
  --dport 25565 \
  -j DNAT \
  --to-destination 192.168.20.111:25565
```

This rule is persisted using:

```text
netfilter-persistent
```

The persistent rule is:

```text
-A PREROUTING -d 100.113.229.169/32 -i wt0 -p tcp -m tcp --dport 25565 -j DNAT --to-destination 192.168.20.111:25565
```

### Important command-path note

The root shell on VM108 does not currently include `/usr/sbin` in its normal `$PATH`.

Therefore, use:

```text
/usr/sbin/iptables
/usr/sbin/nft
```

rather than:

```text
iptables
nft
```

The NAT table is managed through the `iptables-nft` compatibility layer.

Do not directly modify the corresponding nftables NAT table unless there is a specific reason to do so.

---

# Minecraft Public Access Problem

The original attempt to expose Minecraft used NetBird's CLI exposure feature:

```bash
netbird expose --protocol tcp 25565
```

This creates a temporary public reverse-proxy service.

Several temporary endpoints were created during testing, including:

```text
upokwfkzqzjy.eu1.netbird.services:29387
```

and:

```text
kkvy1yzwqnxv.eu1.netbird.services:46767
```

These endpoints were capable of connecting to Minecraft.

However, the connection behaviour was intermittent.

A connection could:

1. Successfully connect to Minecraft.
2. Immediately fail with `connection refused`.
3. Work again later without changes to Minecraft, Docker, Pterodactyl or the local network.

This initially made it unclear whether the problem was caused by:

* Minecraft
* Docker
* Pterodactyl
* Wings
* NetBird
* NAT
* the public NetBird proxy

---

# Diagnosis

The Minecraft server itself was confirmed to be healthy.

A direct local connection to:

```text
192.168.20.111:25565
```

succeeded.

The Minecraft protocol status handshake returned:

```text
Minecraft 1.21.1
Protocol 767
```

The NetBird interface was also confirmed to receive the connection attempts.

Most importantly, the DNAT rule's packet counters increased during failed public connection attempts.

This proved that the failed connections were reaching:

```text
wt0
```

and entering the DNAT path.

Therefore, the problem was **not a missing DNAT rule** and was not caused by Minecraft failing to listen on the requested port.

---

# Temporary NetBird Exposure Behaviour

Further testing showed that the temporary `kkvy` endpoint could resolve through multiple public NetBird proxy addresses.

Some connection attempts were accepted while others were refused.

The same temporary endpoint could also successfully complete a full Minecraft status handshake.

This established that:

* Minecraft was working.
* Docker was working.
* Pterodactyl was working.
* The VM's NetBird connection was working.
* The DNAT path was working.
* The intermittent behaviour was associated with the ephemeral public NetBird exposure path.

The exact internal NetBird mechanism responsible for the intermittent behaviour was not conclusively established.

It should therefore **not** be documented as confirmed rate limiting, DDoS protection, connection throttling, or another specific NetBird feature.

The verified conclusion is simply that the temporary `netbird expose` path was unsuitable as the permanent Minecraft exposure mechanism.

---

# Permanent NetBird Reverse Proxy

The final solution was to use a permanent NetBird Reverse Proxy service rather than the temporary CLI exposure.

A dedicated custom domain was created:

```text
minecraft.robynshomelab.dev
```

The custom domain was verified successfully by NetBird.

NetBird required the following wildcard DNS verification record:

```text
*.minecraft.robynshomelab.dev
CNAME → eu1.netbird.services
```

The record was configured through Cloudflare as DNS-only.

NetBird then provided the permanent Minecraft service.

Final service:

```text
Domain:
minecraft.robynshomelab.dev

Public port:
17161

Protocol:
TCP

Backend:
100.113.229.169:25565
```

The final client connection address is:

```text
minecraft.robynshomelab.dev:17161
```

---

# Minecraft Verification

The permanent endpoint was tested using a raw Minecraft protocol status handshake.

The endpoint returned:

```json
{
  "version": {
    "name": "1.21.1",
    "protocol": 767
  },
  "enforcesSecureChat": true,
  "description": "A Minecraft Server",
  "players": {
    "max": 20,
    "online": 1
  }
}
```

This confirmed that the permanent NetBird endpoint was not merely accepting TCP connections; it was successfully forwarding Minecraft protocol traffic to the actual server.

The endpoint was then tested using the actual Minecraft Java client.

The server was successfully joined in-game.

A packet capture on `wt0` also showed the permanent hostname:

```text
minecraft.robynshomelab.dev
```

arriving at VM108.

This provided independent confirmation that traffic from the permanent public endpoint was reaching the Pterodactyl VM.

---

# Temporary Exposure Endpoints

The following endpoints were created during troubleshooting:

```text
upokwfkzqzjy.eu1.netbird.services:29387
kkvy1yzwqnxv.eu1.netbird.services:46767
```

These were temporary `netbird expose` sessions.

They are **not part of the final infrastructure**.

NetBird documents CLI `expose` sessions as temporary services that remain active only while the command is running; they are automatically removed when the session ends.

The permanent dashboard Reverse Proxy service replaces these temporary endpoints.

---

# Cloudflare DNS

Cloudflare remains authoritative for:

```text
robynshomelab.dev
```

The final Minecraft NetBird custom-domain configuration uses:

```text
*.minecraft.robynshomelab.dev
CNAME → eu1.netbird.services
```

DNS is configured as DNS-only.

The temporary records created during the troubleshooting process have been removed.

In particular, the old Minecraft CNAME and SRV records associated with the previous reverse-proxy service are no longer required.

The current NetBird Reverse Proxy service is the authoritative public path for Minecraft.

---

# Final Minecraft Architecture

```text
                         INTERNET
                            │
                            ▼
          minecraft.robynshomelab.dev:17161
                            │
                            ▼
                  NetBird Reverse Proxy
                            │
                            ▼
                 pterodactyl.netbird.cloud
                   100.113.229.169
                            │
                            ▼
                         wt0
                            │
                            ▼
                   iptables DNAT
                            │
                            ▼
                  192.168.20.111:25565
                            │
                            ▼
                       Docker
                            │
                            ▼
                    Minecraft 1.21.1
```

No Minecraft port forwarding is configured on the home router.

---

# Security Model

The Pterodactyl Panel and Wings management interfaces should remain private.

The intended access model is:

| Service            | Access                               |
| ------------------ | ------------------------------------ |
| Panel              | Nginx / LAN / NetBird                |
| Wings API          | Private infrastructure               |
| SFTP               | LAN / NetBird                        |
| Minecraft          | Public through NetBird Reverse Proxy |
| Other game servers | Only when explicitly exposed         |

The Minecraft public endpoint exposes the game service only.

It does not expose the Pterodactyl Panel or Wings management interfaces.

The Pterodactyl VM should not be given unnecessary public ports.

---

# Firewall Considerations

The final firewall configuration should account for Docker and Wings.

Do not blindly apply a generic UFW configuration to the VM because Docker creates its own networking/NAT rules.

The intended security policy remains:

* Default-deny unnecessary inbound traffic.
* Allow established/related connections.
* Allow loopback.
* SSH only from LAN/NetBird where possible.
* Panel access through the existing reverse proxy.
* Wings management interfaces kept private.
* SFTP limited to LAN/NetBird where possible.
* Game-server ports exposed only when required.
* NetBird traffic permitted as required.
* Docker networking left functional.

Any future firewall hardening must preserve:

```text
wt0 → DNAT → 192.168.20.111:25565
```

for the Minecraft service.

---

# Current Status

## Pterodactyl

**DEPLOYED / VERIFIED**

Panel:

```text
https://panel.robynshomelab.dev
```

VM:

```text
192.168.20.111
```

Wings:

```text
1.13.3
```

Docker:

```text
29.8.0
```

---

## Minecraft

**DEPLOYED / VERIFIED**

Server:

```text
Minecraft Java 1.21.1
Protocol 767
```

Internal:

```text
192.168.20.111:25565
```

NetBird:

```text
100.113.229.169:25565
```

Public:

```text
minecraft.robynshomelab.dev:17161
```

Transport:

```text
TCP
```

---

## NetBird

**DEPLOYED / VERIFIED**

VM108 NetBird:

```text
Version: 0.78.1
IP:      100.113.229.169/16
FQDN:    pterodactyl.netbird.cloud
```

Permanent Minecraft Reverse Proxy:

```text
minecraft.robynshomelab.dev:17161
```

Temporary `netbird expose` endpoints are no longer part of the architecture.

---

# Operational Notes

### Do not remove the DNAT rule

The DNAT rule is required for the current public Minecraft path.

### Do not recreate the temporary CLI exposure

There is no need to use:

```bash
netbird expose --protocol tcp 25565
```

for normal Minecraft access anymore.

That was a troubleshooting mechanism.

### Do not move Minecraft to CT106 Nginx

CT106 Nginx remains responsible for HTTP/HTTPS reverse proxying.

Minecraft is a Layer-4 TCP service and is intentionally handled by NetBird Reverse Proxy.

### Do not add router port forwarding

The final design intentionally avoids forwarding TCP `25565` through the ISP router.

### Preserve the existing Panel configuration

The working:

```text
panel.robynshomelab.dev
```

→ CT106 Nginx → VM108

architecture should remain unchanged.

---

# Future Work

Potential future Pterodactyl work includes:

* Additional game servers.
* Additional Pterodactyl allocations.
* Monitoring game-server availability through Uptime Kuma.
* Monitoring VM/Docker resources through Beszel.
* Backup improvements for game-server data.
* Firewall hardening.
* Further testing of game-server access from external networks.
* Integration with the eventual Homepage dashboard.

The Minecraft networking implementation itself should now be considered **complete and stable**.
