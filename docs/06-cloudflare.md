# Cloudflare and DNS

## Overview

Cloudflare provides the public DNS infrastructure for the homelab domain:

```text
robynshomelab.dev
```

The domain was purchased through Porkbun, while Cloudflare is used as the authoritative DNS provider.

Cloudflare currently provides two main functions for the homelab:

* Authoritative public DNS
* DNS-01 validation for Let's Encrypt TLS certificates

Cloudflare is **not** currently being used as a reverse proxy for the homelab services.

---

## Domain

The homelab domain is:

```text
robynshomelab.dev
```

The domain registrar is Porkbun.

Cloudflare was configured as the authoritative DNS provider by changing the domain's nameservers at Porkbun to:

```text
coby.ns.cloudflare.com
jamie.ns.cloudflare.com
```

This means DNS queries for `robynshomelab.dev` are ultimately delegated to Cloudflare's nameservers.

The registrar and DNS provider therefore have separate responsibilities:

```text
Porkbun
  │
  └── Domain registration

Cloudflare
  │
  └── Authoritative DNS
```

---

## DNS Architecture

The homelab uses different DNS paths depending on where the request originates.

### Internal clients

Internal clients use Pi-hole:

```text
Client
   │
   │ DNS :53
   ▼
Pi-hole
192.168.20.99
   │
   ▼
Unbound
127.0.0.1:5335
   │
   ▼
DNS hierarchy
```

Pi-hole provides the internal DNS records for homelab services.

For example:

```text
jellyfin.robynshomelab.dev → 192.168.20.99
status.robynshomelab.dev   → 192.168.20.99
beszel.robynshomelab.dev   → 192.168.20.99
pihole.robynshomelab.dev   → 192.168.20.99
```

These records exist inside Pi-hole and are **not published to Cloudflare's public DNS**.

---

## Public DNS

Cloudflare hosts the public DNS zone for:

```text
robynshomelab.dev
```

Only records that are intentionally public should be placed in this zone.

The homelab does **not** publish private RFC1918 addresses such as:

```text
192.168.20.x
```

to public DNS.

This prevents external users from learning or attempting to access internal addresses that are not publicly routable.

---

## Internal and Public DNS Separation

The same hostname can therefore have different behaviour depending on where the DNS request originates.

For example:

```text
Internal client
     │
     ▼
Pi-hole
     │
     └── jellyfin.robynshomelab.dev
                 ↓
          192.168.20.99


Public DNS query
     │
     ▼
Cloudflare
     │
     └── No public Jellyfin record
```

This is intentional.

The internal service names are primarily used for convenient HTTPS access inside the homelab.

---

# Cloudflare DDNS

Cloudflare also hosts the public DNS record used for dynamic DNS.

The record is:

```text
home.robynshomelab.dev
```

It is an IPv4 `A` record.

Its purpose is to provide a stable hostname for the home's changing public IPv4 address.

The architecture is:

```text
Home Internet
     │
     ▼
Public IPv4
     │
     ▼
Cloudflare DNS
     │
     └── home.robynshomelab.dev
```

The record is configured as:

```text
Type: A
Name: home
Proxy: DNS only
TTL: Auto
```

---

## Why the DDNS Record Is DNS Only

The `home` record is intentionally **not proxied** through Cloudflare.

It uses Cloudflare's DNS service only:

```text
DNS only
```

rather than:

```text
Proxied
```

This is important because the hostname is intended to represent the home's public IP for future services that may not use HTTP/HTTPS.

Cloudflare's normal orange-cloud proxy is designed primarily for supported web traffic.

For future game servers and other arbitrary network services, the DNS-only record is therefore the appropriate configuration.

---

## DDNS Client

DDNS is handled by `ddclient` inside CT 100.

```text
CT 100
pihole-nginx
192.168.20.99
```

The decision to run DDNS here avoids creating another container solely for a small background service.

CT 100 is already intended to be an always-running infrastructure container and already has the required Cloudflare tooling.

The architecture is:

```text
CT 100
 │
 ├── Pi-hole
 ├── Unbound
 ├── Nginx
 └── ddclient
        │
        ▼
    Cloudflare
```

---

## DDNS Update Process

`ddclient` periodically determines the home's public IPv4 address and updates the Cloudflare `home` record when necessary.

The current configuration checks every five minutes.

The relevant setting is:

```text
daemon_interval="5m"
```

The DDNS service is enabled at boot.

The configuration is stored in:

```text
/etc/ddclient.conf
```

The file contains the Cloudflare API credential and must remain protected.

Its permissions are:

```text
-rw------- 1 root root
```

The credential must **never** be committed to Git.

---

## Cloudflare API Token

A dedicated Cloudflare API token was created specifically for DDNS.

The token is restricted to:

```text
Zone → DNS → Edit
```

and is limited to the:

```text
robynshomelab.dev
```

zone.

The token is separate from the Cloudflare API token used for Let's Encrypt DNS-01 validation.

This separation follows the principle of least privilege:

```text
DDNS token
    ↓
DNS editing only
    ↓
robynshomelab.dev


ACME token
    ↓
DNS editing for certificate validation
    ↓
robynshomelab.dev
```

The actual token value is intentionally **not documented in Git**.

---

## DDNS Testing

The current public IPv4 address can be checked with:

```bash
curl -4 https://icanhazip.com
```

The Cloudflare DNS record can then be checked with:

```bash
dig +short home.robynshomelab.dev
```

The two addresses should match.

A successful manual `ddclient` test was performed with:

```bash
ddclient -daemon=0 -verbose
```

The update completed successfully.

---

# Let's Encrypt DNS-01

Cloudflare is also used for automated Let's Encrypt certificate validation.

The ACME validation method is:

```text
DNS-01
```

This allows Let's Encrypt to verify control of the domain by checking a temporary DNS TXT record.

The process is approximately:

```text
Certbot
   │
   ▼
Cloudflare API
   │
   ▼
_acme-challenge.robynshomelab.dev
   │
   ▼
Let's Encrypt
   │
   ▼
Certificate issued
```

This is particularly useful for the homelab because the internal services do not need to be publicly accessible for certificate validation.

---

## ACME API Token

A separate Cloudflare API token is used for certificate issuance.

It is stored only on CT 100:

```text
/root/.secrets/certbot/cloudflare.ini
```

The file contains the Cloudflare API token required by the Certbot Cloudflare DNS plugin.

The file is:

* Root owned
* Restricted to mode `600`
* Excluded from Git

The credential must never be copied into the homelab repository.

---

## TLS Certificates

The following certificates have been issued:

```text
jellyfin.robynshomelab.dev
status.robynshomelab.dev
beszel.robynshomelab.dev
pihole.robynshomelab.dev
```

They are used by Nginx to provide HTTPS access to the corresponding internal services.

The current certificate architecture is:

```text
Client
  │
  │ HTTPS
  ▼
Nginx :443
  │
  ├── jellyfin.robynshomelab.dev → Jellyfin
  ├── status.robynshomelab.dev   → Uptime Kuma
  ├── beszel.robynshomelab.dev   → Beszel
  └── pihole.robynshomelab.dev   → Pi-hole
```

---

## Why DNS-01 Was Chosen

DNS-01 validation has several advantages for this homelab.

Most importantly, the services do not need to be exposed publicly to obtain valid certificates.

The validation occurs through Cloudflare DNS instead:

```text
Let's Encrypt
      │
      ▼
Cloudflare DNS
      │
      ▼
TXT challenge
      │
      ▼
Domain ownership verified
```

This fits the homelab's security model because Nginx can remain reachable only from the intended network paths.

---

## Certificate Renewal

Let's Encrypt certificates have a limited validity period and must be renewed periodically.

Certbot's systemd timers handle renewal automatically.

The renewal process can be checked with:

```bash
systemctl list-timers | grep certbot
```

A dry-run renewal test can be performed with:

```bash
certbot renew --dry-run
```

The dry run should be used before making significant changes to the Cloudflare or Certbot configuration.

---

# Cloudflare and Reverse Proxy

Cloudflare is **not currently sitting in front of Nginx**.

The current HTTPS architecture is:

```text
Client
   │
   ▼
Pi-hole
   │
   ▼
192.168.20.99
   │
   ▼
Nginx :443
   │
   ├── Jellyfin
   ├── Uptime Kuma
   ├── Beszel
   └── Pi-hole
```

Cloudflare's role is currently limited to:

* Authoritative public DNS
* DDNS
* ACME DNS-01 validation

Nginx handles the actual HTTPS reverse proxying.

---

# Security Considerations

### Never publish private addresses

Addresses such as:

```text
192.168.20.95
192.168.20.96
192.168.20.97
192.168.20.98
192.168.20.99
192.168.20.100
```

are internal network addresses.

They should not be placed in the public Cloudflare DNS zone.

---

### Protect API tokens

Cloudflare API tokens provide access to DNS resources and must be treated as secrets.

They should:

* Never be committed to Git
* Never be pasted into public documentation
* Have the minimum permissions required
* Be stored in root-readable configuration files
* Be separated by function where practical

---

### Do not use the global Cloudflare API key

The homelab uses scoped API tokens rather than Cloudflare's global API key.

This limits the impact if a credential is accidentally compromised.

---

# Current Cloudflare Architecture

The current design can be summarised as:

```text
                     Internet
                        │
                        ▼
                 Cloudflare DNS
                        │
             ┌──────────┴──────────┐
             │                     │
      home.robynshomelab.dev   ACME DNS-01
             │                     │
             ▼                     ▼
        Home public IP        Let's Encrypt
                                  │
                                  ▼
                              Certificates


Internal network
       │
       ▼
    Pi-hole
       │
       ├── Internal DNS records
       │
       ▼
    Unbound
       │
       ▼
 DNS hierarchy
```

Cloudflare therefore provides the public DNS control plane, while Pi-hole and Unbound provide the actual internal DNS infrastructure.

---

# Key Commands

| Command                                     | Purpose                                   |
| ------------------------------------------- | ----------------------------------------- |
| `dig +short home.robynshomelab.dev`         | Check the public DDNS record              |
| `curl -4 https://icanhazip.com`             | Determine the current public IPv4 address |
| `ddclient -daemon=0 -verbose`               | Run a manual DDNS update/test             |
| `systemctl status ddclient`                 | Check the DDNS service                    |
| `systemctl is-enabled ddclient`             | Check whether DDNS starts at boot         |
| `systemctl list-timers \| grep certbot`     | Check Certbot renewal timers              |
| `certbot renew --dry-run`                   | Test certificate renewal                  |
| `dig TXT _acme-challenge.robynshomelab.dev` | Inspect an ACME DNS challenge             |

---

# Future Updates

This document should be updated when:

* Cloudflare DNS records change
* Additional public DNS records are created
* DDNS configuration changes
* Cloudflare API token permissions change
* Additional certificates are issued
* Certificate renewal architecture changes
* Cloudflare proxying is introduced
* Public services are exposed
* The domain registrar changes
* DNS architecture changes
