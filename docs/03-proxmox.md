# Proxmox

This document describes the Proxmox VE infrastructure used by the homelab, including the physical nodes, cluster configuration, virtual machines, containers, and storage responsibilities.

---

## Proxmox Overview

The homelab currently operates as a two-node Proxmox cluster named:

```text
homelab
```

The cluster consists of:

| Node    | Hardware               | IP               | Role                             |
| ------- | ---------------------- | ---------------- | -------------------------------- |
| `pve-1` | Dell OptiPlex 3060     | `192.168.20.100` | Primary Proxmox node             |
| `pve-2` | Dell OptiPlex 9020 SFF | `192.168.20.101` | Secondary Proxmox node / storage |

The cluster is currently configured with:

```text
Nodes:       2
HA:          Disabled
Network:     192.168.20.0/24
Gateway:     192.168.20.1
```

High Availability is intentionally disabled. The two-node cluster is primarily used for centralised Proxmox management and distributing workloads between the two physical systems.

---

# pve-1

```text
Hostname: pve-1
IP:       192.168.20.100
Hardware: Dell OptiPlex 3060
```

pve-1 hosts the majority of the homelab's infrastructure services.

Current guests:

| VMID | Type | Hostname      | Purpose                | IP              |
| ---: | ---- | ------------- | ---------------------- | --------------- |
|  100 | LXC  | `pihole`      | Pi-hole, Unbound, DDNS | `192.168.20.99` |
|  101 | LXC  | `netbird`     | NetBird routing peer   | `192.168.20.97` |
|  102 | LXC  | `jellyfin`    | Jellyfin media server  | `192.168.20.98` |
|  103 | LXC  | `mediastack`  | Media automation stack | `192.168.20.93` |
|  104 | LXC  | `beszel`      | System monitoring      | `192.168.20.96` |
|  105 | LXC  | `uptime-kuma` | Service monitoring     | `192.168.20.95` |
|  106 | LXC  | `nginx`       | Reverse proxy and TLS  | `192.168.20.94` |
|  107 | —    | —             | Reserved for Homarr    | —               |

---

# pve-2

```text
Hostname: pve-2
IP:       192.168.20.101
Hardware: Dell OptiPlex 9020 SFF
CPU:      Intel Core i7-4770
RAM:      16 GB
```

pve-2 provides:

* Proxmox compute
* Pterodactyl compute
* Bulk storage
* NFS storage services

Current guest:

| VMID | Type | Hostname      | Purpose                     | IP               |
| ---: | ---- | ------------- | --------------------------- | ---------------- |
|  108 | VM   | `pterodactyl` | Pterodactyl Panel and Wings | `192.168.20.111` |

---

# Cluster Architecture

The current cluster can be represented as:

```text
                       Proxmox Cluster
                           "homelab"
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
          ┌──────▼──────┐             ┌──────▼──────┐
          │    pve-1    │             │    pve-2    │
          │ 192.168.20.100           │ 192.168.20.101
          │ OptiPlex 3060             │ OptiPlex 9020
          └──────┬──────┘             └──────┬──────┘
                 │                           │
        ┌────────┼────────┐                  │
        │        │        │                  │
       CT100    CT102    CT103             VM108
       CT101    CT104    CT105          Pterodactyl
       CT106
```

The cluster is connected using the normal homelab LAN.

There is currently no dedicated cluster or migration network.

---

# Container and VM Roles

## CT100 — Pi-hole

```text
VMID: 100
Hostname: pihole
IP: 192.168.20.99
```

Services:

* Pi-hole
* Unbound
* ddclient

Primary role:

* DNS filtering
* Internal DNS
* Recursive DNS integration
* Dynamic DNS updates

---

## CT101 — NetBird

```text
VMID: 101
Hostname: netbird
IP: 192.168.20.97
```

Primary role:

* NetBird routing peer

NetBird IP:

```text
100.113.51.59
```

Current LAN routes:

```text
192.168.20.94/32
192.168.20.99/32
```

CT101 allows NetBird clients to reach selected LAN infrastructure.

---

## CT102 — Jellyfin

```text
VMID: 102
Hostname: jellyfin
IP: 192.168.20.98
```

Primary role:

* Jellyfin media server

The container accesses media stored on pve-2 through the NFS-backed storage architecture.

Jellyfin also provides access to the current Moonbase/Moonfin setup.

---

## CT103 — Media Stack

```text
VMID: 103
Hostname: mediastack
IP: 192.168.20.93
```

Primary role:

* Media automation

Docker is installed inside the unprivileged LXC with nesting enabled.

The container runs:

* qBittorrent
* Prowlarr
* FlareSolverr
* Sonarr
* Radarr
* Bazarr
* Seerr

CT103 accesses the media and downloads NFS shares provided by pve-2.

---

## CT104 — Beszel

```text
VMID: 104
Hostname: beszel
IP: 192.168.20.96
```

Primary role:

* System monitoring

Beszel provides resource and system monitoring for the homelab.

Additional monitoring of VM108, Wings, game servers, storage and Docker is planned.

---

## CT105 — Uptime Kuma

```text
VMID: 105
Hostname: uptime-kuma
IP: 192.168.20.95
```

Primary role:

* Service availability monitoring

Uptime Kuma monitors the availability of homelab services and endpoints.

---

## CT106 — Nginx

```text
VMID: 106
Hostname: nginx
IP: 192.168.20.94
```

Primary role:

* Reverse proxy
* HTTPS termination
* Certbot integration

CT106 replaced the previous reverse-proxy role that was historically hosted on CT100.

Current reverse-proxy targets include:

```text
jellyfin.robynshomelab.dev
    → 192.168.20.98:8096

status.robynshomelab.dev
    → 192.168.20.95:3001

beszel.robynshomelab.dev
    → 192.168.20.96:8090

pihole.robynshomelab.dev
    → 192.168.20.99:8080

panel.robynshomelab.dev
    → 192.168.20.111:80
```

---

# VM108 — Pterodactyl

```text
VMID:      108
Hostname:  pterodactyl
IP:        192.168.20.111
OS:        Debian 13
vCPU:      6
RAM:       12 GB
Disk:      40 GB
```

VM108 hosts the Pterodactyl Panel and Wings.

Installed components include:

* Pterodactyl Panel
* Wings
* Docker
* MariaDB
* Redis
* Nginx
* PHP-FPM
* Composer

The VM also has an independent NetBird peer.

NetBird IP:

```text
100.113.229.169
```

FQDN:

```text
pterodactyl.netbird.cloud
```

---

# Storage on pve-2

pve-2 contains the primary 4 TB bulk-storage disk.

```text
Disk:
WDC WD40EZRZ-00GXCB

Mount:
 /mnt/homelab-data
```

The storage is separate from the Proxmox VM disk used by VM108.

The primary storage directories are:

```text
/mnt/homelab-data/media
/mnt/homelab-data/downloads
/mnt/homelab-data/games
/mnt/homelab-data/backups
/mnt/homelab-data/shared
```

pve-2 provides NFS exports for selected directories.

---

# NFS Architecture

The current storage architecture is:

```text
                    pve-2
              192.168.20.101
                     │
              /mnt/homelab-data
                     │
          ┌──────────┼──────────┐
          │          │          │
        media    downloads    games
          │          │          │
          ▼          ▼          ▼
       CT103       CT103      VM108
     Media Stack  Downloads  Pterodactyl
```

The media and downloads shares are also made available to the relevant services through pve-1.

This separates bulk storage from application compute.

---

# Proxmox Storage Considerations

The 4 TB drive on pve-2 is used as bulk data storage rather than the primary Proxmox VM datastore.

This is intentional.

Application workloads remain on their respective Proxmox storage while large media, downloads and game data are stored on the dedicated bulk-storage filesystem.

This reduces unnecessary coupling between VM/container disks and large application datasets.

---

# Networking

The Proxmox nodes currently use the main LAN:

```text
192.168.20.0/24
```

Gateway:

```text
192.168.20.1
```

There are currently no dedicated VLANs for:

* Proxmox management
* Cluster traffic
* Storage
* Migration
* Services

A managed switch and VLAN segmentation are planned for future expansion.

---

# High Availability

Proxmox HA is currently disabled.

This is intentional because the cluster contains only two physical nodes.

The cluster is currently intended to provide:

* Centralised management
* Workload distribution
* Easier maintenance
* Future expansion capability

It should not be considered a fully redundant HA platform.

A two-node cluster does not provide the same fault tolerance as a larger cluster with appropriate quorum and storage infrastructure.

---

# Backups

The `backups` directory exists on the pve-2 bulk-storage filesystem.

A comprehensive backup strategy for the complete homelab remains a future task.

Important configuration should be backed up independently of the live VM/container filesystems.

Future backup planning should cover:

* Proxmox guest configuration
* Application configuration
* Pterodactyl configuration
* Media metadata
* Databases
* Nginx configuration
* DNS configuration
* Monitoring configuration
* Critical host configuration

Secrets and credentials must not be committed to the Git repository.

---

# Future Proxmox Improvements

Planned improvements include:

1. Deploy Homarr on VMID 107
2. Expand monitoring coverage
3. Implement a formal backup strategy
4. Consider dedicated Proxmox storage
5. Introduce VLAN segmentation
6. Introduce a dedicated management network
7. Consider a dedicated storage network
8. Evaluate future Proxmox node expansion

These features should be documented as deployed only after they have been implemented and tested.

---

# Operational Principles

The Proxmox environment follows these principles:

* Keep infrastructure services isolated into dedicated guests
* Keep bulk storage separate from compute workloads
* Avoid exposing management interfaces directly to the Internet
* Use NetBird for private remote administration
* Keep service-specific configuration within the appropriate guest
* Document deployed state rather than planned architecture
* Keep secrets outside the Git repository
* Make major architectural changes through version-controlled commits

The Proxmox cluster is intended to remain simple, maintainable and expandable as the homelab grows.
