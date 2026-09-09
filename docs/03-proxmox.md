# Proxmox

## Overview

The homelab runs Proxmox VE across two physical Dell systems.

Both systems are members of the same Proxmox cluster:

    Cluster: homelab

The cluster contains:

- `pve-1`
- `pve-2`

High availability is deliberately disabled.

The cluster currently requires both nodes for quorum.

## Proxmox Hosts

| Node | Hardware | IP | Role |
|---|---|---|---|
| `pve-1` | Dell OptiPlex 3060 | `192.168.20.100` | Core infrastructure |
| `pve-2` | Dell OptiPlex 9020 SFF | `192.168.20.101` | Pterodactyl / storage |

Both hosts use the following local hostname configuration:

    192.168.20.100 pve-1.home pve-1
    192.168.20.101 pve-2.home pve-2

## Cluster

Cluster name:

    homelab

The cluster currently consists of two nodes.

| Node | Status |
|---|---|
| `pve-1` | Online |
| `pve-2` | Online |

HA is not enabled.

This is intentional because the current hardware and service design does not require automatic VM failover.

Because this is a two-node cluster, quorum currently requires both nodes to be available.

## pve-1

Hostname:

    pve-1

IP:

    192.168.20.100

Hardware:

    Dell OptiPlex 3060

Current workloads:

| ID | Type | Hostname | IP | Service |
|---|---|---|---|---|
| CT100 | LXC | `pihole` | `192.168.20.99` | Pi-hole / Unbound / DDNS |
| CT101 | LXC | `netbird` | `192.168.20.97` | NetBird routing peer |
| CT102 | LXC | `jellyfin` | `192.168.20.98` | Jellyfin |
| CT104 | LXC | `beszel` | `192.168.20.96` | Beszel |
| CT105 | LXC | `uptime-kuma` | `192.168.20.95` | Uptime Kuma |
| CT106 | LXC | `nginx` | `192.168.20.94` | Nginx / Certbot |

Reserved VMIDs:

- VM103 — future media stack
- VM107 — future Homarr

## pve-2

Hostname:

    pve-2

IP:

    192.168.20.101

Hardware:

    Dell OptiPlex 9020 SFF
    Intel Core i7-4770
    4 physical cores
    8 logical threads
    16 GB RAM

Proxmox VE:

    9.2.2

Kernel:

    7.0.2-6-pve

Current workload:

| ID | Type | Hostname | IP | Service |
|---|---|---|---|---|
| VM108 | VM | `pterodactyl` | `192.168.20.111` | Pterodactyl Panel |

## VM108 — Pterodactyl

VMID:

    108

Hostname:

    pterodactyl

Host:

    pve-2

IP:

    192.168.20.111

Operating system:

    Debian 13 Trixie

Kernel:

    6.12.107+deb13-amd64

Virtualisation:

    KVM

### VM Resources

    vCPU: 6
    Sockets: 1
    Cores: 6
    CPU type: host
    RAM: 12 GB
    Disk: 40 GB
    Storage: local-lvm

### VM Configuration

- Q35 machine type
- OVMF / UEFI
- VirtIO network adapter
- VirtIO SCSI single
- QEMU Guest Agent enabled
- NUMA disabled
- Memory ballooning disabled
- Nested virtualisation disabled
- Proxmox VM firewall currently disabled
- Disk cache: none
- Discard enabled
- IO thread enabled
- SSD emulation enabled
- Backup enabled

The VM is headless and administered through SSH.

SSH access:

    ssh robyn@192.168.20.111

## VM108 Software

The Pterodactyl VM currently contains the software required for the Panel.

Installed components include:

- Docker Engine Community
- containerd
- runc
- PHP 8.3
- PHP-FPM
- MariaDB 11.8
- Redis
- Composer
- Nginx
- Git
- Curl
- CA certificates
- Required PHP extensions and supporting packages

PHP packages were installed using the Sury repository.

## Pterodactyl Panel

The Panel is installed under:

    /var/www/pterodactyl

The Laravel application is configured for production.

Current application configuration includes:

    APP_ENV=production
    APP_DEBUG=false
    APP_TIMEZONE=Australia/Melbourne
    APP_URL=https://panel.robynshomelab.dev

The Panel database is hosted locally on VM108 using MariaDB.

Redis is used for the Laravel queue.

The Panel database migrations and seed operations have been completed.

An administrative account has been created.

Credentials are intentionally not documented in this repository.

## Pterodactyl Network Architecture

The Panel is accessed through CT106 rather than being directly exposed.

    Client
      |
      | HTTPS
      v
    CT106 Nginx
    192.168.20.94
      |
      | HTTP
      v
    VM108
    192.168.20.111
      |
      v
    Pterodactyl Panel

CT106 currently handles the external-facing HTTPS/TLS layer.

The Panel itself communicates with the local VM Nginx over HTTP.

## Storage

The current Proxmox installation uses local storage on each host.

VM108's virtual disk is stored on:

    local-lvm

The VM's 40 GB virtual disk is intended for the operating system and Pterodactyl application components.

Bulk storage is planned separately on `pve-2`.

A WD Blue 4 TB (`WD40EZRZ`) HDD is intended to be installed directly into `pve-2`.

The planned storage architecture is:

    pve-2
      |
      +--> SSD
      |     |
      |     +--> Proxmox
      |     +--> VM108
      |
      +--> 4 TB HDD
            |
            +--> Host filesystem
            +--> NFS/fileshare
            +--> Future media storage

The 4 TB HDD is not intended to replace the Proxmox VM storage.

## Proxmox Networking

The Proxmox hosts currently operate on:

    192.168.20.0/24

Default gateway:

    192.168.20.1

The current network is flat.

Both Proxmox hosts connect directly to the existing network infrastructure.

A managed switch, VLANs, and improved firewall/routing are planned for future network upgrades.

## Backups

Proxmox VM backup configuration is enabled for VM108.

A broader backup strategy for application data, databases, configuration, and future game-server data still needs to be developed.

The future backup design should account for:

- Proxmox VM configuration
- Pterodactyl Panel data
- MariaDB
- Redis configuration
- Wings configuration
- Game-server data
- Nginx configuration
- DNS configuration
- Critical service configuration

## Future Pterodactyl Components

The following components are not yet deployed:

- Pterodactyl Wings
- Pterodactyl node registration
- Game-server allocations
- Game servers
- NetBird peer on VM108
- Game-server networking
- Pterodactyl-specific monitoring

The intended future architecture is:

    VM108
      |
      +--> Pterodactyl Panel
      |
      +--> Wings
            |
            +--> Docker
                  |
                  +--> Game Server
                  +--> Game Server
                  +--> Game Server

VM108 will eventually run its own NetBird peer.

This will allow game-server networking to be handled independently from the existing CT101 routing peer.

## VMID Allocation

Current and reserved VMIDs:

| VMID | Status | Purpose |
|---|---|---|
| CT100 | Deployed | Pi-hole / Unbound / DDNS |
| CT101 | Deployed | NetBird |
| CT102 | Deployed | Jellyfin |
| VM103 | Reserved | Media stack |
| CT104 | Deployed | Beszel |
| CT105 | Deployed | Uptime Kuma |
| CT106 | Deployed | Nginx / Certbot |
| VM107 | Reserved | Homarr |
| VM108 | Deployed | Pterodactyl |

## Proxmox Design Principles

The current Proxmox architecture prioritises:

1. Simple service separation.
2. Reuse of existing hardware.
3. Low overhead for infrastructure services.
4. Dedicated VM isolation for Pterodactyl.
5. Separate bulk storage from VM storage.
6. Incremental expansion.
7. Avoiding unnecessary HA complexity.

The Proxmox configuration should be updated whenever nodes, guests, storage, or cluster architecture changes.