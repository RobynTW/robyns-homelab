# Proxmox VE

## Overview

Proxmox VE is the virtualisation platform used as the foundation of the homelab.

The homelab currently consists of two physical Proxmox hosts:

* Dell OptiPlex 3060 — `pve-1`
* Dell OptiPlex 9020 SFF — `pve-2`

The two hosts are members of the `homelab` Proxmox cluster.

High-level architecture:

```text
                    homelab Proxmox cluster
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        Dell OptiPlex 3060       Dell OptiPlex 9020
             pve-1                    pve-2
       192.168.20.100            192.168.20.101
              │                         │
       Infrastructure              Pterodactyl
       Media services                VM 108
       Monitoring
```

The cluster is used primarily for centralised Proxmox management. High availability is intentionally not enabled.

---

## Proxmox Cluster

### Cluster Name

```text
Cluster: homelab
Nodes:   pve-1
         pve-2
```

The cluster currently contains two nodes.

Both nodes use the local homelab network:

```text
192.168.20.0/24
```

The cluster currently operates with quorum requiring both nodes.

HA is deliberately disabled. The cluster is therefore used for management and resource organisation rather than automatic service failover.

### Hostnames

The two Proxmox nodes are configured with the following hostnames:

```text
192.168.20.100 pve-1.home pve-1
192.168.20.101 pve-2.home pve-2
```

The corresponding host entries are present on both Proxmox systems.

---

# Proxmox Host — pve-1

## Hardware

```text
Model: Dell OptiPlex 3060
Hostname: pve-1
IP:       192.168.20.100
```

pve-1 is the primary infrastructure and compute host.

Its responsibilities include:

* Network infrastructure
* DNS
* HTTPS reverse proxy
* Remote access
* Media services
* Monitoring
* Homarr (planned)

pve-1 also contains the homelab's existing Nginx reverse-proxy infrastructure.

## Existing LXC Services

| VMID | Hostname       | Purpose                              | IP              |
| ---: | -------------- | ------------------------------------ | --------------- |
|  100 | `pihole-nginx` | Pi-hole, Unbound, Nginx and DDNS     | `192.168.20.99` |
|  101 | `netbird`      | Private remote access / routing peer | `192.168.20.97` |
|  102 | `jellyfin`     | Media server                         | `192.168.20.98` |
|  104 | `beszel`       | System monitoring                    | `192.168.20.96` |
|  105 | `uptime-kuma`  | Service monitoring                   | `192.168.20.95` |

VMID 103 remains unused.

VMID 107 is reserved for the planned Homarr deployment.

---

# Proxmox Host — pve-2

## Hardware

```text
Model: Dell OptiPlex 9020 SFF
Hostname: pve-2
IP:       192.168.20.101
```

Hardware:

```text
CPU: Intel Core i7-4770
Cores: 4 physical / 8 logical
RAM: 16 GB
System SSD: Samsung MZ7PC128HA
SSD capacity: approximately 119 GB
```

The 9020 was introduced as the second physical Proxmox host for the homelab.

Its primary workload is the Pterodactyl game-server environment.

A separate 4 TB WD Blue `WD40EZRZ` HDD is intended to provide bulk storage/NAS functionality. The drive has not yet been installed.

The planned NAS architecture is a simple filesystem/NFS-based share rather than TrueNAS or OpenMediaVault.

---

## pve-2 Proxmox Storage

Current local storage:

```text
local
├── Type: directory
├── Capacity: approximately 40.5 GB
└── Available: approximately 33.9 GB

local-lvm
├── Type: LVM-thin
├── Capacity: approximately 56.5 GB available
└── Used: 0 GB at initial deployment
```

The Proxmox installation resides on the 128 GB-class SSD.

The future 4 TB HDD is intended for bulk file storage and NFS exports rather than Pterodactyl application storage.

---

# Network Configuration

Both Proxmox nodes are connected to the existing homelab LAN:

```text
192.168.20.0/24
```

The current network is still based around the existing ISP router.

A managed network switch is planned for a future infrastructure upgrade.

The current model is:

```text
ISP Router
     │
     ├── pve-1
     │    └── 192.168.20.100
     │
     └── pve-2
          └── 192.168.20.101
```

Both Proxmox systems use `vmbr0` for their virtualised network connectivity.

---

# Proxmox Cluster Integration

The Dell OptiPlex 9020 was installed with Proxmox VE and subsequently integrated into the existing `homelab` cluster.

The resulting cluster is:

```text
homelab
│
├── pve-1
│   └── 192.168.20.100
│
└── pve-2
    └── 192.168.20.101
```

The cluster does not currently use HA.

This means that the cluster provides centralised management but does not automatically migrate or restart workloads if a physical host fails.

---

# Virtual Machines

Proxmox uses KVM/QEMU for full virtual machines.

## VM 108 — Pterodactyl

VMID:

```text
108
```

Host:

```text
pve-2
```

Hostname:

```text
pterodactyl
```

IP:

```text
192.168.20.111
```

Purpose:

```text
Pterodactyl game-server management
```

### VM Configuration

```text
Operating system: Debian 13 (Trixie)
Firmware: OVMF / UEFI
Machine: Q35
CPU: 6 vCPU
CPU type: host
Sockets: 1
Cores: 6
RAM: 12 GB
Disk: 40 GB
Storage: local-lvm
Network: VirtIO
Bridge: vmbr0
SCSI controller: VirtIO SCSI single
QEMU Guest Agent: enabled
NUMA: disabled
Memory ballooning: disabled
Nested virtualisation: disabled
```

Disk configuration:

```text
Bus: SCSI
Storage: local-lvm
Capacity: 40 GB
Cache: none
Discard: enabled
IO thread: enabled
SSD emulation: enabled
Backup: enabled
```

The VM is intentionally headless.

Debian was installed without a desktop environment. SSH server and standard system utilities were installed.

---

# VM 108 Networking

The Pterodactyl VM currently uses:

```text
Interface: ens18
IPv4:      192.168.20.111/24
```

SSH access is available using:

```bash
ssh robyn@192.168.20.111
```

The VM's hostname is:

```text
pterodactyl
```

The VM currently receives its LAN address through DHCP. A permanent DHCP reservation/static addressing arrangement can be implemented later.

---

# VM 108 Base Configuration

The Debian installation was verified as:

```text
Debian GNU/Linux 13 (Trixie)
Kernel: 6.12.107+deb13-amd64
Virtualisation: KVM
```

The initial user account is:

```text
robyn
```

`sudo` was installed and the user was added to the sudo group.

The VM is administered primarily through SSH.

---

# Future Storage Architecture

The Dell OptiPlex 9020 is intended to provide both compute and bulk storage.

The intended architecture is:

```text
Dell OptiPlex 9020
│
├── Proxmox
│
├── 4 TB HDD
│   └── NFS / file share
│
└── VM 108
    └── Pterodactyl
```

The 4 TB HDD is intended to be a simple network file share.

It is not intended to host the Pterodactyl VM itself.

The Pterodactyl VM currently uses the 9020's system SSD.

---

# Proxmox Management Commands

Useful commands include:

```bash
pvecm status
```

Check cluster status.

```bash
pvecm nodes
```

List cluster nodes.

```bash
qm list
```

List virtual machines.

```bash
qm status 108
```

Check VM 108 status.

```bash
qm config 108
```

Display VM 108 configuration.

```bash
qm start 108
```

Start VM 108.

```bash
qm stop 108
```

Stop VM 108.

```bash
ip addr
```

Inspect network interfaces.

```bash
ip route
```

Inspect routing.

```bash
ss -tulpn
```

Inspect listening services.

---

# Current Proxmox Status

```text
pve-1:
    Operational
    192.168.20.100

pve-2:
    Operational
    192.168.20.101

Cluster:
    homelab
    Operational
    2 nodes
    HA disabled

Pterodactyl VM:
    VMID 108
    Operational
    192.168.20.111

4 TB HDD:
    Not yet installed
    Planned for NFS/file sharing
```

---

# Documentation Philosophy

When infrastructure changes, this document should be updated to reflect the actual deployed state.

Document:

* VMID
* Hostname
* IP address
* Physical host
* Purpose
* CPU/RAM allocation
* Storage
* Network configuration
* Important services
* Cluster membership
* Important troubleshooting commands

Do not commit:

* Passwords
* Private keys
* API tokens
* Database credentials
* Other secrets

The documentation should distinguish between **deployed**, **in progress**, and **planned** infrastructure rather than presenting planned architecture as operational.
