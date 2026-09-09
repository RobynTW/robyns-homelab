# Network

## Overview

The homelab currently operates on a single flat LAN.

The network is intentionally simple at this stage, with both Proxmox hosts connected directly to the existing home router.

Future networking plans include a managed switch, VLANs, and improved firewall/routing.

## Current Network

| Component | Address |
|---|---|
| LAN | `192.168.20.0/24` |
| Router / Gateway | `192.168.20.1` |
| pve-1 | `192.168.20.100` |
| pve-2 | `192.168.20.101` |

All infrastructure services currently communicate across the same LAN.

## Proxmox Hosts

### pve-1

    Hostname: pve-1
    IP:       192.168.20.100

### pve-2

    Hostname: pve-2
    IP:       192.168.20.101

The two hosts are members of the same Proxmox cluster:

    Cluster: homelab

HA is deliberately disabled.

## Service IP Allocation

| VM/CT | Hostname | IP | Primary Service |
|---|---|---|---|
| CT100 | `pihole` | `192.168.20.99` | Pi-hole / Unbound / DDNS |
| CT101 | `netbird` | `192.168.20.97` | NetBird |
| CT102 | `jellyfin` | `192.168.20.98` | Jellyfin |
| CT104 | `beszel` | `192.168.20.96` | Beszel |
| CT105 | `uptime-kuma` | `192.168.20.95` | Uptime Kuma |
| CT106 | `nginx` | `192.168.20.94` | Nginx / Certbot |
| VM108 | `pterodactyl` | `192.168.20.111` | Pterodactyl Panel |

Reserved:

| VMID | Planned Service |
|---|---|
| VM103 | Media stack |
| VM107 | Homarr |

## DNS

CT100 provides the primary DNS service for the homelab.

    Pi-hole
    192.168.20.99:53
         |
         v
    Unbound
    127.0.0.1:5335

Pi-hole provides:

- DNS filtering
- Local DNS records
- Internal split-DNS overrides

Unbound provides recursive DNS resolution.

## Internal DNS

Internal service hostnames resolve to CT106, which acts as the central reverse proxy.

| Hostname | Internal Address |
|---|---|
| `jellyfin.robynshomelab.dev` | `192.168.20.94` |
| `status.robynshomelab.dev` | `192.168.20.94` |
| `beszel.robynshomelab.dev` | `192.168.20.94` |
| `pihole.robynshomelab.dev` | `192.168.20.94` |
| `panel.robynshomelab.dev` | `192.168.20.94` |

This allows clients on the LAN to use the same hostnames regardless of whether the service is physically located on another VM or container.

## Reverse Proxy

CT106 is the central Nginx reverse proxy.

    CT106
    192.168.20.94
         |
         +--> Jellyfin
         |    192.168.20.98:8096
         |
         +--> Uptime Kuma
         |    192.168.20.95:3001
         |
         +--> Beszel
         |    192.168.20.96:8090
         |
         +--> Pi-hole
         |    192.168.20.99:8080
         |
         +--> Pterodactyl Panel
              192.168.20.111:80

CT106 handles HTTPS and TLS termination.

Backend services currently communicate with Nginx over the internal LAN using HTTP where appropriate.

## Pterodactyl Network Path

The Pterodactyl Panel is hosted on VM108:

    VM108
    192.168.20.111

Clients access the Panel through the Nginx reverse proxy:

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

The Panel is intended to remain a private service.

There is currently no direct router port forwarding to VM108.

## NetBird

CT101 operates as the NetBird routing peer.

    CT101
    192.168.20.97

NetBird provides remote access to selected internal network resources without exposing those resources directly to the Internet.

Current routed networks/hosts include:

    192.168.20.94/32
    192.168.20.99/32

These provide access to:

- CT106 Nginx
- CT100 Pi-hole

## NetBird DNS

NetBird clients use Pi-hole as their DNS resolver:

    192.168.20.99:53

This means NetBird clients can receive the same DNS filtering and internal hostname resolution as LAN clients.

The intended flow is:

    NetBird Client
          |
          v
    NetBird Network
          |
          v
    CT101
    192.168.20.97
          |
          +--> Pi-hole
          |    192.168.20.99
          |
          +--> Nginx
               192.168.20.94

## Pterodactyl + NetBird

The current Panel does not require a direct NetBird route to VM108.

Instead:

    NetBird Client
          |
          v
    CT101 NetBird
          |
          | route: 192.168.20.94/32
          v
    CT106 Nginx
          |
          v
    VM108
    192.168.20.111

Later, VM108 will have its own NetBird peer.

This will allow game-server networking to be separated from the Panel's access path.

The future architecture is:

    Internet
       |
       v
    NetBird
       |
       v
    VM108
       |
       +--> Wings
       |
       +--> Docker
       |
       +--> Game servers

## Cloudflare

Cloudflare is authoritative for:

    robynshomelab.dev

Cloudflare is currently used for:

- Authoritative DNS
- DDNS
- Let's Encrypt DNS-01 validation

Cloudflare proxying is not currently used.

Public DNS records exist for services such as:

    home.robynshomelab.dev
    panel.robynshomelab.dev

These records point to the current WAN address.

The `panel` record is DNS-only and does not provide direct public access to the Panel because there is no router port forwarding.

Internal clients resolve the Panel hostname through Pi-hole to:

    panel.robynshomelab.dev
        |
        v
    192.168.20.94

This is deliberate split-DNS behaviour.

## Internet Exposure

There is currently no router port forwarding for homelab services.

The intended access model is:

    LAN Client
        |
        v
    Internal DNS
        |
        v
    Nginx
        |
        v
    Internal Service

or:

    NetBird Client
        |
        v
    NetBird Routing Peer
        |
        v
    Nginx
        |
        v
    Internal Service

Cloudflare DNS does not imply that the services are publicly reachable.

## Current Firewall Model

The current network relies primarily on the existing home router and host/service configuration.

The Pterodactyl VM currently does not have its own active Proxmox firewall configuration.

Firewall rules will be refined after Wings, Docker, NetBird, and the actual game-server allocations are deployed.

This avoids prematurely restricting Docker or game-server networking before the final port requirements are known.

## Future Network Architecture

The current flat network is temporary.

The planned architecture includes:

- Managed Ethernet switch
- VLAN support
- Dedicated firewall/router
- Separation of infrastructure services
- Dedicated server/game-server networking
- More granular access control
- Improved monitoring of network infrastructure

Potential future logical separation may include:

    Management
        |
        +--> Proxmox
        +--> Switch
        +--> Firewall

    Infrastructure
        |
        +--> DNS
        +--> Monitoring
        +--> Reverse Proxy

    Services
        |
        +--> Jellyfin
        +--> Media Stack
        +--> Pterodactyl

    Storage
        |
        +--> NFS
        +--> Bulk HDD storage

    Remote Access
        |
        +--> NetBird

The exact VLAN structure has not yet been finalised.

## Network Design Principles

The network is designed around:

1. Minimal direct Internet exposure.
2. Centralised reverse proxying.
3. Internal split DNS.
4. NetBird for remote private access.
5. Separation of services at the VM/container level.
6. Incremental introduction of VLANs and firewall rules.
7. Avoiding unnecessary public port forwarding.

The network architecture should be updated as physical networking and VLAN infrastructure are introduced.