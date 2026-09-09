# Hardware

## Overview

The homelab currently consists of two physical Dell OptiPlex systems running Proxmox VE as members of the same cluster.

The systems have different roles:

- `pve-1` provides the primary core-infrastructure host.
- `pve-2` provides additional compute capacity and will provide bulk HDD storage.

Neither system is intended to be a traditional dedicated NAS. Storage will be provided directly from `pve-2` using a host filesystem and NFS.

## Physical Hosts

| Host | Model | Role | IP |
|---|---|---|---|
| `pve-1` | Dell OptiPlex 3060 | Proxmox / core services | `192.168.20.100` |
| `pve-2` | Dell OptiPlex 9020 SFF | Proxmox / Pterodactyl / storage | `192.168.20.101` |

Both hosts are members of the `homelab` Proxmox cluster.

## pve-1

### System

- Model: Dell OptiPlex 3060
- Hostname: `pve-1`
- IP address: `192.168.20.100`
- Hypervisor: Proxmox VE

`pve-1` currently hosts the majority of the core infrastructure containers.

### Current Workloads

- CT100 — Pi-hole / Unbound / DDNS
- CT101 — NetBird routing peer
- CT102 — Jellyfin
- CT104 — Beszel
- CT105 — Uptime Kuma
- CT106 — Nginx / Certbot

Reserved:

- VM103 — future media stack
- VM107 — future Homarr

## pve-2

### System

- Model: Dell OptiPlex 9020 SFF
- Hostname: `pve-2`
- IP address: `192.168.20.101`
- CPU: Intel Core i7-4770
- CPU configuration: 4 physical cores / 8 logical threads
- RAM: 16 GB
- Hypervisor: Proxmox VE
- Proxmox VE version: 9.2.2
- Kernel: `7.0.2-6-pve`

### Current Workloads

VM108 is currently hosted on `pve-2`:

- Pterodactyl Panel
- IP: `192.168.20.111`
- 6 vCPU
- 12 GB RAM
- 40 GB virtual disk

The remaining host resources are available for future workloads and storage services.

## pve-2 Storage

The current Proxmox installation uses the internal SSD for the operating system and virtual machine storage.

The system contains:

- Samsung MZ7PC128HA SSD
- Approximately 119 GB raw capacity

VM108 currently uses a virtual disk on Proxmox `local-lvm`.

### Future HDD Storage

A WD Blue 4 TB HDD is intended to be installed in `pve-2`.

Drive:

- Model: WD40EZRZ
- Capacity: 4 TB
- Type: WD Blue consumer desktop HDD
- Current status: Not yet installed

The intended purpose of this drive is bulk file storage rather than Proxmox VM storage.

Planned architecture:

    pve-2
      |
      +--> Internal SSD
      |     |
      |     +--> Proxmox
      |     +--> VM108
      |
      +--> 4 TB HDD
            |
            +--> Host filesystem
            |
            +--> NFS/fileshare
            |
            +--> Future media storage

The HDD will not be used as the primary storage location for the Pterodactyl VM.

## HDD Power Considerations

The OptiPlex 9020 SFF uses Dell-specific internal power cabling.

The system currently has:

- One standard SATA power connection
- One additional Dell proprietary/slim connector associated with the optical-drive configuration

Because the proprietary connector has not been fully established as a suitable HDD power source, additional SATA power hardware is planned rather than assuming that connector can safely power another standard HDD.

The exact power arrangement should be verified before the 4 TB HDD is installed.

## Bundled 1 TB HDD

The OptiPlex 9020 also came with a 1 TB HDD.

Its eventual role has not yet been finalised.

It should not be considered part of the storage architecture until its condition, model, and intended purpose are confirmed.

## Storage Design

The homelab does not use TrueNAS or OpenMediaVault.

The current design is intentionally simpler:

- Proxmox remains the host operating system.
- The 4 TB HDD will be mounted directly on `pve-2`.
- The filesystem will be managed by the Proxmox host.
- NFS will provide network access to other systems.
- Future media services will consume storage over the network.

This keeps storage management separate from the virtual machine storage used by Proxmox.

## Hardware Expansion

Potential future hardware improvements include:

- Managed network switch
- Additional HDD storage
- Improved HDD power/connectivity
- Larger or additional storage drives
- Dedicated firewall/router hardware
- VLAN-capable network infrastructure

These are future improvements rather than requirements for the current deployment.

## Hardware Design Principles

The homelab hardware is being used to prioritise:

1. Reuse of existing hardware.
2. Low power consumption where practical.
3. Separation of infrastructure workloads.
4. Simple and recoverable storage architecture.
5. Incremental expansion rather than purchasing a dedicated NAS immediately.

The 9020's additional compute resources are currently being used for Pterodactyl and will later provide bulk storage.