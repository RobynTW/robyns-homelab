# Robyn's Homelab

Documentation and configuration notes for my personal homelab.

The homelab is built around a two-node Proxmox cluster and currently hosts networking, storage, media, monitoring, a central Homepage dashboard, and game-server infrastructure.

> **Documentation state:** Updated 2026-09-22. Individual documentation files describe the current deployed configuration. The architecture diagram is intentionally not yet treated as final and will be rebuilt after the infrastructure has remained stable for several months.

---

## Hardware

| Host | Hardware | IP |
| --- | --- | --- |
| pve-1 | Dell OptiPlex 3060 | `192.168.20.100` |
| pve-2 | Dell OptiPlex 9020 SFF | `192.168.20.101` |

pve-2 provides the primary 4TB HDD storage.

---

## Network

```text
LAN:       192.168.20.0/24
Router:    192.168.20.1
```

Pi-hole provides internal DNS and Unbound provides recursive DNS resolution.

NetBird provides private remote access without router port forwarding.

Cloudflare provides authoritative DNS and DNS-01 ACME validation.

Nginx on CT106 provides the central reverse proxy and TLS layer.

---

## Services

| ID | Hostname | IP | Service |
| --- | --- | --- | --- |
| CT100 | `pihole` | `192.168.20.99` | Pi-hole / Unbound / DDNS |
| CT101 | `netbird` | `192.168.20.97` | NetBird routing |
| CT102 | `jellyfin` | `192.168.20.98` | Jellyfin |
| CT103 | `mediastack` | `192.168.20.93` | Media stack |
| CT104 | `beszel` | `192.168.20.96` | Beszel |
| CT105 | `uptime-kuma` | `192.168.20.95` | Uptime Kuma |
| CT106 | `nginx` | `192.168.20.94` | Nginx / Certbot |
| CT107 | `homepage` | `192.168.20.92` | Homepage dashboard |
| VM108 | `pterodactyl` | `192.168.20.111` | Pterodactyl Panel / Wings |

CT107 is the former dashboard reservation and is now deployed as Homepage. It is an LXC, not a VM.

---

## Storage

The primary storage is a 4TB WD Blue HDD in pve-2:

```text
/mnt/homelab-data/
├── media/
├── downloads/
├── games/
├── backups/
└── shared/
```

Selected storage is exported over NFS. Pterodactyl game-server workloads remain logically separate from general NAS/media storage.

---

## Media

CT103 runs:

- qBittorrent
- Gluetun
- Prowlarr
- Sonarr
- Radarr
- Bazarr+
- Seerr
- FlareSolverr

qBittorrent uses Gluetun as its Docker network namespace. Bazarr+ retains the existing configuration and provides additional Provider Hub integrations.

Jellyfin runs separately on CT102.

---

## Monitoring

The homelab uses:

- **Beszel** for system/resource monitoring
- **Uptime Kuma** for service availability

Beszel currently represents the major homelab hosts and services.

Uptime Kuma has the curated status page:

```text
https://status.robynshomelab.dev/status/homelab
```

Homepage integrates both monitoring systems.

---

## Homepage

Homepage runs on CT107 at `192.168.20.92` using Docker and version 2.4.0.

The dashboard includes:

- Infrastructure
- Network
- Media
- Gaming
- Monitoring
- Live Proxmox resource widgets
- Beszel and Uptime Kuma integration
- Direct GitHub repository widget
- Custom background
- Glass-style service cards
- Responsive custom layout

The GitHub widget links directly to `https://github.com/RobynTW/robyns-homelab`.

See [`docs/17-homepage.md`](docs/17-homepage.md).

---

## Pterodactyl

Pterodactyl runs on VM108 with Panel, Wings 1.13.3, Docker, MariaDB, Redis, and an independent NetBird peer.

Panel:

```text
https://panel.robynshomelab.dev
```

Minecraft uses the permanent NetBird Reverse Proxy:

```text
minecraft.robynshomelab.dev:17161
```

No router port forwarding is used.

---

## Current Software Versions

These are point-in-time versions observed in the deployed environment:

| Component | Version |
| --- | --- |
| Proxmox VE | 9.2.2 |
| Homepage | 2.4.0 |
| NetBird | 0.78.1 |
| Pterodactyl Wings | 1.13.3 |
| Docker Engine on VM108 | 29.8.0 |
| qBittorrent | 5.2.3 |
| Bazarr+ | 2.6.2 |
| Jellyfin | 10.11.11 |

These are not claims about the latest upstream releases.

---

## Disaster Recovery / Rebuild

A rebuild-oriented configuration snapshot is maintained in [`config/`](config/). It contains the known-good system and service configuration needed to help recreate the current homelab without committing live secrets.

In the event of a catastrophic failure, use the configuration snapshot together with the dated [AI handover](docs/ai-handover-2026-09-22.md). The handover records the current topology, important implementation details, what is intentionally excluded from Git, and a step-by-step approach for using the configuration copies during a rebuild.

**Important:** this repository is not a complete backup of the homelab. Secrets, application databases, runtime state, media, game data, and other critical data require separate backups and secure storage.

## Documentation

| File | Topic |
| --- | --- |
| `00-overview.md` | Overview |
| `01-hardware.md` | Hardware |
| `02-network.md` | Network |
| `03-proxmox.md` | Proxmox |
| `04-pihole.md` | Pi-hole |
| `05-unbound.md` | Unbound |
| `06-cloudflare.md` | Cloudflare |
| `07-nginx.md` | Nginx |
| `08-certbot.md` | Certbot |
| `09-netbird.md` | NetBird |
| `10-jellyfin.md` | Jellyfin |
| `11-beszel.md` | Beszel |
| `12-uptime-kuma.md` | Uptime Kuma |
| `13-media-stack.md` | Media stack |
| `14-pterodactyl.md` | Pterodactyl |
| `15-ddns.md` | Dynamic DNS |
| `16-gluetun-bazarr-plus.md` | Gluetun / Bazarr+ |
| `17-homepage.md` | Homepage dashboard |

AI continuity:

- [`.ai-homelab-context.md`](.ai-homelab-context.md)
- [`docs/ai-handover-2026-09-21.md`](docs/ai-handover-2026-09-21.md)
- [`docs/ai-handover-2026-09-22.md`](docs/ai-handover-2026-09-22.md)

---

## Current Status

Core infrastructure is operational.

Recently completed:

- Two-node Proxmox cluster
- pve-2 4TB storage and NFS
- Media stack and Bazarr+ migration
- Pterodactyl Panel and Wings
- Permanent NetBird Minecraft networking
- Beszel monitoring expansion
- Uptime Kuma status page
- Homepage dashboard deployment and configuration pass

Remaining work:

- Firewall hardening
- Further monitoring expansion
- Backup improvements
- Remaining service configuration/cleanup
- Extended stability testing

The architecture diagram will be rebuilt after the environment has demonstrated long-term stability.

---

## Security

No passwords, API keys, tokens, certificates, private keys, or other secrets should be committed to this repository.
