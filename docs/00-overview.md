# Homelab Overview

## Project

This repository documents Robyn's personal homelab infrastructure.

The homelab is built around two Proxmox hosts running in a single cluster, with dedicated containers and virtual machines for individual services.

Primary domain:

robynshomelab.dev

Repository:

https://github.com/RobynTW/robyns-homelab

## Current Status

### Deployed

- Two-node Proxmox cluster (`homelab`)
- Pi-hole + Unbound DNS
- Cloudflare authoritative DNS
- Cloudflare DDNS
- NetBird VPN/routing
- Nginx reverse proxy
- Let's Encrypt certificates via Certbot DNS-01
- Jellyfin
- Beszel monitoring
- Uptime Kuma monitoring
- Pterodactyl Panel
- Debian VM dedicated to Pterodactyl

### In Progress

- Pterodactyl HTTPS access
- Pterodactyl Wings
- Pterodactyl node configuration
- 4 TB HDD storage on `pve-2`
- NFS/fileshare infrastructure

### Planned

- Pterodactyl game servers
- NetBird integration for game-server networking
- Media automation stack
- Homarr dashboard
- Managed network switch
- Network segmentation/VLANs
- pfSense/router improvements
- Expanded monitoring and backup infrastructure

## Physical Infrastructure

### `pve-1`

- Dell OptiPlex 3060
- Proxmox VE
- IP: `192.168.20.100`
- Primary host for core infrastructure containers

### `pve-2`

- Dell OptiPlex 9020 SFF
- Intel i7-4770
- 16 GB RAM
- Proxmox VE
- IP: `192.168.20.101`
- Hosts the Pterodactyl VM
- Intended to provide future bulk storage

## Proxmox Cluster

Cluster name:

`homelab`

The two physical hosts are members of the same Proxmox cluster.

| Node | IP | Status |
|---|---|---|
| `pve-1` | `192.168.20.100` | Deployed |
| `pve-2` | `192.168.20.101` | Deployed |

High availability is deliberately disabled.

The cluster currently requires both nodes for quorum.

## Network

LAN:

`192.168.20.0/24`

Router:

`192.168.20.1`

The current network is intentionally simple and flat. Both Proxmox hosts connect directly to the existing network infrastructure.

A managed switch, VLANs, and more advanced firewall/routing are planned for a later stage.

## Core Services

| VM/CT | Hostname | IP | Service |
|---|---|---|---|
| CT100 | `pihole` | `192.168.20.99` | Pi-hole, Unbound, DDNS |
| CT101 | `netbird` | `192.168.20.97` | NetBird routing peer |
| CT102 | `jellyfin` | `192.168.20.98` | Jellyfin |
| CT104 | `beszel` | `192.168.20.96` | Beszel |
| CT105 | `uptime-kuma` | `192.168.20.95` | Uptime Kuma |
| CT106 | `nginx` | `192.168.20.94` | Nginx + Certbot |
| VM108 | `pterodactyl` | `192.168.20.111` | Pterodactyl Panel |

Reserved VMIDs:

- VM103 — future media stack
- VM107 — future Homarr

## DNS Architecture

Pi-hole provides local DNS filtering and internal DNS overrides.

Unbound runs locally on CT100 and provides recursive DNS resolution for Pi-hole.

Internal service names resolve to the Nginx reverse proxy:

- `jellyfin.robynshomelab.dev` → `192.168.20.94`
- `status.robynshomelab.dev` → `192.168.20.94`
- `beszel.robynshomelab.dev` → `192.168.20.94`
- `pihole.robynshomelab.dev` → `192.168.20.94`
- `panel.robynshomelab.dev` → `192.168.20.94`

Cloudflare remains authoritative for the public domain.

## Reverse Proxy Architecture

CT106 provides the central Nginx reverse proxy and TLS termination.

Current architecture:

    Client
      |
      | HTTPS
      v
    Nginx / Certbot
    CT106 - 192.168.20.94
      |
      +--> Jellyfin       192.168.20.98:8096
      |
      +--> Uptime Kuma    192.168.20.95:3001
      |
      +--> Beszel         192.168.20.96:8090
      |
      +--> Pi-hole        192.168.20.99:8080
      |
      +--> Pterodactyl    192.168.20.111:80

TLS certificates are issued using Let's Encrypt DNS-01 through Cloudflare.

## Pterodactyl

Pterodactyl is hosted on VM108 on `pve-2`.

The Panel is already installed and operational locally.

Current architecture:

    LAN / NetBird Client
            |
            | HTTPS
            v
    CT106 Nginx
    192.168.20.94
            |
            | HTTP
            v
    VM108 Pterodactyl
    192.168.20.111
            |
            +--> Nginx
            +--> PHP-FPM
            +--> Laravel
            +--> MariaDB
            +--> Redis

The Panel is intended to remain private and accessible through the LAN and NetBird.

The VM will later run Pterodactyl Wings and the game-server workloads.

## NetBird

CT101 acts as the NetBird routing peer.

It provides access from NetBird clients to selected services on the LAN.

Current routes include:

    192.168.20.94/32
    192.168.20.99/32

This allows NetBird clients to reach the Nginx reverse proxy and Pi-hole.

The Pterodactyl Panel therefore follows:

    NetBird Client
        |
        v
    CT101 NetBird
        |
        | 192.168.20.94/32
        v
    CT106 Nginx
        |
        v
    VM108 Pterodactyl

The Pterodactyl VM will eventually run its own NetBird peer for game-server networking.

## Storage

`pve-2` is intended to provide bulk storage using locally attached HDD storage.

A WD Blue 4 TB (`WD40EZRZ`) drive is intended for this purpose but has not yet been deployed.

Planned architecture:

    pve-2
     |
     +--> Proxmox / VM storage
     |
     +--> 4 TB HDD
           |
           +--> Host filesystem
           |
           +--> NFS/fileshare
           |
           +--> Future media storage

The HDD is not intended to be used as Pterodactyl VM storage.

A dedicated NAS operating system such as TrueNAS or OpenMediaVault is not part of the current design.

## Media

Jellyfin is already deployed on CT102.

A separate media automation stack is planned for VMID 103.

Planned services include:

- Seerr/Jellyseerr
- Sonarr
- Radarr
- Prowlarr
- Bazarr
- qBittorrent

The future media stack will use storage provided by `pve-2`.

## Monitoring

Current monitoring services:

- Beszel — CT104
- Uptime Kuma — CT105

Future monitoring will include the Pterodactyl VM, Wings, and game servers.

## Security Model

The homelab is designed to minimise direct public exposure.

There is currently no router port forwarding for homelab services.

Cloudflare provides:

- Authoritative DNS
- DDNS
- Let's Encrypt DNS-01 validation

Cloudflare proxying is not currently used.

Internal services are accessed through:

- LAN
- NetBird

Secrets, API tokens, passwords, private keys, and credentials must never be committed to this repository.

## Documentation Principles

This repository should describe the actual deployed architecture rather than the intended future design.

When documenting future components:

- Clearly label them as planned or in progress.
- Do not describe planned services as deployed.
- Do not expose credentials or secrets.
- Prefer actual IP addresses, VMIDs, hostnames, and service paths where useful.
- Update documentation whenever the architecture changes.

The AI context file at the repository root provides the canonical machine-readable summary of the homelab state.

## High-Level Architecture

    Internet
       |
       v
    Cloudflare DNS
       |
       v
    Home Router
    192.168.20.1
       |
       | 192.168.20.0/24
       |
       +-----------------------------+
       |                             |
       v                             v
    pve-1                          pve-2
    192.168.20.100                 192.168.20.101
       |                             |
       |                             +--> VM108 Pterodactyl
       |                                  192.168.20.111
       |
       +--> CT100 Pi-hole / Unbound
       |    192.168.20.99
       |
       +--> CT101 NetBird
       |    192.168.20.97
       |
       +--> CT102 Jellyfin
       |    192.168.20.98
       |
       +--> CT104 Beszel
       |    192.168.20.96
       |
       +--> CT105 Uptime Kuma
       |    192.168.20.95
       |
       +--> CT106 Nginx / Certbot
            192.168.20.94
                |
                +--> Jellyfin
                +--> Uptime Kuma
                +--> Beszel
                +--> Pi-hole
                +--> Pterodactyl

## Current Priority

The immediate infrastructure priority is completing the Pterodactyl deployment:

1. Complete HTTPS access through CT106.
2. Install and configure Wings.
3. Register VM108 as a Pterodactyl node.
4. Verify Docker/Wings operation.
5. Install NetBird directly on VM108.
6. Configure game-server networking.
7. Deploy the first game server.
8. Add monitoring and backups.