# Robyn's Homelab

## Overview

This repository contains the documentation, configuration, diagrams, and supporting scripts for my personal homelab.

The purpose of this homelab is not only to provide useful services, but also to serve as a practical learning environment. The documentation therefore explains both **what has been configured** and **why it has been configured that way**.

The infrastructure is being developed incrementally, with each major stage documented and version-controlled using Git.

---

## Current Architecture

The homelab currently consists of two primary physical systems:

* **Dell OptiPlex 3060** — primary Proxmox host for network, media, monitoring, and supporting services.
* **Dell OptiPlex 9020 SFF** — planned secondary Proxmox host for storage/NAS and game-server workloads.

The current network is a relatively simple flat LAN provided by the ISP router and an unmanaged switch.

A future network redesign will introduce a dedicated pfSense router, managed switching, and VLAN-based network segmentation.

---

## Proxmox

The Dell 3060 runs Proxmox VE and currently hosts several LXC containers:

| VMID | Hostname       | Purpose                       | IP              |
| ---: | -------------- | ----------------------------- | --------------- |
|  100 | `pihole-nginx` | Pi-hole, Unbound and Nginx    | `192.168.20.99` |
|  101 | `netbird`      | Private remote-access gateway | `192.168.20.97` |
|  102 | `jellyfin`     | Media server                  | `192.168.20.98` |
|  104 | `beszel`       | System monitoring             | `192.168.20.96` |
|  105 | `uptime-kuma`  | Service monitoring            | `192.168.20.95` |

The Proxmox host itself uses:

```text
Hostname: pve-1
IP:       192.168.20.100
```

The host is currently standalone rather than part of a Proxmox cluster.

---

## DNS Architecture

Pi-hole provides DNS for the homelab on port 53.

Unbound runs locally on the Pi-hole container and provides recursive DNS resolution and DNSSEC validation.

The resulting architecture is:

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

Pi-hole remains responsible for local DNS records and DNS filtering, while Unbound handles recursive external DNS resolution.

---

HTTPS and Reverse Proxy

Nginx runs alongside Pi-hole and acts as the central HTTPS reverse proxy.

Cloudflare provides authoritative DNS for the robynshomelab.dev domain and is used for DNS-01 validation when obtaining Let's Encrypt certificates.

The current service hostnames are:

jellyfin.robynshomelab.dev
status.robynshomelab.dev
beszel.robynshomelab.dev
pihole.robynshomelab.dev

These hostnames currently resolve internally through Pi-hole to:

192.168.20.99

The service records are not publicly published to Cloudflare DNS.

Nginx receives the HTTPS requests and forwards them to the appropriate internal service.

---

## Remote Access

NetBird provides private remote access to the homelab.

The NetBird LXC is separate from the NetBird installation planned for the future Pterodactyl server.

The current NetBird deployment is intended for **private homelab access**, rather than public service exposure.

---

## Media

Jellyfin runs on the Dell 3060 because the system provides access to its Intel integrated GPU for hardware-accelerated media transcoding.

The future media architecture will use the 9020 as network storage:

```text
Jellyseerr
    │
    ├── Sonarr
    └── Radarr
          │
       Prowlarr
          │
      qBittorrent
          │
          ▼
      NAS / NFS
          │
          ▼
       Jellyfin
```

This portion of the architecture will be implemented after the 9020 NAS is established.

---

## Monitoring

Two monitoring systems are currently deployed:

### Beszel

Used for system-level monitoring of the Proxmox host and service containers.

### Uptime Kuma

Used for service availability monitoring, including DNS, HTTP, and network reachability checks.

Using both provides two different perspectives:

* **Beszel** — system health and resource utilisation.
* **Uptime Kuma** — service availability and uptime.

---

## Planned Infrastructure

The next major stages of the homelab are:

1. Cloudflare DDNS
2. Network architecture diagram
3. Dell 9020 NAS
4. NFS storage
5. Media automation stack
6. Pterodactyl
7. NetBird service exposure
8. Homelab dashboard
9. pfSense
10. Managed switching
11. VLAN segmentation

The architecture will evolve as these components are introduced.

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

Example progression:

```text
v1 — Current infrastructure
v2 — NAS + storage
v3 — Media + Pterodactyl
v4 — pfSense + VLANs
```

The exact versioning scheme may evolve as the homelab grows.
