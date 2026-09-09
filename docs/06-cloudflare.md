# Cloudflare

Cloudflare provides authoritative DNS for the homelab's public domain, Dynamic DNS updates, and DNS-01 validation for Let's Encrypt certificates.

The domain used throughout the homelab is:

```text
robynshomelab.dev
```

Cloudflare is **not** being used as a reverse proxy for homelab traffic.

---

# Role of Cloudflare

Cloudflare currently provides three primary functions:

1. Authoritative DNS
2. Dynamic DNS
3. ACME DNS-01 validation

The architecture is intentionally DNS-only.

```text
                    Cloudflare
                        │
          ┌─────────────┼─────────────┐
          │             │             │
     Authoritative     DDNS       ACME DNS-01
        DNS                         validation
```

Cloudflare's HTTP proxy/CDN functionality is not used for the homelab's services.

---

# Authoritative DNS

Cloudflare is authoritative for:

```text
robynshomelab.dev
```

Public DNS records are managed through Cloudflare.

The homelab also uses Pi-hole for internal split-DNS records. These internal records override the corresponding public records for clients using the homelab DNS service.

---

# DNS-Only Configuration

Homelab DNS records are intentionally configured as **DNS-only**.

The traffic flow is therefore:

```text
Client
  │
  │ DNS lookup
  ▼
Cloudflare DNS
  │
  │ returns WAN address
  ▼
Client
```

Cloudflare does not sit in the HTTP traffic path.

When a client accesses a service from inside the LAN, Pi-hole provides the internal address instead.

---

# Split DNS

The homelab uses split DNS for:

```text
robynshomelab.dev
```

For example, the public DNS record for:

```text
panel.robynshomelab.dev
```

points to the home's WAN address.

Internally, Pi-hole overrides the result:

```text
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

This allows the same hostname to be used internally while keeping the public DNS record available for normal DNS and ACME purposes.

---

# Public Panel DNS

The Pterodactyl Panel has the public hostname:

```text
panel.robynshomelab.dev
```

The public Cloudflare record points to the home's WAN IP.

This record does **not** mean that the Pterodactyl Panel is directly accessible from the Internet.

There is currently no router port forwarding.

The actual service path is:

```text
Internal client
      │
      ▼
Pi-hole
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

Remote access can instead be provided through NetBird.

---

# Dynamic DNS

The homelab's WAN IP is dynamic.

Dynamic DNS is handled by `ddclient` running in CT100 alongside Pi-hole and Unbound.

```text
CT100
192.168.20.99
├── Pi-hole
├── Unbound
└── ddclient
```

ddclient updates the appropriate Cloudflare DNS record when the home's public IP changes.

This prevents the public DNS record from becoming stale after an ISP-assigned IP address changes.

---

# DDNS Architecture

The general process is:

```text
Home WAN IP
     │
     ▼
ddclient
     │
     │ Cloudflare API
     ▼
Cloudflare DNS
     │
     ▼
Updated A record
```

The DDNS service runs internally and does not require inbound access to the homelab.

---

# ACME DNS-01

Let's Encrypt certificates are issued using the ACME DNS-01 challenge.

Cloudflare provides the DNS API used to create the temporary ACME validation record.

The process is:

```text
Certbot
   │
   │ DNS-01 request
   ▼
Cloudflare API
   │
   ▼
_acme-challenge.robynshomelab.dev
   │
   ▼
Let's Encrypt
   │
   │ validation
   ▼
Certificate issued
```

This allows certificates to be issued without exposing an HTTP challenge endpoint to the Internet.

---

# Certificate Architecture

Certbot runs on CT106:

```text
Hostname: nginx
IP:       192.168.20.94
```

The current TLS architecture is:

```text
Client
  │
  │ HTTPS :443
  ▼
CT106 Nginx
  │
  │ TLS termination
  ▼
Internal service
```

Cloudflare is only involved in the DNS-01 validation process.

It is not involved in the subsequent HTTPS traffic.

---

# Current Certificates

The current certificates are managed by Certbot on CT106.

Known certificate expiry dates are:

| Certificate                  | Expiry     |
| ---------------------------- | ---------- |
| `jellyfin.robynshomelab.dev` | 2026-12-04 |
| `status.robynshomelab.dev`   | 2026-12-04 |
| `beszel.robynshomelab.dev`   | 2026-12-04 |
| `pihole.robynshomelab.dev`   | 2026-12-04 |
| `panel.robynshomelab.dev`    | 2026-12-08 |

Certbot's systemd timer is enabled for automated renewal.

A renewal dry-run has successfully completed.

---

# Cloudflare and Network Exposure

The homelab intentionally does not use Cloudflare Tunnel or Cloudflare's HTTP proxy for its current service architecture.

The design is:

```text
                     Internet
                        │
                        │ DNS only
                        ▼
                   Cloudflare
                        │
                        ▼
                    WAN IP
                        │
                  No port forward
                        │
                        X
```

Internal access instead uses:

```text
LAN / NetBird
      │
      ▼
Pi-hole split DNS
      │
      ▼
Nginx / internal service
```

This means the existence of a public DNS record does not automatically expose the corresponding service.

---

# Cloudflare API Credentials

Cloudflare API credentials are required for:

* DDNS updates
* ACME DNS-01 validation

Credentials must **never** be stored in this repository.

They should be stored only in the relevant service configuration with appropriate filesystem permissions.

The documentation should describe where credentials are used without documenting the actual tokens.

---

# Security Considerations

Cloudflare API credentials should use the minimum permissions required for their respective functions.

Where possible:

* Use scoped API tokens rather than global API keys
* Restrict tokens to the required DNS zone
* Restrict permissions to the required DNS operations
* Protect credential files with restrictive filesystem permissions
* Never commit credentials to Git
* Rotate credentials if they are accidentally exposed

---

# Troubleshooting

## Check Public DNS

From a system using an external resolver:

```bash
dig panel.robynshomelab.dev
```

This should return the configured public DNS result.

---

## Check Internal DNS

From a LAN or NetBird client using Pi-hole:

```bash
dig @192.168.20.99 panel.robynshomelab.dev
```

The expected internal result is:

```text
192.168.20.94
```

---

## Check Cloudflare Record

If a public DNS record is not updating:

1. Check the current WAN IP
2. Check the ddclient service
3. Check ddclient logs
4. Confirm Cloudflare API credentials are valid
5. Confirm the Cloudflare DNS record
6. Confirm the record is configured as DNS-only

---

## Check ddclient

From CT100:

```bash
systemctl status ddclient
```

Logs can be inspected with:

```bash
journalctl -u ddclient
```

---

# Relationship With Other Services

Cloudflare is one part of a larger DNS and HTTPS architecture:

```text
                         Cloudflare
                             │
                ┌────────────┴────────────┐
                │                         │
             Public DNS              ACME DNS-01
                │                         │
                │                         ▼
                │                     Let's Encrypt
                │                         │
                ▼                         ▼
             WAN IP                  Certbot CT106
                │                         │
                │                         ▼
                │                       Nginx
                │                         │
                └──────────────┐          │
                               │          ▼
                               │     Internal services
                               │
                               X
                         No port forwarding
                              
Internal clients
       │
       ▼
   Pi-hole
192.168.20.99
       │
       ▼
 Split DNS
       │
       ▼
Nginx / internal services
```

---

# Operational Principles

The current Cloudflare configuration follows these principles:

* Cloudflare remains authoritative for the public domain
* Public records are DNS-only
* Internal DNS is handled by Pi-hole
* DDNS is handled by ddclient
* Certificates use DNS-01 validation
* Nginx handles HTTPS termination
* Cloudflare does not proxy service traffic
* No router port forwarding is required for the current architecture
* API credentials are kept out of the Git repository

Any future change to the Cloudflare architecture should be reflected here and in the network documentation.
