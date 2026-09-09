# Robyn's Homelab

## Overview

This repository contains the documentation, configuration, diagrams, and supporting scripts for my personal homelab.

The purpose of this homelab is not only to provide useful services, but also to serve as a practical learning environment. The documentation therefore explains both **what has been configured** and **why it has been configured that way**.

The infrastructure is developed incrementally, with each major stage documented and version-controlled using Git.

---

## Current Architecture

The homelab currently consists of two physical Proxmox systems forming a two-node cluster:

| Host    | Hardware               | IP               | Role                                      |
| ------- | ---------------------- | ---------------- | ----------------------------------------- |
| `pve-1` | Dell OptiPlex 3060     | `192.168.20.100` | Primary Proxmox host                      |
| `pve-2` | Dell OptiPlex 9020 SFF | `192.168.20.101` | Secondary Proxmox host and storage server |

The Proxmox cluster is named:

```text
homelab
```

High Availability (HA) is currently disabled.

The network remains a relatively simple LAN:

```text
Network: 192.168.20.0/24
Gateway: 192.168.20.1
```

There is currently **no router port forwarding** for homelab services. Remote access is provided through NetBird.

Future network improvements may include managed switching, VLAN segmentation, and a dedicated firewall/router.

---

## Proxmox

The homelab currently uses two Proxmox hosts.

### pve-1

```text
Hostname: pve-1
IP:       192.168.20.100
```

Current guests:

| VMID | Hostname      | Purpose                         | IP              |
| ---: | ------------- | ------------------------------- | --------------- |
|  100 | `pihole`      | Pi-hole, Unbound and DDNS       | `192.168.20.99` |
|  101 | `netbird`     | NetBird routing peer            | `192.168.20.97` |
|  102 | `jellyfin`    | Jellyfin media server           | `192.168.20.98` |
|  103 | `mediastack`  | Media automation stack          | `192.168.20.93` |
|  104 | `beszel`      | System monitoring               | `192.168.20.96` |
|  105 | `uptime-kuma` | Service monitoring              | `192.168.20.95` |
|  106 | `nginx`       | Nginx reverse proxy and Certbot | `192.168.20.94` |
|  107 | —             | Reserved for Homarr             | —               |

### pve-2

```text
Hostname: pve-2
IP:       192.168.20.101
```

Current guest:

| VMID | Hostname      | Purpose                     | IP               |
| ---: | ------------- | --------------------------- | ---------------- |
|  108 | `pterodactyl` | Pterodactyl Panel and Wings | `192.168.20.111` |

pve-2 also provides the homelab's primary bulk storage and NFS services.

---

## Storage

The Dell OptiPlex 9020 contains the primary 4 TB homelab data drive:

```text
Model:       WDC WD40EZRZ-00GXCB
Capacity:    ~4 TB
Filesystem:  ext4
Label:       homelab-data
Mount:       /mnt/homelab-data
```

The storage is organised as:

```text
/mnt/homelab-data/
├── media/
│   ├── anime/
│   ├── books/
│   ├── movies/
│   ├── music/
│   └── tv/
├── downloads/
│   ├── incomplete/
│   └── complete/
├── games/
├── backups/
└── shared/
```

pve-2 exports selected directories over NFS.

The media and download shares are consumed by the media stack, while the games share is consumed by the Pterodactyl server.

The desktop also mounts the media storage directly over NFS.

---

## DNS Architecture

Pi-hole provides DNS for the homelab on port 53.

Unbound runs on the Pi-hole container and provides recursive DNS resolution and DNSSEC validation.

The basic DNS architecture is:

```text
Client
  │
  ▼
Pi-hole :53
  │
  ▼
Unbound :5335
  │
  ▼
DNS hierarchy
```

Pi-hole remains responsible for:

* DNS filtering
* local DNS records
* split-horizon DNS for homelab services

Unbound provides recursive external DNS resolution.

NetBird clients also use the Pi-hole DNS server at:

```text
192.168.20.99:53
```

---

## Internal DNS

The following service hostnames resolve internally through Pi-hole to the Nginx reverse proxy:

```text
panel.robynshomelab.dev
jellyfin.robynshomelab.dev
status.robynshomelab.dev
beszel.robynshomelab.dev
pihole.robynshomelab.dev
```

Internal resolution:

```text
Service hostname
      │
      ▼
Pi-hole
192.168.20.99
      │
      ▼
192.168.20.94
      │
      ▼
Nginx
```

The exception is the Wings hostname, which resolves to the Pterodactyl VM:

```text
wings.robynshomelab.dev
        │
        ▼
192.168.20.111
```

---

## Cloudflare and HTTPS

Cloudflare is authoritative for:

```text
robynshomelab.dev
```

Cloudflare is used for:

* authoritative DNS
* DDNS
* DNS-01 ACME validation
* Let's Encrypt certificate issuance

Cloudflare is **not** being used as a reverse proxy for homelab traffic.

The Cloudflare records are DNS-only.

The public `panel.robynshomelab.dev` record points to the home's WAN address for DNS and ACME purposes. This does **not** mean the Panel is directly reachable from the public Internet, as there is no router port forwarding.

---

## Reverse Proxy

Nginx and Certbot run on CT106:

```text
Hostname: nginx
IP:       192.168.20.94
```

Nginx terminates HTTPS and forwards requests to internal services.

Current reverse-proxy architecture:

```text
Client
  │
  │ HTTPS :443
  ▼
Nginx
192.168.20.94
  │
  ├── jellyfin.robynshomelab.dev
  │       └── 192.168.20.98:8096
  │
  ├── status.robynshomelab.dev
  │       └── 192.168.20.95:3001
  │
  ├── beszel.robynshomelab.dev
  │       └── 192.168.20.96:8090
  │
  ├── pihole.robynshomelab.dev
  │       └── 192.168.20.99:8080
  │
  └── panel.robynshomelab.dev
          └── 192.168.20.111:80
```

The Pterodactyl Panel is therefore accessed through:

```text
HTTPS :443
    │
    ▼
CT106 Nginx
    │
    ▼
HTTP :80
    │
    ▼
VM108 Pterodactyl Panel
```

Let's Encrypt certificates are obtained using Cloudflare DNS-01 validation.

Certificate renewal is automated through Certbot's systemd timer.

---

## Remote Access

NetBird provides private remote access to the homelab.

There are currently two independent NetBird peers involved in the infrastructure.

### CT101 — LAN Routing Peer

```text
CT101
192.168.20.97
NetBird IP: 100.113.51.59
```

CT101 provides access from NetBird clients into selected homelab LAN addresses.

Current advertised routes include:

```text
192.168.20.94/32
192.168.20.99/32
```

This provides NetBird clients with access to:

* Nginx
* Pi-hole/DNS

NetBird DNS is configured to use:

```text
192.168.20.99:53
```

### VM108 — Independent NetBird Peer

The Pterodactyl VM is also independently connected to NetBird:

```text
VM108
192.168.20.111
NetBird IP: 100.113.229.169
FQDN: pterodactyl.netbird.cloud
```

This peer is independent of CT101.

The distinction is intentional:

```text
NetBird client
    │
    ├── CT101
    │     └── LAN routing
    │
    └── VM108
          └── Direct Pterodactyl VM access
```

The NetBird game-server networking configuration remains an area of ongoing development.

---

## Media Architecture

The media stack is deployed on CT103:

```text
CT103
192.168.20.93
```

The stack uses Docker and consists of:

* qBittorrent
* Prowlarr
* FlareSolverr
* Sonarr
* Radarr
* Bazarr
* Seerr

The general workflow is:

```text
Seerr
  │
  ├── Sonarr
  │
  └── Radarr
        │
        ▼
     Prowlarr
        │
        ▼
    qBittorrent
        │
        ▼
      NFS
        │
        ├── downloads
        │
        ▼
     Sonarr/Radarr
        │
        ▼
      media
        │
        ▼
     Jellyfin
```

The media data is stored on pve-2 and accessed by CT103 through NFS.

Jellyfin runs separately on CT102 because the Dell OptiPlex 3060 provides access to Intel integrated graphics for hardware-accelerated transcoding.

---

## Jellyfin

Jellyfin runs on:

```text
CT102
192.168.20.98
```

Jellyfin uses the NFS-backed media storage provided by pve-2.

The current media architecture is:

```text
pve-2 storage
      │
      │ NFS
      ▼
CT103 media stack
      │
      │ media files
      ▼
Jellyfin CT102
192.168.20.98
```

Moonbase is installed in Jellyfin and provides the integration layer used by the current Jellyfin environment.

Moonfin is also configured on the Android TV client.

Seerr is integrated with Jellyfin and provides media request functionality.

---

## Pterodactyl

Pterodactyl is deployed on VM108:

```text
VMID:     108
Hostname: pterodactyl
IP:       192.168.20.111
OS:       Debian 13
```

The VM hosts:

* Pterodactyl Panel
* Wings
* Docker
* MariaDB
* Redis
* Nginx
* PHP-FPM

The Panel is available internally through:

```text
https://panel.robynshomelab.dev
```

The current access path is:

```text
Client
  │
  ▼
Nginx CT106
192.168.20.94
  │
  ▼
Pterodactyl VM108
192.168.20.111
```

Wings is installed and running as a systemd service.

The Wings daemon provides the Docker-based game-server environment.

Game-server networking and public/NetBird access are still being developed.

---

## Monitoring

Two monitoring systems are currently deployed.

### Beszel

Beszel provides system-level monitoring and resource utilisation information.

It runs on:

```text
CT104
192.168.20.96
```

Future monitoring expansion includes additional coverage of:

* VM108
* Wings
* game servers
* storage
* Docker
* network infrastructure

### Uptime Kuma

Uptime Kuma provides service availability monitoring.

It runs on:

```text
CT105
192.168.20.95
```

It is intended for monitoring service availability and network-reachable endpoints.

---

## Current Service Inventory

| Service              | Host     | IP               | Status   |
| -------------------- | -------- | ---------------- | -------- |
| Pi-hole              | CT100    | `192.168.20.99`  | Deployed |
| Unbound              | CT100    | `192.168.20.99`  | Deployed |
| ddclient             | CT100    | `192.168.20.99`  | Deployed |
| NetBird routing peer | CT101    | `192.168.20.97`  | Deployed |
| Jellyfin             | CT102    | `192.168.20.98`  | Deployed |
| Media stack          | CT103    | `192.168.20.93`  | Deployed |
| Beszel               | CT104    | `192.168.20.96`  | Deployed |
| Uptime Kuma          | CT105    | `192.168.20.95`  | Deployed |
| Nginx                | CT106    | `192.168.20.94`  | Deployed |
| Certbot              | CT106    | `192.168.20.94`  | Deployed |
| Homarr               | VMID 107 | —                | Reserved |
| Pterodactyl Panel    | VM108    | `192.168.20.111` | Deployed |
| Wings                | VM108    | `192.168.20.111` | Deployed |

---

## Planned Infrastructure

The following components are still planned or under development:

1. Finalise Pterodactyl game-server networking
2. Harden VM108 firewall using nftables
3. Expand monitoring to VM108, Wings, storage and game servers
4. Deploy Homarr
5. Further develop network segmentation
6. Introduce managed switching
7. Consider VLAN segmentation
8. Consider a dedicated firewall/router such as pfSense

The architecture will continue to evolve as these components are introduced.

---

## Documentation Philosophy

Each major component should document:

* What the technology does
* Why it is being used
* How it fits into the homelab
* How it was configured
* Important configuration files
* How the configuration was tested
* Problems encountered during setup
* How those problems were resolved
* Security considerations
* Future improvements

Configuration files containing credentials, private keys, API tokens, or other secrets must never be committed to the repository.

The Git repository is therefore intended to provide a **reproducible technical record of the homelab without exposing secrets**.

---

## Versioning

Major architectural changes will be represented by Git commits and, where appropriate, Git tags.

Network diagrams will also be versioned as the infrastructure evolves.

The current architecture represents the transition from the original single-host deployment to a two-node Proxmox cluster with dedicated storage, media automation, reverse-proxy infrastructure, and Pterodactyl.

Example progression:

```text
v1 — Single Proxmox host
v2 — Two-node Proxmox cluster
v3 — Dedicated storage and NFS
v4 — Media automation stack
v5 — Pterodactyl deployment
v6 — Future network segmentation
```

The exact versioning scheme may evolve as the homelab grows.
