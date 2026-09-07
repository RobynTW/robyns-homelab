# Cloudflare DDNS

## Overview

Dynamic DNS (DDNS) automatically updates a DNS record when the public IP address assigned to the home network changes.

This homelab uses Cloudflare DNS as the authoritative DNS provider for `robynshomelab.dev`. The hostname:

```text
home.robynshomelab.dev
```

is used as the dynamic DNS hostname for the home network.

The DDNS updater runs on CT 100 (`pihole-nginx`) using `ddclient`.

---

## Why DDNS Is Needed

Residential internet connections may receive a public IPv4 address that can change over time.

Without DDNS, a service configured to use the home's public IP would stop being reachable when the ISP changes that address.

DDNS provides a stable hostname:

```text
home.robynshomelab.dev
        │
        ▼
current public IPv4 address
```

When the public IP changes, `ddclient` detects the new address and updates the Cloudflare DNS record.

---

## Architecture

```text
                 Internet
                    │
                    ▼
                ISP Router
                    │
             Public IPv4 address
                    │
                    │
             ┌──────▼──────┐
             │  Cloudflare │
             │     DNS     │
             └──────┬──────┘
                    │
                    ▼
        home.robynshomelab.dev
                    │
                    ▼
             Current public IP


CT 100
┌──────────────────────────────┐
│ pihole-nginx                 │
│                              │
│ ddclient                     │
│   │                          │
│   ├── discovers public IP    │
│   │   using ipify            │
│   │                          │
│   └── updates Cloudflare     │
│       using API token        │
└──────────────────────────────┘
```

DDNS only maintains the DNS record. It does not create firewall rules, port forwards, or network access to internal services.

---

## Hostname

The DDNS hostname is:

```text
home.robynshomelab.dev
```

The Cloudflare record is an IPv4 `A` record.

The record is configured as:

```text
Type:    A
Name:    home
Target:  current public IPv4 address
Proxy:   DNS only
TTL:     Auto
```

---

## Why DNS Only Is Used

The `home.robynshomelab.dev` record is configured as **DNS only** rather than proxied through Cloudflare.

This means Cloudflare provides DNS resolution but does not proxy the connection.

This is important because the hostname may eventually be used for services such as game servers or other protocols that cannot use Cloudflare's standard HTTP/HTTPS reverse proxy.

DNS resolution therefore behaves as:

```text
home.robynshomelab.dev
        │
        ▼
Cloudflare DNS
        │
        ▼
Home public IPv4
```

The Cloudflare orange-cloud proxy should not be enabled for arbitrary game-server traffic.

---

## DDNS Updater

The DDNS updater runs on:

```text
CT 100
Hostname: pihole-nginx
IP:       192.168.20.99
```

The software used is:

```text
ddclient 3.10.0
```

The updater discovers the public IPv4 address using the web-based IP discovery service:

```text
ipify IPv4
```

This is necessary because CT 100 itself has the private LAN address:

```text
192.168.20.99
```

and therefore cannot determine the home's public address from its network interface.

---

## Configuration

The main `ddclient` configuration is stored on CT 100 at:

```text
/etc/ddclient.conf
```

This file contains the Cloudflare API token and therefore **must not be committed to Git**.

Its permissions are:

```text
-rw------- 1 root root
```

This means only `root` can read or modify the file.

The configuration manages only:

```text
home.robynshomelab.dev
```

rather than giving the updater responsibility for unrelated DNS records.

---

## Authentication

A dedicated Cloudflare API token is used for DDNS.

The token is separate from the Cloudflare API token used by Certbot for Let's Encrypt DNS-01 validation.

This separation follows the principle of least privilege and limits the impact if one credential is compromised.

The DDNS token is stored only on CT 100 and is not stored in this Git repository.

---

## Update Interval

The Debian `ddclient` configuration uses:

```text
daemon_interval="5m"
```

This causes `ddclient` to check for changes every five minutes.

A five-minute interval provides a reasonable balance between detecting address changes quickly and avoiding unnecessary API requests.

---

## Service

`ddclient` runs as a systemd service.

The service has been verified as:

```text
active
```

and:

```text
enabled
```

Being enabled means the service will automatically start when CT 100 boots.

---

## Verification

The DDNS configuration was tested manually before relying on the automatic service.

The manual update was executed with:

```bash
ddclient -daemon=0 -verbose
```

The update succeeded with:

```text
SUCCESS: updating home.robynshomelab.dev: IPv4 address set to <public-ip>
```

DNS resolution was then independently verified with:

```bash
dig +short home.robynshomelab.dev
```

The result matched the current public IPv4 address.

This verifies both:

1. `ddclient` can authenticate with Cloudflare and update the record.
2. Cloudflare DNS returns the updated address.

---

## Troubleshooting

### Check the service

```bash
systemctl status ddclient
```

### Check whether the service starts automatically

```bash
systemctl is-enabled ddclient
```

Expected:

```text
enabled
```

### Run a manual update

```bash
ddclient -daemon=0 -verbose
```

This is useful for diagnosing authentication, DNS, or IP-detection problems.

### Check the DNS record

```bash
dig +short home.robynshomelab.dev
```

### Check the configuration permissions

```bash
ls -l /etc/ddclient.conf
```

Expected:

```text
-rw------- 1 root root
```

---

## Security Considerations

The Cloudflare API token is a credential and must never be committed to Git.

The following files and information should remain outside the repository:

```text
/etc/ddclient.conf
Cloudflare API tokens
Private keys
Passwords
Other credentials
```

The repository documents the configuration and architecture without containing the secret itself.

The DDNS token should also remain restricted to the `robynshomelab.dev` zone and only the permissions required for DNS management.

---

## What DDNS Does Not Do

DDNS only keeps a hostname pointed at the current public IP address.

It does **not**:

* open ports on the router
* bypass NAT
* configure firewall rules
* expose internal services automatically
* provide encryption
* provide a reverse proxy
* replace NetBird

For example:

```text
DDNS
home.robynshomelab.dev
        │
        ▼
current public IP
```

This does not mean an external connection can automatically reach an internal server.

Any future public service exposure will require an appropriate network path and security controls.

---

## Relationship With NetBird

DDNS and NetBird serve different purposes.

### DDNS

Used for stable public DNS addressing:

```text
home.robynshomelab.dev
        │
        ▼
Home public IP
```

### NetBird

Used for private remote access:

```text
Remote device
      │
      ▼
   NetBird
      │
      ▼
Homelab services
```

The current NetBird LXC remains dedicated to private homelab access.

The future NetBird deployment on the Pterodactyl VM will be used separately for controlled service/game exposure.

---

## Future Use

The DDNS hostname may eventually be useful for services hosted on the Dell OptiPlex 9020, particularly game-server workloads.

The hostname provides a stable DNS name even if the ISP changes the home's public IPv4 address.

The exact services exposed through the public address will be documented separately when the 9020 and Pterodactyl infrastructure are implemented.
