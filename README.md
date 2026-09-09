# Robyn's Homelab

Documentation and configuration notes for my personal homelab.

The homelab is built around a two-node Proxmox cluster and currently hosts networking, storage, media, monitoring, and game-server infrastructure.

> **Note:** The architecture diagram is currently out of date. It will be rebuilt once the remaining infrastructure work is complete and the homelab has been stable for several months. The individual documentation files contain the current configuration.

---

## Hardware

| Host  | Hardware               | IP               |
| ----- | ---------------------- | ---------------- |
| pve-1 | Dell OptiPlex 3060     | `192.168.20.100` |
| pve-2 | Dell OptiPlex 9020 SFF | `192.168.20.101` |

pve-2 also provides the primary 4TB HDD storage used by the homelab.

---

## Network

```text
LAN:       192.168.20.0/24
Router:    192.168.20.1
```

Pi-hole provides internal DNS, with Unbound providing recursive DNS resolution.

NetBird provides private remote access without router port forwarding.

Cloudflare provides authoritative DNS for `robynshomelab.dev`.

Nginx provides the central reverse proxy and TLS layer.

---

## Services

|    ID | Hostname      | IP               | Service                  |
| ----: | ------------- | ---------------- | ------------------------ |
| CT100 | `pihole`      | `192.168.20.99`  | Pi-hole / Unbound / DDNS |
| CT101 | `netbird`     | `192.168.20.97`  | NetBird routing          |
| CT102 | `jellyfin`    | `192.168.20.98`  | Jellyfin                 |
| CT103 | `mediastack`  | `192.168.20.93`  | Media stack              |
| CT104 | `beszel`      | `192.168.20.96`  | Beszel                   |
| CT105 | `uptime-kuma` | `192.168.20.95`  | Uptime Kuma              |
| CT106 | `nginx`       | `192.168.20.94`  | Nginx / Certbot          |
| VM108 | `pterodactyl` | `192.168.20.111` | Pterodactyl              |

VM107 is currently reserved for a future Homarr deployment.

---

## Storage

The primary storage is a 4TB WD Blue HDD in pve-2.

```text
/mnt/homelab-data/
├── media/
├── downloads/
├── games/
├── backups/
└── shared/
```

NFS is used to provide the required storage shares to other systems.

---

## Media

The media stack runs on CT103 and includes:

* qBittorrent
* Prowlarr
* Sonarr
* Radarr
* Bazarr
* Seerr
* FlareSolverr

Jellyfin runs separately on CT102 and uses the shared media storage.

---

## Monitoring

The homelab uses:

* **Beszel** for system and resource monitoring
* **Uptime Kuma** for service availability monitoring

Monitoring coverage is still being expanded as the infrastructure develops.

---

## Pterodactyl

Pterodactyl runs on VM108 using:

* Pterodactyl Panel
* Wings
* Docker
* MariaDB
* Redis

Game-server storage is provided through the dedicated NFS `games` share.

The Panel is accessed through:

```text
https://panel.robynshomelab.dev
```

---

## Documentation

Detailed documentation is organised numerically in [`docs/`](docs/):

| File                | Topic       |
| ------------------- | ----------- |
| `00-overview.md`    | Overview    |
| `01-hardware.md`    | Hardware    |
| `02-network.md`     | Network     |
| `03-proxmox.md`     | Proxmox     |
| `04-pihole.md`      | Pi-hole     |
| `05-unbound.md`     | Unbound     |
| `06-cloudflare.md`  | Cloudflare  |
| `07-nginx.md`       | Nginx       |
| `08-certbot.md`     | Certbot     |
| `09-netbird.md`     | NetBird     |
| `10-jellyfin.md`    | Jellyfin    |
| `11-beszel.md`      | Beszel      |
| `12-uptime-kuma.md` | Uptime Kuma |
| `13-media-stack.md` | Media stack |
| `14-pterodactyl.md` | Pterodactyl |
| `15-ddns.md`        | Dynamic DNS |

---

## Current Status

The core homelab infrastructure is operational.

Remaining work primarily consists of:

* Firewall hardening
* Monitoring expansion
* Backup improvements
* Additional service configuration
* Stability testing

Once the remaining work is complete and the environment has proven stable, the architecture diagram will be rebuilt to reflect the final topology.

---

## Security

No passwords, API keys, tokens, certificates, or other secrets should be committed to this repository.

This repository documents the infrastructure and configuration without exposing sensitive credentials.
