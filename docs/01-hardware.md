# Hardware

This document describes the physical hardware currently used by the homelab.

---

## Hardware Overview

The homelab currently consists of two physical Proxmox hosts.

| Host    | Model                  | CPU                |   RAM | Primary Role                       |
| ------- | ---------------------- | ------------------ | ----: | ---------------------------------- |
| `pve-1` | Dell OptiPlex 3060     | Intel CPU          |     — | Primary Proxmox host               |
| `pve-2` | Dell OptiPlex 9020 SFF | Intel Core i7-4770 | 16 GB | Secondary Proxmox host and storage |

Both systems are members of the `homelab` Proxmox cluster.

---

# pve-1

## System

```text
Hostname: pve-1
Model:    Dell OptiPlex 3060
IP:       192.168.20.100
Role:     Primary Proxmox host
```

pve-1 hosts the majority of the homelab's infrastructure services.

Current guests include:

| VMID | Guest         | Purpose                   |
| ---: | ------------- | ------------------------- |
|  100 | `pihole`      | Pi-hole, Unbound and DDNS |
|  101 | `netbird`     | NetBird routing peer      |
|  102 | `jellyfin`    | Jellyfin media server     |
|  103 | `mediastack`  | Media automation          |
|  104 | `beszel`      | Monitoring                |
|  105 | `uptime-kuma` | Service monitoring        |
|  106 | `nginx`       | Reverse proxy and TLS     |
|  107 | —             | Reserved for Homarr       |

---

# pve-2

## System

```text
Hostname: pve-2
Model:    Dell OptiPlex 9020 SFF
IP:       192.168.20.101
CPU:      Intel Core i7-4770
RAM:      16 GB
Role:     Secondary Proxmox host / storage server
```

pve-2 is the second member of the `homelab` Proxmox cluster.

It currently hosts VM108 for Pterodactyl and provides the homelab's bulk storage and NFS services.

---

## Internal Storage

The primary bulk-storage disk installed in pve-2 is:

```text
Model:       WDC WD40EZRZ-00GXCB
Manufacturer: Western Digital
Capacity:    4,000,787,030,016 bytes
Approximate: 4 TB raw
Rotation:    5400 RPM
Interface:   SATA
Logical sector: 512 bytes
Physical sector: 4096 bytes
Filesystem:  ext4
Label:       homelab-data
```

The disk is mounted at:

```text
/mnt/homelab-data
```

The disk is used for bulk homelab data rather than Proxmox VM storage.

---

## Drive Health

The WD Blue drive passed SMART health checks during installation.

At the time of inspection:

* No reallocated sectors were reported
* No pending sectors were reported
* No uncorrectable sectors were reported
* No reported SATA CRC errors were present
* Drive temperature was approximately 20 °C
* Approximately 9,000 power-on hours were reported

A full extended SMART test was not run during the initial inspection because the estimated completion time was several hours.

The drive should continue to be monitored through SMART and the homelab's monitoring infrastructure.

---

## Storage Layout

The bulk-storage filesystem is organised as:

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

### `media`

Stores the organised media library consumed by Jellyfin.

### `downloads`

Stores active and completed downloads used by the media automation stack.

### `games`

Provides storage for Pterodactyl game-server data.

### `backups`

Reserved for homelab backup data.

### `shared`

General-purpose shared storage.

---

# NFS Storage

pve-2 provides NFS exports for selected storage directories.

Current exports are intentionally separated by purpose.

```text
/mnt/homelab-data/media
/mnt/homelab-data/downloads
/mnt/homelab-data/games
```

The media and downloads shares are consumed by CT103 through pve-1.

The games share is consumed directly by VM108.

The desktop also mounts the media share directly from pve-2.

This arrangement avoids exporting the entire storage filesystem and allows different access policies to be applied to different datasets.

---

## Storage Permissions

The media and downloads shares use the dedicated:

```text
User: mediastack
UID:  999
GID:  990
```

The corresponding directories are owned by:

```text
999:990
```

and use group inheritance permissions appropriate for shared media-stack access.

NFS exports use `all_squash` with the `mediastack` UID/GID for the media and downloads shares.

The games export uses a separate configuration with `root_squash`.

---

# Pterodactyl VM

pve-2 hosts VM108:

```text
VMID:     108
Hostname: pterodactyl
IP:       192.168.20.111
OS:       Debian 13
```

VM108 has:

```text
vCPU:      6
RAM:       12 GB
Disk:      40 GB virtual disk
```

The VM runs:

* Pterodactyl Panel
* Wings
* Docker
* MariaDB
* Redis
* Nginx
* PHP-FPM

The VM also connects directly to the homelab's NFS games share.

---

# Networking Hardware

The current homelab network is based around the existing home router.

```text
LAN:     192.168.20.0/24
Gateway: 192.168.20.1
```

The homelab currently does not use a dedicated managed switch or VLAN infrastructure.

A managed switch is planned for future expansion.

Potential future improvements include:

* Managed switching
* VLAN segmentation
* Dedicated firewall/router
* Separate server, management, client and IoT networks

These changes have not yet been deployed.

---

# Desktop System

The primary desktop used to administer the homelab is:

```text
Hostname: RobynPC
OS:       Arch Linux
Interface: enp5s0
MAC:      d4:5d:64:d7:d7:59
IP:       192.168.20.102
```

The desktop receives its address through DHCP with a reservation for `192.168.20.102`.

It mounts the homelab media storage directly from pve-2 using NFS.

---

# Hardware Roles

The current physical architecture can be summarised as:

```text
                         ┌─────────────────────┐
                         │       Router        │
                         │    192.168.20.1     │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
              ┌──────▼──────┐               ┌──────▼──────┐
              │    pve-1    │               │    pve-2    │
              │ OptiPlex3060│               │ OptiPlex9020│
              │ .100        │               │ .101        │
              └──────┬──────┘               └──────┬──────┘
                     │                             │
              Proxmox guests                Proxmox + storage
                                                   │
                                             ┌─────▼─────┐
                                             │   4 TB    │
                                             │ WD Blue   │
                                             └───────────┘
```

---

# Hardware Expansion

Future hardware changes may include:

* Additional storage drives
* A dedicated NAS/storage system if required
* Managed network switching
* Additional RAM
* UPS protection
* Dedicated firewall/router hardware
* Additional compute nodes

Any future hardware should be documented here once it is actually deployed.

---

# Hardware Philosophy

The homelab prioritises:

1. Reusing existing hardware where practical
2. Low power consumption
3. Simple maintenance
4. Service isolation
5. Expandability
6. Reliable storage
7. Clear separation between compute and bulk storage

The two-node Proxmox architecture allows infrastructure services and workloads to be distributed between the two physical systems while keeping the environment relatively simple.
