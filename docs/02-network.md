# Network

## Overview

This document describes the current homelab network, including physical connectivity, IP addressing, DNS, remote access, and the planned network architecture.

The network is currently intentionally simple:

```text
Internet
   │
   ▼
ISP Router
   │
   ▼
Dell OptiPlex 3060
└── Proxmox
    ├── CT 100 - Pi-hole / Nginx / Unbound / DDNS
    ├── CT 101 - NetBird
    ├── CT 102 - Jellyfin
    ├── CT 104 - Beszel
    └── CT 105 - Uptime Kuma
```

The Dell OptiPlex 9020 and network switch are planned additions and are therefore not part of the current physical network.

---

## Current Network

### Physical Topology

The current network uses the ISP-provided router as the primary router and DHCP server.

There is currently **no network switch**.

```text
                    Internet
                       │
                       ▼
                  ISP Router
                       │
                       │ Ethernet
                       ▼
              Dell OptiPlex 3060
                   Proxmox
```

The 3060 currently connects directly to the ISP router.

The router provides connectivity between the homelab and the Internet and currently performs the routing and NAT functions.

---

## IP Addressing

The current homelab uses the `192.168.20.0/24` private IPv4 network.

| Device / Service |       IP address | Purpose            |
| ---------------- | ---------------: | ------------------ |
| ISP Router       |   `192.168.20.1` | Gateway / router   |
| Proxmox 3060     | `192.168.20.100` | Proxmox host       |
| CT 100           |  `192.168.20.99` | DNS / HTTPS / DDNS |
| CT 101           |  `192.168.20.97` | NetBird            |
| CT 102           |  `192.168.20.98` | Jellyfin           |
| CT 104           |  `192.168.20.96` | Beszel             |
| CT 105           |  `192.168.20.95` | Uptime Kuma        |

The homelab services use static addresses so that other services can reliably reach them.

---

## Proxmox Networking

The Dell OptiPlex 3060 runs Proxmox VE.

Proxmox provides the virtual networking required by the LXC containers.

The containers are connected to the same local network as the Proxmox host, allowing them to communicate directly using their `192.168.20.x` addresses.

This allows services to communicate without requiring port forwarding between containers.

For example:

```text
Jellyfin
192.168.20.98
      ▲
      │ HTTP :8096
      │
Nginx
192.168.20.99
```

Nginx can therefore reverse proxy to Jellyfin directly over the local network.

---

## DNS Architecture

DNS is provided by Pi-hole in CT 100.

The DNS architecture is:

```text
Client
  │
  │ DNS :53
  ▼
Pi-hole
192.168.20.99
  │
  │ DNS
  ▼
Unbound
127.0.0.1:5335
  │
  │ Recursive DNS
  ▼
DNS hierarchy / authoritative servers
```

Pi-hole provides:

* DNS filtering
* Local DNS records
* DNS query visibility
* The primary DNS endpoint for the homelab

Unbound provides recursive DNS resolution and DNSSEC validation.

Pi-hole and Unbound run on the same LXC, but use different ports:

```text
Pi-hole / FTL
0.0.0.0:53

Unbound
127.0.0.1:5335
```

Unbound is deliberately bound to localhost so that clients cannot directly access it.

---

## Internal DNS

Internal service names are provided through Pi-hole.

Current records include:

| Hostname                     |         Address | Service             |
| ---------------------------- | --------------: | ------------------- |
| `jellyfin.robynshomelab.dev` | `192.168.20.99` | Nginx → Jellyfin    |
| `status.robynshomelab.dev`   | `192.168.20.99` | Nginx → Uptime Kuma |
| `beszel.robynshomelab.dev`   | `192.168.20.99` | Nginx → Beszel      |
| `pihole.robynshomelab.dev`   | `192.168.20.99` | Nginx → Pi-hole     |

The service hostnames resolve to Nginx rather than directly to the backend service.

For example:

```text
jellyfin.robynshomelab.dev
          │
          ▼
    192.168.20.99
       Nginx
          │
          ▼
    192.168.20.98
      Jellyfin
```

This provides a consistent HTTPS endpoint for services.

---

## HTTPS and Reverse Proxy

Nginx runs on CT 100 and acts as the central HTTPS reverse proxy.

The flow for an internal service is:

```text
Client
  │
  │ HTTPS :443
  ▼
Nginx
192.168.20.99
  │
  ├── Jellyfin → 192.168.20.98:8096
  ├── Beszel → 192.168.20.96:8090
  ├── Uptime Kuma → 192.168.20.95:3001
  └── Pi-hole → 192.168.20.99:8080
```

This means individual services do not need to expose HTTPS themselves.

TLS certificates are issued by Let's Encrypt using Cloudflare DNS-01 validation.

---

## Cloudflare and Public DNS

Cloudflare is the authoritative DNS provider for:

```text
robynshomelab.dev
```

Cloudflare is used for:

* Authoritative DNS
* Let's Encrypt DNS-01 validation
* Dynamic DNS for the home Internet connection

The internal service records are **not** published publicly to Cloudflare DNS.

For example, the following is an internal DNS record:

```text
jellyfin.robynshomelab.dev
→ 192.168.20.99
```

The private address `192.168.20.99` must not be published as a public DNS record.

---

## Dynamic DNS

The public Internet connection uses a dynamic IPv4 address.

The hostname:

```text
home.robynshomelab.dev
```

is used as the public dynamic DNS record.

The DDNS flow is:

```text
Home Internet
     │
     ▼
Public IPv4 address
     │
     ▼
ddclient
     │
     ▼
Cloudflare DNS
     │
     ▼
home.robynshomelab.dev
```

`ddclient` runs on CT 100 and periodically checks the current public IPv4 address.

If the address changes, ddclient updates the Cloudflare DNS record.

The record is DNS-only rather than proxied because it is intended to represent the home's public IP for future non-HTTP services such as game-server infrastructure.

---

## NetBird Private Remote Access

NetBird provides private remote access to the homelab.

The dedicated NetBird container is:

```text
CT 101
192.168.20.97
```

The NetBird network uses a separate overlay address space.

Current example addresses include:

```text
NetBird server:
100.113.51.59

iPhone:
100.113.124.99
```

The private-access path is:

```text
Remote device
      │
      │ NetBird
      ▼
CT 101 - NetBird
192.168.20.97
      │
      ▼
Homelab LAN
192.168.20.0/24
```

CT 101 provides access to selected internal homelab resources.

Currently this includes:

* Pi-hole
* Jellyfin
* Beszel
* Uptime Kuma

DNS traffic from the NetBird client can also be sent to Pi-hole:

```text
iPhone
  │
  │ NetBird
  ▼
NetBird routing peer
  │
  ▼
Pi-hole
192.168.20.99:53
  │
  ▼
Unbound
127.0.0.1:5335
```

This allows the phone to use the same homelab DNS while away from home.

### NetBird Role Separation

The NetBird installation on the 3060 is intended for **private homelab access**.

A separate NetBird installation is planned on the 9020/Pterodactyl VM for **service and game-server exposure**.

These roles are intentionally kept separate.

```text
3060
└── CT 101 NetBird
    └── Private homelab access


9020
└── Pterodactyl VM
    └── NetBird
        └── Service / game-server exposure
```

The two NetBird installations should not be treated as the same network function.

---

## Current Traffic Flows

### Normal Internet Access

```text
Client
  │
  ▼
ISP Router
  │
  ▼
Internet
```

### Internal DNS

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
Internet DNS hierarchy
```

### Internal HTTPS

```text
Client
  │
  │ HTTPS
  ▼
Nginx :443
  │
  ▼
Backend service
```

### Remote Private Access

```text
Remote device
  │
  │ NetBird
  ▼
CT 101
  │
  ▼
192.168.20.0/24
```

### Dynamic DNS

```text
Home public IP
  │
  ▼
ddclient
  │
  ▼
Cloudflare
  │
  ▼
home.robynshomelab.dev
```

---

## Planned Network Expansion

The current network is deliberately simple. Future infrastructure will introduce a dedicated router and managed switching.

The planned architecture is:

```text
Internet
   │
   ▼
pfSense
   │
   │ VLAN trunk
   ▼
Managed Switch
   ├── VLAN 10 - Trusted
   ├── VLAN 20 - Servers
   ├── VLAN 30 - IoT
   ├── VLAN 40 - Guest
   └── VLAN 50 - Management
```

This is **not currently deployed**.

The unmanaged switch planned for the next stage is only intended to provide additional physical Ethernet ports. It does not provide VLAN functionality.

VLAN segmentation will therefore wait until the pfSense router and managed switch are available.

---

## Planned Network Security Model

The eventual firewall policy will follow a least-privilege approach.

Initial planned rules include:

| Source  | Destination       | Planned policy |
| ------- | ----------------- | -------------- |
| Trusted | Servers           | Allow          |
| Trusted | Internet          | Allow          |
| Servers | Internet          | Allow          |
| Servers | Trusted           | Deny           |
| IoT     | Internet          | Allow          |
| IoT     | Servers           | Deny           |
| IoT     | Management        | Deny           |
| Guest   | Internet          | Allow          |
| Guest   | Internal networks | Deny           |

Specific exceptions will be added where required.

For example, clients may be permitted to reach Pi-hole for DNS even when general access to server networks is restricted.

---

## Future Physical Topology

Once the 9020 and initial switch are installed, the physical topology is expected to become:

```text
                    Internet
                       │
                       ▼
                  ISP Router
                       │
                       ▼
                 Network Switch
                   ┌────┴────┐
                   │         │
                   ▼         ▼
             OptiPlex 3060  OptiPlex 9020
               Proxmox        Proxmox
                   │             │
                   │             ├── NAS
                   │             └── Pterodactyl
                   │
                   └── Homelab services
```

This is an intermediate architecture.

The eventual network will replace the ISP router's routing function with pfSense and introduce managed VLAN switching.

---

## Key Commands

These commands were used while building and troubleshooting the network.

### `ip addr`

```bash
ip addr
```

Displays network interfaces and their assigned IP addresses.

Useful for checking whether an interface has the expected address.

---

### `ip route`

```bash
ip route
```

Displays the system's routing table.

For example, it can be used to verify the default gateway:

```text
default via 192.168.20.1
```

---

### `ip link`

```bash
ip link
```

Lists network interfaces and their link state.

This is useful for determining whether a physical or virtual network interface is available and up.

---

### `ping`

```bash
ping 192.168.20.1
```

Tests basic IP connectivity to another host.

For example, the router can be tested with:

```bash
ping 192.168.20.1
```

A successful response confirms basic Layer 3 connectivity to the gateway.

---

### `dig`

```bash
dig example.com
```

Queries DNS and displays the response in detail.

The command was particularly useful for testing the Pi-hole → Unbound chain.

For example:

```bash
dig en.wikipedia.org @127.0.0.1
```

tests the local Pi-hole DNS service.

To query Unbound directly:

```bash
dig pi-hole.net @127.0.0.1 -p 5335
```

The `@` specifies the DNS server and `-p` specifies a non-standard DNS port.

---

### `ss`

```bash
ss -tulpn
```

Displays listening TCP and UDP sockets.

This is useful when determining which service owns a particular port.

For example, it helped verify that:

```text
:53
:5335
:80
:443
```

were being used by the expected services.

---

### `tcpdump`

```bash
tcpdump -ni any port 53
```

Captures DNS traffic passing through the host.

This was useful when troubleshooting NetBird DNS.

It allowed traffic such as:

```text
100.113.124.99 → 192.168.20.99:53
```

to be observed directly.

This confirmed that DNS queries from the remote NetBird client were reaching Pi-hole.

---

### `hostnamectl`

```bash
hostnamectl
```

Displays the current hostname and system information.

The Proxmox host was renamed to:

```text
pve-1
```

using:

```bash
hostnamectl set-hostname pve-1
```

---

### Proxmox `pct`

```bash
pct list
```

Lists LXC containers running on the Proxmox host.

This is useful for checking the state of the network services hosted by Proxmox.

---

## Troubleshooting Principles

When diagnosing a network problem, the investigation should move from the lowest dependency toward the application layer.

A useful sequence is:

```text
Physical link
     ↓
Interface
     ↓
IP address
     ↓
Routing
     ↓
Connectivity
     ↓
DNS
     ↓
TCP/UDP port
     ↓
Application
```

For example, if a service cannot be reached:

1. Check the network interface.
2. Check the IP address.
3. Check the routing table.
4. Ping the destination where appropriate.
5. Check DNS resolution.
6. Check whether the destination port is listening.
7. Check the application itself.

This prevents application-level troubleshooting when the underlying network connection is the actual problem.

---

## Future Updates

This document should be updated when:

* the unmanaged switch is installed
* the Dell 9020 is connected
* the NAS is configured
* pfSense is introduced
* a managed switch is installed
* VLANs are created
* firewall policies are implemented
* the network topology changes

Planned infrastructure should remain clearly separated from deployed infrastructure.
