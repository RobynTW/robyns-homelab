# Pi-hole

Pi-hole provides the homelab's primary DNS service, local DNS records, and network-wide DNS filtering.

Pi-hole runs in CT100 and works together with Unbound for recursive DNS resolution.

---

## Container

```text id="p8m2xj"
VMID:     100
Hostname: pihole
IP:       192.168.20.99
Host:      pve-1
```

CT100 also runs:

* Unbound
* ddclient

Pi-hole is therefore the primary DNS endpoint for the homelab.

---

# DNS Architecture

The normal DNS path is:

```text id="1n4y8q"
Client
  │
  │ DNS :53
  ▼
Pi-hole
192.168.20.99
  │
  ▼
Unbound
  │
  ▼
DNS hierarchy
```

Pi-hole handles filtering and local DNS records.

Unbound handles recursive DNS resolution.

---

# Pi-hole Configuration

Pi-hole listens on:

```text id="0w8v7p"
192.168.20.99:53
```

This address is used by:

* LAN clients
* NetBird clients
* Homelab services requiring DNS

NetBird is configured to use:

```text id="3b2k6s"
192.168.20.99:53
```

as its DNS server.

---

# Local DNS

Pi-hole provides split-DNS records for the homelab's web services.

The following hostnames resolve internally to the Nginx reverse proxy:

```text id="v7q2me"
panel.robynshomelab.dev
    → 192.168.20.94

jellyfin.robynshomelab.dev
    → 192.168.20.94

status.robynshomelab.dev
    → 192.168.20.94

beszel.robynshomelab.dev
    → 192.168.20.94

pihole.robynshomelab.dev
    → 192.168.20.94
```

The Wings hostname is directed directly to the Pterodactyl VM:

```text id="a3k7wp"
wings.robynshomelab.dev
    → 192.168.20.111
```

This allows internal clients to use the same service hostnames without requiring services to be directly exposed.

---

# Split DNS and Cloudflare

Cloudflare is authoritative for:

```text id="j3c9mv"
robynshomelab.dev
```

The public Cloudflare records and internal Pi-hole records serve different purposes.

For example:

```text id="0f8r1c"
Public DNS:

panel.robynshomelab.dev
        │
        ▼
WAN IP
```

while internal DNS returns:

```text id="2m6v4s"
Internal DNS:

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

The public Panel record exists for DNS and ACME purposes and does not provide direct public access because there is no router port forwarding.

---

# Pi-hole Web Interface

The Pi-hole web interface is available internally through:

```text id="6g0v1a"
pihole.robynshomelab.dev
```

The hostname resolves to Nginx:

```text id="4q9x7j"
192.168.20.94
```

Nginx then proxies the request to the Pi-hole web interface on:

```text id="5c2n8h"
192.168.20.99:8080
```

This provides HTTPS access through the same reverse-proxy architecture used by the other homelab web services.

---

# Nginx Separation

Historically, Nginx and Certbot were hosted alongside Pi-hole in CT100.

This is no longer the architecture.

The current separation is:

```text id="3w7f9p"
CT100
192.168.20.99
├── Pi-hole
├── Unbound
└── ddclient

CT106
192.168.20.94
├── Nginx
└── Certbot
```

This keeps DNS infrastructure separate from the reverse-proxy and TLS infrastructure.

---

# Unbound Integration

Unbound provides recursive DNS resolution behind Pi-hole.

The relationship is:

```text id="5s1k8n"
Client
   │
   ▼
Pi-hole :53
   │
   │ filtered / local DNS
   ▼
Unbound
   │
   │ recursive resolution
   ▼
Authoritative DNS servers
```

Pi-hole therefore remains the single DNS endpoint exposed to clients.

Unbound is not intended to replace Pi-hole as the client-facing DNS server.

---

# DNS Security

The DNS architecture provides several useful security and privacy properties:

* Network-wide DNS filtering through Pi-hole
* Local DNS control
* Recursive resolution through Unbound
* DNSSEC validation through Unbound
* Centralised DNS for NetBird clients
* No requirement to expose Pi-hole directly to the Internet

Pi-hole's administrative interface should remain accessible only through trusted network paths.

---

# Remote DNS Access

NetBird clients can use the homelab DNS service through CT101.

The current path is:

```text id="8w3j4n"
NetBird Client
      │
      ▼
CT101
100.113.51.59
      │
      │ route 192.168.20.99/32
      ▼
Pi-hole
192.168.20.99:53
      │
      ▼
Unbound
```

This allows remote NetBird-connected devices to receive the same DNS filtering and local hostname resolution used on the LAN.

---

# Troubleshooting

## Check Pi-hole DNS

From a client on the LAN:

```bash
dig @192.168.20.99 example.com
```

A successful response confirms that Pi-hole is responding to DNS queries.

---

## Check Local DNS

Test an internal hostname:

```bash
dig @192.168.20.99 panel.robynshomelab.dev
```

The expected internal answer is:

```text
192.168.20.94
```

---

## Check Pi-hole Service

From CT100:

```bash
systemctl status pihole-FTL
```

---

## Check DNS Port

From another LAN system:

```bash
ss -lntup | grep ':53'
```

Pi-hole should be listening for DNS traffic on port 53.

---

# Operational Notes

Pi-hole is a critical infrastructure service.

If Pi-hole becomes unavailable:

* Normal DNS resolution may fail
* Internal service hostnames will stop resolving
* NetBird DNS resolution may fail
* Access to services by hostname may become unavailable

The direct IP addresses of services can still be used for troubleshooting where appropriate.

For example:

```text
Nginx:      192.168.20.94
Jellyfin:   192.168.20.98
Pterodactyl:192.168.20.111
```

---

# Future Improvements

Potential future improvements include:

* DNS redundancy
* Secondary Pi-hole
* Improved monitoring of DNS availability
* Dedicated DNS/network VLAN
* More comprehensive backup of Pi-hole configuration

These should only be documented as deployed after implementation and testing.
