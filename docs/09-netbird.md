# NetBird

NetBird provides private network connectivity to the homelab without requiring router port forwarding.

The current deployment uses two independent NetBird peers:

* CT101 as the LAN routing peer
* VM108 as an independent NetBird peer

---

# Architecture

```text
                         NetBird Network
                              │
                 ┌────────────┴────────────┐
                 │                         │
          Remote Clients              VM108 Peer
                 │                  100.113.229.169
                 │                         │
                 ▼                         ▼
              CT101                 Pterodactyl
          192.168.20.97             192.168.20.111
                 │
                 │ LAN routes
          ┌──────┴──────┐
          │             │
          ▼             ▼
     192.168.20.94  192.168.20.99
        Nginx          Pi-hole
```

CT101 provides access to selected LAN addresses.

VM108 has its own NetBird installation and does not depend on CT101 for NetBird connectivity.

---

# CT101 Routing Peer

```text
VMID:     101
Hostname: netbird
IP:       192.168.20.97
```

CT101 acts as the NetBird routing peer for selected homelab services.

Current NetBird version:

```text
0.78.1
```

Current NetBird virtual IP:

```text
100.113.51.59/16
```

---

# LAN Routes

CT101 currently advertises the following routes:

```text
192.168.20.94/32
192.168.20.99/32
```

These provide NetBird clients with access to:

```text
192.168.20.94
    Nginx

192.168.20.99
    Pi-hole / Unbound / DNS
```

The use of `/32` routes intentionally limits NetBird access to the required hosts rather than exposing the entire LAN subnet.

---

# Nginx Access

Remote NetBird clients can access the Nginx reverse proxy through:

```text
192.168.20.94
```

The path is:

```text
Remote NetBird client
        │
        ▼
NetBird
        │
        ▼
CT101
100.113.51.59
        │
        ▼
192.168.20.94
        │
        ▼
Nginx
        │
        ▼
Internal service
```

This allows remote clients to use the same HTTPS hostnames used by LAN clients.

---

# DNS

Pi-hole is available to NetBird clients at:

```text
192.168.20.99:53
```

NetBird's global/default nameserver is configured as:

```text
192.168.20.99:53
```

for:

```text
.
```

This causes NetBird clients to use the homelab Pi-hole DNS infrastructure.

The DNS path is:

```text
NetBird client
      │
      ▼
CT101 routing
      │
      ▼
Pi-hole
192.168.20.99:53
      │
      ▼
Unbound
      │
      ▼
Recursive DNS
```

---

# Split DNS

Because NetBird clients use Pi-hole, they receive the same internal DNS records as LAN clients.

For example:

```text
panel.robynshomelab.dev
        │
        ▼
192.168.20.94
```

This allows a remote NetBird client to access:

```text
https://panel.robynshomelab.dev
```

using the same hostname as an internal LAN client.

---

# VM108 NetBird Peer

VM108 runs its own independent NetBird installation.

```text
VMID:     108
Hostname: pterodactyl
IP:       192.168.20.111
```

NetBird version:

```text
0.78.1
```

NetBird virtual IP:

```text
100.113.229.169/16
```

NetBird FQDN:

```text
pterodactyl.netbird.cloud
```

VM108 is therefore independently reachable over the NetBird network.

---

# Independent Peer Design

VM108 does **not** use CT101 as its NetBird peer.

The architecture is:

```text
NetBird
   │
   ├───────────────┐
   │               │
   ▼               ▼
 CT101           VM108
   │               │
   ▼               ▼
 LAN routes     Pterodactyl
```

CT101 and VM108 are separate NetBird peers.

This distinction is important when troubleshooting connectivity.

---

# Pterodactyl Access

The Pterodactyl Panel is accessed internally through Nginx:

```text
NetBird client
      │
      ▼
CT101
      │
      ▼
192.168.20.94
      │
      ▼
Nginx
      │
      ▼
192.168.20.111:80
      │
      ▼
Pterodactyl Panel
```

The VM108 NetBird peer also provides a direct private path to VM108 itself.

The two paths serve different purposes:

```text
CT101 route
    → Nginx
    → Panel hostname / HTTPS

VM108 NetBird peer
    → VM108 itself
```

---

# Network Security Model

NetBird is used as the remote-access layer instead of exposing homelab services directly to the Internet.

The current design intentionally has:

```text
No router port forwarding
```

Remote access is instead:

```text
Remote device
      │
      ▼
NetBird
      │
      ├── CT101 → selected LAN services
      │
      └── VM108 → Pterodactyl host
```

This limits direct Internet exposure.

---

# Current NetBird Addressing

| Device | LAN IP           | NetBird IP        | Role             |
| ------ | ---------------- | ----------------- | ---------------- |
| CT101  | `192.168.20.97`  | `100.113.51.59`   | LAN routing peer |
| VM108  | `192.168.20.111` | `100.113.229.169` | Independent peer |

---

# Troubleshooting

## Check NetBird Status

On CT101:

```bash
netbird status
```

On VM108:

```bash
netbird status
```

Both peers should report an active connection.

---

## Check NetBird Version

```bash
netbird version
```

The current deployed version is:

```text
0.78.1
```

---

## Test CT101 Routes

From a NetBird client, test:

```bash
ping 192.168.20.94
```

and:

```bash
ping 192.168.20.99
```

If these fail, investigate CT101 routing before troubleshooting the destination services.

---

## Test DNS

From a NetBird client:

```bash
dig @192.168.20.99 example.com
```

For an internal hostname:

```bash
dig @192.168.20.99 panel.robynshomelab.dev
```

The internal result should be:

```text
192.168.20.94
```

---

## Test HTTPS

From a NetBird client:

```bash
curl -I https://panel.robynshomelab.dev
```

The request should resolve through Pi-hole to Nginx and then be proxied to VM108.

---

# Troubleshooting Path

When a NetBird client cannot access a homelab service, determine which path is failing.

```text
NetBird client
      │
      ▼
NetBird connection
      │
      ▼
Routing peer
      │
      ▼
LAN route
      │
      ▼
Destination host
      │
      ▼
Service
```

For DNS-related failures:

```text
NetBird client
      │
      ▼
Pi-hole
      │
      ▼
Unbound / local DNS
```

For Pterodactyl Panel access:

```text
NetBird client
      │
      ▼
CT101
      │
      ▼
192.168.20.94
      │
      ▼
Nginx
      │
      ▼
192.168.20.111:80
```

For direct VM108 NetBird access:

```text
NetBird client
      │
      ▼
VM108
100.113.229.169
```

---

# Known Previous Test

A previous NetBird managed Reverse Proxy test was performed for Pterodactyl/Minecraft TCP traffic.

The test successfully established public connectivity to the temporary endpoint, but the traffic did not reach VM108 as expected.

Troubleshooting of this test was paused.

This should not be treated as part of the current production access architecture.

The current documented design is based on:

* CT101 LAN routing
* VM108's independent NetBird peer
* Nginx reverse proxy
* No router port forwarding

---

# Operational Principles

The current NetBird deployment follows these principles:

* CT101 provides selected LAN routes
* LAN routes use `/32` addresses where practical
* Pi-hole provides DNS to NetBird clients
* CT101 routes access to Nginx and Pi-hole
* VM108 operates as an independent NetBird peer
* NetBird provides remote private access
* Router port forwarding is not required
* Public reverse-proxy experiments are not part of the production architecture

---

# Future Improvements

Potential future improvements include:

* Additional routed services
* More granular NetBird access policies
* Monitoring of NetBird peer health
* Documented peer groups and ACLs
* Additional independent peers where useful
* Improved redundancy for remote access

Any additional route or peer should be documented here after it has been deployed and tested.
