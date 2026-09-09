# Network

This document describes the current network architecture of the homelab, including addressing, DNS, reverse proxying, remote access, and the planned network expansion.

---

## Network Overview

The homelab currently operates on a single LAN:

```text id="q2f8z1"
Network: 192.168.20.0/24
Gateway: 192.168.20.1
```

The current network does not use VLAN segmentation or a dedicated firewall/router.

All Proxmox hosts and homelab services are currently reachable over the local LAN according to their configured firewall and service access rules.

A managed switch and network segmentation are planned for a future stage of the homelab.

---

# IP Addressing

The current static/reserved addressing is:

| Address          | Host / Service      | Purpose                   |
| ---------------- | ------------------- | ------------------------- |
| `192.168.20.1`   | Router              | Default gateway           |
| `192.168.20.93`  | CT103 `mediastack`  | Media automation          |
| `192.168.20.94`  | CT106 `nginx`       | Reverse proxy / TLS       |
| `192.168.20.95`  | CT105 `uptime-kuma` | Service monitoring        |
| `192.168.20.96`  | CT104 `beszel`      | System monitoring         |
| `192.168.20.97`  | CT101 `netbird`     | NetBird routing peer      |
| `192.168.20.98`  | CT102 `jellyfin`    | Media server              |
| `192.168.20.99`  | CT100 `pihole`      | DNS / Pi-hole             |
| `192.168.20.100` | `pve-1`             | Proxmox                   |
| `192.168.20.101` | `pve-2`             | Proxmox / storage         |
| `192.168.20.102` | `RobynPC`           | Administration desktop    |
| `192.168.20.111` | VM108 `pterodactyl` | Pterodactyl Panel / Wings |

The router's DHCP pool begins at `.150`, allowing the lower address range to be used for infrastructure.

---

# Proxmox Network

The two physical Proxmox systems are:

```text id="q5g2r9"
pve-1
192.168.20.100

pve-2
192.168.20.101
```

Both systems belong to the:

```text id="j0g6zq"
homelab
```

Proxmox cluster.

The current cluster uses a simple LAN-based network and does not currently have dedicated management, storage, migration, or cluster VLANs.

---

# Service Network Layout

The primary service architecture is:

```text id="v2w8bp"
                         Router
                      192.168.20.1
                            │
                            │
              ┌─────────────┴─────────────┐
              │                           │
        ┌─────▼─────┐               ┌─────▼─────┐
        │   pve-1   │               │   pve-2   │
        │ .100      │               │ .101      │
        └─────┬─────┘               └─────┬─────┘
              │                           │
       ┌──────┼───────────────┐     ┌─────┴──────┐
       │      │       │       │     │            │
      .93    .94     .95     .96   .111       Storage
     Media  Nginx   Kuma   Beszel  Ptero         NFS
       │      │
      .98    .99
    Jellyfin Pi-hole
```

---

# DNS Architecture

Pi-hole provides the primary DNS service for the homelab:

```text id="qbyj3p"
192.168.20.99:53
```

Unbound runs behind Pi-hole and performs recursive DNS resolution.

The local DNS path is:

```text id="lq8d4e"
Client
  │
  ▼
Pi-hole
192.168.20.99:53
  │
  ▼
Unbound
  │
  ▼
Internet DNS hierarchy
```

Pi-hole is also used for internal DNS records.

---

# Split DNS

The domain:

```text id="e0c8a6"
robynshomelab.dev
```

is used for both internal service access and public DNS/ACME purposes.

Internally, Pi-hole resolves service hostnames to the Nginx reverse proxy.

Current internal records include:

```text id="p4j9e7"
panel.robynshomelab.dev  → 192.168.20.94
jellyfin.robynshomelab.dev → 192.168.20.94
status.robynshomelab.dev  → 192.168.20.94
beszel.robynshomelab.dev  → 192.168.20.94
pihole.robynshomelab.dev  → 192.168.20.94
```

The Wings hostname is directed to the Pterodactyl VM:

```text id="6h8k3a"
wings.robynshomelab.dev → 192.168.20.111
```

This allows clients on the LAN to use the same hostnames as the reverse-proxied services without requiring those services to be directly exposed on the LAN.

---

# Reverse Proxy Network Path

Nginx operates on CT106:

```text id="y9p4vn"
192.168.20.94
```

HTTPS connections terminate at Nginx.

The current internal routing is:

```text id="4z1g3c"
Client
  │
  │ HTTPS :443
  ▼
Nginx
192.168.20.94
  │
  ├── Jellyfin → 192.168.20.98:8096
  ├── Uptime Kuma → 192.168.20.95:3001
  ├── Beszel → 192.168.20.96:8090
  ├── Pi-hole → 192.168.20.99:8080
  └── Pterodactyl → 192.168.20.111:80
```

Nginx therefore provides the central HTTPS entry point for the homelab's web services.

---

# Cloudflare

Cloudflare is authoritative for:

```text id="x8m5h4"
robynshomelab.dev
```

Cloudflare is used for:

* Authoritative DNS
* Dynamic DNS
* ACME DNS-01 validation

Cloudflare's proxy/CDN functionality is **not** enabled for homelab service traffic.

DNS records are intentionally configured as DNS-only.

---

# Public DNS vs Internal Access

The Panel hostname is an important example of the split-DNS architecture.

Public Cloudflare DNS contains:

```text id="r1h4bw"
panel.robynshomelab.dev
        │
        ▼
WAN IP
```

Internally, Pi-hole overrides that hostname:

```text id="3p0j7v"
panel.robynshomelab.dev
        │
        ▼
192.168.20.94
        │
        ▼
Nginx
        │
        ▼
192.168.20.111
```

The public DNS record exists primarily to maintain the public hostname and allow Cloudflare DNS-01 certificate validation.

It does **not** provide direct public access to the Panel.

---

# Router and Port Forwarding

The router is:

```text id="x0b7wp"
192.168.20.1
```

There is currently **no router port forwarding** for homelab services.

This is intentional.

Remote access is provided through NetBird rather than exposing individual services directly to the Internet.

The current design therefore avoids opening inbound WAN ports for:

* SSH
* Pterodactyl
* Jellyfin
* Pi-hole
* Monitoring
* Media services

---

# NetBird Network

NetBird provides private remote connectivity to the homelab.

There are currently two separate NetBird peers serving different purposes.

## CT101 Routing Peer

```text id="q3h7ma"
CT101
LAN IP:     192.168.20.97
NetBird IP: 100.113.51.59
```

CT101 operates as a routing peer for selected LAN destinations.

Current routes:

```text id="b6p0qy"
192.168.20.94/32
192.168.20.99/32
```

This provides NetBird clients with access to:

* Nginx
* Pi-hole

NetBird DNS is configured to use:

```text id="n1j6s8"
192.168.20.99:53
```

---

## VM108 NetBird Peer

VM108 also runs NetBird independently:

```text id="v4t7nx"
VM108
LAN IP:     192.168.20.111
NetBird IP: 100.113.229.169
FQDN:       pterodactyl.netbird.cloud
```

VM108 is **not routed through CT101** for its NetBird connection.

It operates as its own NetBird peer.

This allows direct private access to the Pterodactyl VM for administration and future game-server networking.

---

# NetBird Access Architecture

The current architecture can be represented as:

```text id="5w3m1c"
                    NetBird Network
                          │
             ┌────────────┴────────────┐
             │                         │
        NetBird Client            NetBird Client
             │                         │
             ▼                         ▼
          CT101                     VM108
        100.113.51.59            100.113.229.169
             │                         │
             │ LAN routes              │
             ▼                         ▼
       192.168.20.94             192.168.20.111
       192.168.20.99             Pterodactyl
```

The distinction between the two peers is intentional.

CT101 provides LAN routing, while VM108 provides direct access to the Pterodactyl host.

---

# Storage Network

Bulk storage is provided by pve-2:

```text id="4z8n2m"
pve-2
192.168.20.101
```

The storage is mounted locally at:

```text id="x4g7ad"
/mnt/homelab-data
```

Selected directories are exported using NFS.

Current NFS shares include:

```text id="k9x2wc"
/mnt/homelab-data/media
/mnt/homelab-data/downloads
/mnt/homelab-data/games
```

The media and downloads shares are consumed by the media stack.

The games share is consumed by VM108.

---

# Media Network Path

The media stack operates on CT103:

```text id="8m1f4e"
CT103
192.168.20.93
```

The storage path is:

```text id="q9r5sm"
pve-2
192.168.20.101
   │
   │ NFS
   ▼
pve-1
   │
   ▼
CT103
192.168.20.93
```

The media stack then provides content to Jellyfin:

```text id="f6x3pn"
NFS Storage
    │
    ▼
CT103 Media Stack
    │
    ▼
Media Library
    │
    ▼
Jellyfin CT102
192.168.20.98
```

---

# Pterodactyl Network Path

The Pterodactyl VM is:

```text id="a7y4jc"
VM108
192.168.20.111
```

Web access uses the reverse proxy:

```text id="m8q2vd"
Client
  │
  ▼
Nginx
192.168.20.94
  │
  │ HTTP :80
  ▼
Pterodactyl Panel
192.168.20.111
```

Wings operates directly on VM108.

The current Wings services include:

```text id="z4p7xs"
Daemon: 8080
SFTP:   2022
```

The final external game-server networking design remains under development.

---

# Desktop Access

The primary administration workstation is:

```text id="f1q8ds"
RobynPC
192.168.20.102
```

It accesses the homelab through the normal LAN.

The desktop also mounts the media NFS share directly from pve-2.

---

# Network Security Model

The current security model is based on:

1. No router port forwarding
2. Private LAN addressing
3. NetBird for remote access
4. Split DNS
5. Centralised HTTPS termination through Nginx
6. Cloudflare DNS-only records
7. Service isolation using separate containers/VMs
8. Host-level firewalling where configured

The Pterodactyl VM is still awaiting final nftables hardening.

Docker must be considered when implementing the VM108 firewall because Docker-managed networking can interact with host firewall rules.

---

# Future Network Architecture

The current flat LAN is intentionally simple while the homelab is being developed.

Future improvements may include:

```text id="w4c9zr"
                 Firewall / Router
                        │
                 Managed Switch
                        │
        ┌───────────────┼───────────────┐
        │               │               │
     Servers        Management        Clients
        │               │               │
      VLAN           VLAN            VLAN
```

Potential future VLANs include:

* Server infrastructure
* Management
* Storage
* Trusted clients
* IoT
* Guest devices
* Gaming/services

These VLANs have **not yet been deployed**.

---

# Network Design Principles

The current network is designed around several principles:

### Minimise Internet Exposure

Services should remain private unless there is a specific requirement for public access.

### Centralise Web Access

Web services use Nginx as the central TLS/reverse-proxy layer.

### Separate Remote Access from Public Exposure

NetBird provides private remote access instead of relying on router port forwarding.

### Keep DNS Centralised

Pi-hole provides local DNS and split-DNS records, while Unbound provides recursive resolution.

### Separate Storage from Compute

Bulk storage resides on pve-2 and is exposed through NFS rather than being tightly coupled to an individual application container.

### Expand Gradually

The current flat LAN is sufficient for the present scale. VLANs, managed switching and a dedicated firewall will be introduced when the complexity justifies them.
