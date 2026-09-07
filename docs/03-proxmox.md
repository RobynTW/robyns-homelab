# Proxmox VE

## Overview

Proxmox VE is the virtualisation platform used as the foundation of the homelab.

The primary Proxmox host is a Dell OptiPlex 3060.

```text
Hostname: pve-1
IP:       192.168.20.100
```

The host is currently operating as a standalone Proxmox server rather than part of a Proxmox cluster.

Proxmox provides the virtualisation and container infrastructure used by the homelab's core services.

---

## Proxmox Host

### Dell OptiPlex 3060

The 3060 is currently the primary homelab compute host.

Its primary responsibilities are:

* Network infrastructure
* DNS
* HTTPS reverse proxy
* Remote access
* Media services
* Monitoring

The current LXC allocation is:

| VMID | Hostname       | Purpose                          | IP              |
| ---: | -------------- | -------------------------------- | --------------- |
|  100 | `pihole-nginx` | Pi-hole, Unbound, Nginx and DDNS | `192.168.20.99` |
|  101 | `netbird`      | Private remote access            | `192.168.20.97` |
|  102 | `jellyfin`     | Media server                     | `192.168.20.98` |
|  104 | `beszel`       | System monitoring                | `192.168.20.96` |
|  105 | `uptime-kuma`  | Service monitoring               | `192.168.20.95` |

VMID 103 is intentionally unused at present and is reserved for the planned media stack.

---

## LXC Containers

The majority of the current homelab services run as Linux Containers (LXC).

LXC provides lightweight operating-system-level virtualisation.

Compared with a full virtual machine, containers share the host kernel and generally require fewer resources.

This makes LXC suitable for many of the relatively lightweight services in the homelab.

### CT 100 — pihole-nginx

```text
VMID:     100
Hostname: pihole-nginx
IP:       192.168.20.99
```

CT 100 hosts several closely related network services:

* Pi-hole
* Unbound
* Nginx
* ddclient

The services share the same container because they form the primary DNS, HTTPS and DDNS infrastructure for the homelab.

---

### CT 101 — NetBird

```text
VMID:     101
Hostname: netbird
IP:       192.168.20.97
```

CT 101 provides private remote access to the homelab using NetBird.

It allows authorised remote devices to access selected services on the `192.168.20.0/24` network.

---

### CT 102 — Jellyfin

```text
VMID:     102
Hostname: jellyfin
IP:       192.168.20.98
```

CT 102 runs Jellyfin.

Jellyfin remains on the 3060 because the host provides access to its Intel integrated GPU for hardware-accelerated media transcoding.

The future NAS will provide storage to the media services, while Jellyfin remains on the compute host.

---

### CT 104 — Beszel

```text
VMID:     104
Hostname: beszel
IP:       192.168.20.96
```

CT 104 runs Beszel for system-level monitoring.

It provides visibility into system resource usage and health.

---

### CT 105 — Uptime Kuma

```text
VMID:     105
Hostname: uptime-kuma
IP:       192.168.20.95
```

CT 105 runs Uptime Kuma for service availability monitoring.

It is used to monitor whether services and network endpoints remain reachable.

---

## Container Networking

The LXC containers are connected to the homelab's `192.168.20.0/24` network.

This allows containers to communicate directly with one another.

For example:

```text
CT 100
192.168.20.99
     │
     │ HTTP
     ▼
CT 102
192.168.20.98
Jellyfin
```

Nginx on CT 100 can therefore reverse proxy requests to Jellyfin without requiring the services to communicate through the public Internet.

The same principle applies to other internal services.

---

## Container Management

Proxmox provides the `pct` command for managing LXC containers.

The most useful commands for this homelab include:

### List containers

```bash
pct list
```

Displays the LXC containers configured on the Proxmox host, including their VMIDs, status and hostnames.

---

### Container status

```bash
pct status 100
```

Checks the current state of CT 100.

The VMID can be replaced with another container's VMID.

For example:

```bash
pct status 102
```

checks Jellyfin.

---

### Start a container

```bash
pct start 100
```

Starts the specified LXC container.

---

### Stop a container

```bash
pct stop 100
```

Stops the specified LXC container.

---

### Enter a container

```bash
pct enter 100
```

Opens a shell inside the specified container.

This is useful when performing configuration or troubleshooting from the Proxmox host.

For example:

```bash
pct enter 100
```

enters the Pi-hole/NGINX container.

---

### Container configuration

```bash
pct config 100
```

Displays the Proxmox configuration for a container.

This can be useful for checking:

* Network configuration
* Storage mounts
* Container features
* Resource limits
* Startup configuration

---

## Virtual Machines

Proxmox also supports full virtual machines through KVM/QEMU.

The `qm` command is used to manage these virtual machines.

For example:

```bash
qm list
```

lists the virtual machines configured on the Proxmox host.

The homelab does not currently rely on a large number of virtual machines.

A future Pterodactyl installation is planned to run inside a dedicated VM on the Dell OptiPlex 9020.

---

## Proxmox Storage

The current Proxmox host provides the storage used by its local containers.

The future storage architecture will separate compute from bulk storage.

The planned model is:

```text
Dell OptiPlex 3060
└── Proxmox
    └── Jellyfin / Services
             │
             │ NFS
             ▼
Dell OptiPlex 9020
└── Proxmox
    └── NAS Storage
```

This allows the 9020 to provide storage while the 3060 continues providing compute for services such as Jellyfin.

---

## Proxmox Host Networking

The Proxmox host is currently connected directly to the ISP router.

The current network path is:

```text
Internet
    │
    ▼
ISP Router
    │
    ▼
Proxmox 3060
    │
    ├── CT 100
    ├── CT 101
    ├── CT 102
    ├── CT 104
    └── CT 105
```

A network switch is planned but is not currently installed.

The future switch will allow the 3060 and 9020 to share the same physical network infrastructure.

---

## Proxmox Cluster Status

The 3060 is currently a standalone Proxmox host.

There is no Proxmox cluster at present.

This is intentional because the homelab currently consists of a single active Proxmox host.

The planned 9020 does not automatically imply that the two systems will form a cluster. The final architecture will be determined based on the storage and workload requirements of the homelab.

---

## Future Proxmox Architecture

The planned infrastructure will eventually consist of two physical Proxmox systems:

```text
Dell OptiPlex 3060
└── Proxmox
    ├── Infrastructure
    ├── Jellyfin
    └── Monitoring


Dell OptiPlex 9020
└── Proxmox
    ├── NAS / Storage
    └── Pterodactyl VM
```

The 9020 is planned but is not currently part of the operational Proxmox infrastructure.

---

## Troubleshooting Approach

When troubleshooting a Proxmox service, the investigation should generally proceed from the host toward the container and then toward the application.

```text
Proxmox host
     ↓
Container state
     ↓
Container network
     ↓
Service process
     ↓
Service port
     ↓
Application
```

For example, if Jellyfin becomes unavailable:

1. Check whether CT 102 is running.
2. Check the container's network connectivity.
3. Check whether Jellyfin is running.
4. Check whether the expected port is listening.
5. Test access directly.
6. Check Nginx if the direct service works but HTTPS does not.

This separates Proxmox/container problems from application problems.

---

## Key Commands

The following commands form the core Proxmox troubleshooting toolkit used by this homelab.

| Command             | Purpose                              |
| ------------------- | ------------------------------------ |
| `pct list`          | List LXC containers                  |
| `pct status <VMID>` | Check container status               |
| `pct start <VMID>`  | Start an LXC container               |
| `pct stop <VMID>`   | Stop an LXC container                |
| `pct enter <VMID>`  | Open a shell inside a container      |
| `pct config <VMID>` | Display container configuration      |
| `qm list`           | List virtual machines                |
| `qm status <VMID>`  | Check VM status                      |
| `ip addr`           | Inspect network interfaces           |
| `ip route`          | Inspect routing                      |
| `ping <address>`    | Test network connectivity            |
| `ss -tulpn`         | Inspect listening services and ports |

Commands should generally be run on the Proxmox host unless otherwise stated.

---

## Documentation and Configuration Philosophy

The Proxmox configuration should be documented alongside the services running on it.

When a container is created or modified, the documentation should record:

* VMID
* Hostname
* IP address
* Purpose
* Network configuration
* Storage configuration
* Important resource allocations
* Services running inside the container
* Relevant troubleshooting procedures

Secrets such as passwords, private keys and API tokens must not be committed to Git.

---

## Future Updates

This document should be updated when:

* The 9020 is deployed
* Additional LXC containers are created
* The media stack is deployed
* Pterodactyl is deployed
* Proxmox networking changes
* Storage configuration changes
* A second Proxmox host is introduced
* A cluster is created, if one is eventually required
