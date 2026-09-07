# Hardware

## Overview

This document records the physical hardware used by the homelab, its current roles, and planned hardware additions.

The homelab currently consists primarily of a Dell OptiPlex 3060 running Proxmox. A Dell OptiPlex 9020 SFF is planned as the dedicated storage/NAS and Pterodactyl host.

The hardware is intentionally divided by role so that services can be isolated and the infrastructure can be expanded over time.

---

## Current Hardware

### Dell OptiPlex 3060

| Component       | Specification                       |
| --------------- | ----------------------------------- |
| Model           | Dell OptiPlex 3060                  |
| Role            | Proxmox host                        |
| IP address      | `192.168.20.100`                    |
| Hostname        | `pve-1`                             |
| Virtualisation  | Proxmox VE                          |
| Primary purpose | Homelab services and infrastructure |

The 3060 currently hosts the main infrastructure containers:

* CT 100 — Pi-hole, Nginx, Unbound and ddclient
* CT 101 — NetBird
* CT 102 — Jellyfin
* CT 104 — Beszel
* CT 105 — Uptime Kuma

The 3060 is currently connected directly to the ISP router. A network switch is planned for a future expansion.

### Current Container Allocation

| VMID | Hostname       | Role                            | IP address      |
| ---: | -------------- | ------------------------------- | --------------- |
|  100 | `pihole-nginx` | Pi-hole, Unbound, Nginx, DDNS   | `192.168.20.99` |
|  101 | `netbird`      | Private remote access           | `192.168.20.97` |
|  102 | `jellyfin`     | Media server                    | `192.168.20.98` |
|  104 | `beszel`       | Infrastructure monitoring       | `192.168.20.96` |
|  105 | `uptime-kuma`  | Service availability monitoring | `192.168.20.95` |

---

## Planned Hardware

### Dell OptiPlex 9020 SFF

The Dell OptiPlex 9020 SFF is planned as the dedicated storage and game-server host.

Planned responsibilities include:

* NAS storage
* NFS storage for the 3060
* Pterodactyl
* Game servers

The 9020 is intentionally not planned to host the main media services. Jellyfin and the future media automation stack will remain on the 3060, while bulk media storage will reside on the 9020.

### Storage

A 4 TB Western Digital Blue HDD is planned for the NAS:

```text
Model: WD40EZRZ
Capacity: 4 TB
```

The drive is intended primarily for media storage and NFS access.

The WD40EZRZ is a conventional desktop HDD rather than a purpose-built NAS drive. It can be used for the planned homelab storage system, but its suitability for long-term 24/7 operation should be monitored rather than assuming it has the same workload characteristics as a NAS-rated drive.

### 9020 Power Considerations

The 9020 SFF uses a Dell 255 W power supply.

The existing system has:

* one standard SATA power connection
* one additional Dell proprietary/slim power connection associated with the optical-drive configuration

A Dell SATA power splitter is planned to allow the standard SATA power connection to supply additional standard SATA drives.

The exact current capacity of the proprietary Dell power connection has not been established and should not be assumed without appropriate documentation or measurement.

---

## Hardware Roles

The intended hardware separation is:

```text
Dell OptiPlex 3060
└── Proxmox
    ├── Infrastructure
    │   ├── Pi-hole
    │   ├── Unbound
    │   ├── Nginx
    │   └── NetBird
    │
    ├── Media
    │   └── Jellyfin
    │
    └── Monitoring
        ├── Beszel
        └── Uptime Kuma


Dell OptiPlex 9020
└── Proxmox
    ├── NAS / NFS
    └── Pterodactyl
        └── Game servers
```

This separation keeps storage and game-server workloads independent from the primary infrastructure and media services.

---

## Planned Hardware Expansion

The following hardware changes are planned but are not yet part of the current network:

1. Dell OptiPlex 9020
2. NAS storage
3. Additional HDDs as required
4. Network switch
5. Dedicated pfSense router
6. Managed switch for VLAN support

The network switch and pfSense infrastructure will eventually allow the network to be segmented into VLANs.

---

## Hardware Documentation Philosophy

Hardware specifications are documented only when they have been confirmed.

Where a specification has not been verified, it is deliberately described as unknown or planned rather than estimated.

This is particularly important for:

* Dell proprietary power connectors
* maximum supported drive configurations
* power-delivery limits
* future hardware compatibility

---

## Key Commands

The following commands have been useful when identifying and managing the homelab hardware and Proxmox host.

### `hostnamectl`

```bash
hostnamectl
```

Displays information about the system hostname and operating system.

The hostname was changed from `pve` to:

```text
pve-1
```

The hostname was changed with:

```bash
hostnamectl set-hostname pve-1
```

### `ip addr`

```bash
ip addr
```

Displays the system's network interfaces and assigned IP addresses.

This is useful for identifying the current network configuration of a Proxmox host.

### `lsblk`

```bash
lsblk
```

Lists block devices such as HDDs, SSDs and their partitions.

This is useful when identifying storage devices before configuring them for NAS or virtualisation workloads.

### `lscpu`

```bash
lscpu
```

Displays information about the system CPU, including architecture, cores and threads.

### `free`

```bash
free -h
```

Displays system memory usage in human-readable units.

### `lsusb`

```bash
lsusb
```

Lists USB devices connected to the system.

### `lspci`

```bash
lspci
```

Lists PCI and PCIe devices, which is useful when identifying network adapters, graphics devices and other expansion hardware.

### Proxmox `pct`

```bash
pct list
```

Lists the LXC containers running on a Proxmox host.

For example:

```text
VMID  Status   Name
100   running  pihole-nginx
101   running  netbird
102   running  jellyfin
104   running  beszel
105   running  uptime-kuma
```

Individual containers can be managed with commands such as:

```bash
pct start <VMID>
pct stop <VMID>
pct status <VMID>
```

### Proxmox `qm`

```bash
qm list
```

Lists virtual machines managed by Proxmox.

This will become particularly relevant when the Pterodactyl VM is created on the 9020.

---

## Future Updates

This document should be updated when:

* the Dell 9020 is installed
* NAS storage is configured
* additional drives are installed
* the network switch is purchased
* the pfSense router is introduced
* hardware is replaced or upgraded
* hardware specifications are confirmed or corrected

Changes should be committed to Git so that the hardware history of the homelab remains traceable.
