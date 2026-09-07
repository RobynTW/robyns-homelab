# NetBird Private Network Access

## Overview

NetBird provides private remote access to the homelab without exposing internal services directly to the public internet.

NetBird currently runs in a dedicated Proxmox LXC:

```text
Proxmox pve-1
└── CT101
    ├── Hostname: netbird
    ├── LAN IP: 192.168.20.97
    └── NetBird IP: 100.113.51.59
```

The container acts as a **routing peer** for the homelab.

Its current purpose is deliberately limited to:

* private access to homelab services
* routing traffic between NetBird clients and the LAN
* providing Pi-hole DNS to NetBird clients

It is **not** currently used for public service or game-server exposure.

## Network Details

| Component       | Address            |
| --------------- | ------------------ |
| NetBird LXC     | `192.168.20.97`    |
| NetBird address | `100.113.51.59/16` |
| Pi-hole         | `192.168.20.99`    |
| Proxmox         | `192.168.20.100`   |
| Jellyfin        | `192.168.20.98`    |
| Nginx           | `192.168.20.94`    |

The NetBird container is connected to the normal homelab LAN and participates in the NetBird overlay network.

## NetBird Addressing

NetBird assigns overlay addresses from:

```text
100.113.0.0/16
```

The current NetBird address of CT101 is:

```text
100.113.51.59
```

The iPhone currently has:

```text
100.113.124.99
```

These addresses are separate from the physical LAN addresses in `192.168.20.0/24`.

Conceptually:

```text
                 NetBird overlay
             100.113.0.0/16
                    │
        ┌───────────┴───────────┐
        │                       │
   iPhone                    CT101
100.113.124.99          100.113.51.59
                                │
                                │ routing
                                ▼
                         Homelab LAN
                        192.168.20.0/24
```

## Routing Peer

CT101 operates as a NetBird routing peer.

This allows NetBird clients to reach resources on the physical homelab LAN that do not themselves run NetBird.

For example:

```text
iPhone
  │
  │ NetBird
  ▼
CT101
192.168.20.97
  │
  │ LAN routing
  ▼
Pi-hole
192.168.20.99
```

This is particularly useful for accessing infrastructure services without installing NetBird on every individual service.

## Current Routed Resource

The current routed resource is:

```text
192.168.20.99
```

This is the Pi-hole server.

The resource allows remote NetBird clients to communicate with Pi-hole across the NetBird routing peer.

## Masquerading

Masquerading is enabled for the routed traffic.

This allows traffic arriving through the NetBird routing peer to be translated appropriately when communicating with the LAN.

The effective flow is:

```text
NetBird client
      │
      ▼
100.113.51.59
      │
      │ masqueraded/routed
      ▼
192.168.20.99
```

Masquerading is useful here because the LAN does not currently have a dedicated route back to the NetBird overlay network.

A future firewall/router deployment may allow this architecture to be refined.

## DNS

Pi-hole provides DNS for NetBird clients.

The configured DNS server is:

```text
192.168.20.99
```

DNS requests therefore follow:

```text
NetBird client
     │
     ▼
CT101 / NetBird
     │
     ▼
Pi-hole
192.168.20.99:53
     │
     ▼
Unbound
127.0.0.1:5335
```

This allows remote clients to use the same DNS infrastructure as local homelab clients.

## Internal DNS

Pi-hole also provides internal DNS records for the homelab services.

Current records include:

```text
jellyfin.robynshomelab.dev → 192.168.20.94
status.robynshomelab.dev   → 192.168.20.94
beszel.robynshomelab.dev   → 192.168.20.94
pihole.robynshomelab.dev   → 192.168.20.94
```

When connected to NetBird, a client can therefore use the same service hostnames as a device physically connected to the LAN.

## NetBird Policies

NetBird access policies restrict what connected peers can access.

The current configuration permits the required DNS traffic to Pi-hole:

```text
Pi-hole
192.168.20.99
TCP/53
UDP/53
```

TCP port 8080 is also permitted where required for Pi-hole web access.

The intention is to avoid giving remote NetBird clients unrestricted access to the entire `192.168.20.0/24` network.

Access should be granted only to services that actually need to be reachable remotely.

## Remote Client

An iPhone is currently enrolled as a NetBird peer.

Current overlay address:

```text
100.113.124.99
```

The iPhone connects to the homelab through a NetBird relay.

Despite the relay connection, normal internet access remains functional.

Traffic destined for homelab resources is routed through NetBird, while normal internet traffic continues through the phone's regular internet connection.

Conceptually:

```text
                    iPhone
               100.113.124.99
                      │
               NetBird overlay
                      │
                      ▼
                   CT101
              100.113.51.59
                      │
                 LAN routing
                      │
                      ▼
                Homelab LAN
```

## DNS Verification

DNS traffic from the iPhone was verified with packet capture on Pi-hole.

Example:

```bash
tcpdump -ni any port 53
```

This confirmed that DNS requests originating from the remote NetBird client reach Pi-hole.

This is an important verification because it confirms that the NetBird routing, policy, and DNS configuration are functioning together rather than merely showing the peer as connected.

## Connectivity Testing

Check the NetBird service:

```bash
systemctl status netbird
```

Check the NetBird version:

```bash
netbird version
```

Check peer status:

```bash
netbird status
```

The status output can be used to confirm:

* whether the daemon is connected
* the assigned NetBird address
* connected peers
* connection type
* relay/direct connectivity

## Routing Verification

Check the routing table:

```bash
ip route
```

Check the network interfaces:

```bash
ip addr
```

The NetBird interface should be visible alongside the normal LAN interface.

## DNS Testing

From a NetBird client, test Pi-hole directly:

```bash
dig google.com @192.168.20.99
```

Test an internal homelab hostname:

```bash
dig jellyfin.robynshomelab.dev @192.168.20.99
```

The internal hostname should resolve to:

```text
192.168.20.94
```

This confirms that the remote client can use Pi-hole's local DNS configuration.

## Service Testing

After confirming routing and DNS, test the reverse-proxied services:

```bash
curl -I https://jellyfin.robynshomelab.dev
curl -I https://status.robynshomelab.dev
curl -I https://beszel.robynshomelab.dev
curl -I https://pihole.robynshomelab.dev
```

These hostnames should resolve through Pi-hole and reach Nginx at:

```text
192.168.20.94
```

The resulting traffic path is:

```text
Remote client
     │
     ▼
NetBird
     │
     ▼
CT101
     │
     ▼
Pi-hole DNS
     │
     ▼
192.168.20.94
     │
     ▼
Nginx
     │
     ├── Jellyfin
     ├── Uptime Kuma
     ├── Beszel
     └── Pi-hole
```

## Firewall Considerations

The current ISP router is responsible for the basic LAN network.

A dedicated firewall/router has not yet been deployed.

The future network design is expected to use pfSense with VLANs:

```text
Internet
    │
    ▼
pfSense
    │
    ▼
Managed switch
    ├── VLAN 10 Trusted
    ├── VLAN 20 Servers
    ├── VLAN 30 IoT
    ├── VLAN 40 Guest
    └── VLAN 50 Management
```

At that point, NetBird access can be integrated with more granular firewall rules.

The current NetBird routing design should therefore be considered the initial homelab implementation rather than the final network-security architecture.

## Security Model

The homelab does not use router port forwarding for private NetBird access.

Instead:

```text
Internet
   │
   │ encrypted NetBird connection
   ▼
NetBird overlay
   │
   ▼
CT101
   │
   ▼
Homelab LAN
```

This keeps internal services inaccessible from the public internet unless they are deliberately exposed through a separate mechanism.

NetBird policies should remain restrictive.

Avoid creating broad rules such as unrestricted access from every NetBird peer to the entire LAN unless there is a specific requirement.

## Separation From Future Game Services

NetBird CT101 is **not** intended to become the gateway for the future Pterodactyl installation.

The planned Pterodactyl server will run on the Dell OptiPlex 9020.

The future architecture is:

```text
9020
└── Debian VM
    ├── Pterodactyl Panel
    ├── Wings
    └── NetBird
        └── Reverse Proxy
```

That NetBird instance will have a separate purpose from CT101.

CT101:

```text
Private homelab access
```

9020 VM:

```text
Game/service exposure to selected friends
```

Keeping these roles separate prevents the private infrastructure access gateway from becoming coupled to publicly reachable game services.

## No Router Port Forwarding

The current NetBird deployment does not require port forwarding on the ISP router.

This is intentional.

The homelab should not expose:

```text
192.168.20.94
192.168.20.95
192.168.20.96
192.168.20.97
192.168.20.98
192.168.20.99
192.168.20.100
```

directly to the public internet.

Public DNS should also never contain these private addresses.

## Troubleshooting

### NetBird is disconnected

Check:

```bash
systemctl status netbird
```

Then:

```bash
netbird status
```

Check recent logs:

```bash
journalctl -u netbird --no-pager
```

### Peer is connected but LAN resources are unreachable

Check:

```bash
ip route
```

Then verify the routing peer configuration in the NetBird management interface.

Confirm that the relevant resource includes:

```text
192.168.20.99
```

and that masquerading is enabled where required.

### DNS does not work remotely

Test Pi-hole directly:

```bash
dig google.com @192.168.20.99
```

If that fails, check whether the NetBird client can reach Pi-hole at all.

On Pi-hole, inspect DNS traffic:

```bash
tcpdump -ni any port 53
```

If no traffic appears, investigate NetBird routing or policy configuration.

### Internal hostnames do not resolve

Test:

```bash
dig jellyfin.robynshomelab.dev @192.168.20.99
```

Expected result:

```text
192.168.20.94
```

If Pi-hole returns the correct address but the service is inaccessible, the problem is likely routing, policy, Nginx, or the backend service rather than DNS.

### Internet access stops on the remote client

The current configuration is intended to route homelab traffic through NetBird while leaving normal internet traffic on the client's normal connection.

If all internet traffic begins routing through the homelab, check the NetBird routing and DNS configuration for unintended default-route behaviour.

## Key Commands

| Command                                         | Purpose                               |
| ----------------------------------------------- | ------------------------------------- |
| `systemctl status netbird`                      | Check the NetBird service             |
| `systemctl restart netbird`                     | Restart the NetBird service           |
| `netbird status`                                | Show peer and connection status       |
| `netbird version`                               | Show installed NetBird version        |
| `ip addr`                                       | Show network interfaces and addresses |
| `ip route`                                      | Show routing table                    |
| `dig google.com @192.168.20.99`                 | Test remote access to Pi-hole DNS     |
| `dig jellyfin.robynshomelab.dev @192.168.20.99` | Test internal DNS resolution          |
| `tcpdump -ni any port 53`                       | Monitor DNS traffic                   |
| `journalctl -u netbird --no-pager`              | View NetBird service logs             |

## Current State

NetBird private access is operational.

Current topology:

```text
                           NetBird
                       100.113.0.0/16
                              │
                 ┌────────────┴────────────┐
                 │                         │
              iPhone                    CT101
         100.113.124.99             100.113.51.59
                                           │
                                           │ routing
                                           ▼
                                  Homelab LAN
                                  192.168.20.0/24
                                           │
                                           ▼
                                     Pi-hole
                                  192.168.20.99
                                           │
                                           ▼
                                      Unbound
                                  127.0.0.1:5335
```

The iPhone has successfully connected through a NetBird relay, reached Pi-hole, and generated DNS traffic visible on the Pi-hole host.

NetBird is currently used exclusively for private homelab access.

The future Pterodactyl/9020 NetBird deployment will be separate.

