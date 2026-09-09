# Pi-hole

## Overview

CT100 provides the homelab's primary DNS filtering and local DNS services.

Hostname:

    pihole

IP address:

    192.168.20.99

VMID:

    CT100

Primary services:

- Pi-hole
- Unbound
- ddclient

Pi-hole provides DNS filtering and internal DNS overrides for LAN and NetBird clients.

## Network Configuration

LAN:

    192.168.20.0/24

Pi-hole:

    192.168.20.99:53

Router:

    192.168.20.1

Pi-hole is the primary DNS server used by the homelab.

NetBird clients are also configured to use Pi-hole for DNS.

## Unbound

Unbound runs locally on CT100.

    Pi-hole
    192.168.20.99:53
        |
        v
    Unbound
    127.0.0.1:5335

Pi-hole forwards recursive DNS queries to Unbound.

Unbound provides recursive DNS resolution rather than relying directly on a third-party public recursive resolver.

Further details are documented in `05-unbound.md`.

## Local DNS

Pi-hole provides local DNS records for internal services.

The current internal DNS records point service hostnames to CT106, the central Nginx reverse proxy.

| Hostname | Address | Purpose |
|---|---|---|
| `jellyfin.robynshomelab.dev` | `192.168.20.94` | Jellyfin reverse proxy |
| `status.robynshomelab.dev` | `192.168.20.94` | Uptime Kuma reverse proxy |
| `beszel.robynshomelab.dev` | `192.168.20.94` | Beszel reverse proxy |
| `pihole.robynshomelab.dev` | `192.168.20.94` | Pi-hole reverse proxy |
| `panel.robynshomelab.dev` | `192.168.20.94` | Pterodactyl reverse proxy |

This creates split-DNS behaviour for services that also have public Cloudflare DNS records.

## Pterodactyl Panel DNS

The Pterodactyl Panel uses:

    panel.robynshomelab.dev

For internal clients, Pi-hole resolves this hostname to:

    192.168.20.94

The request then reaches CT106:

    Client
      |
      | panel.robynshomelab.dev
      v
    Pi-hole
    192.168.20.99
      |
      | 192.168.20.94
      v
    CT106 Nginx
      |
      v
    VM108
    192.168.20.111

The public Cloudflare record remains separate and is not overridden by Pi-hole for external clients.

## DNS Filtering

Pi-hole provides network-wide DNS filtering.

Blocked domains are returned according to the Pi-hole filtering configuration.

A blocked DNS request may therefore return an address such as:

    0.0.0.0

or:

    ::

This is expected filtering behaviour and does not necessarily indicate a DNS failure.

## NetBird DNS

NetBird clients use Pi-hole as their DNS server:

    192.168.20.99:53

This provides NetBird clients with:

- Pi-hole filtering
- Internal service hostname resolution
- Access to the homelab's DNS architecture

The NetBird DNS configuration uses Pi-hole as the global/default nameserver for:

    [.]

This means general DNS queries from NetBird clients are routed through Pi-hole.

## DDNS

CT100 also runs ddclient.

ddclient updates the Cloudflare DNS record:

    home.robynshomelab.dev

The DDNS configuration uses a dedicated Cloudflare API credential.

The credential is stored locally on CT100 and is not committed to GitHub.

DDNS details are documented in `14-ddns.md`.

## Web Interface

The Pi-hole web interface is hosted locally on CT100.

Local backend address:

    192.168.20.99:8080

The interface is exposed through the central Nginx reverse proxy.

Internal hostname:

    pihole.robynshomelab.dev

The access path is:

    Client
      |
      | HTTPS
      v
    CT106 Nginx
    192.168.20.94
      |
      | HTTP
      v
    CT100 Pi-hole
    192.168.20.99:8080

## Reverse Proxy

Nginx was previously hosted on CT100.

That architecture is no longer current.

The current architecture is:

    CT100
    192.168.20.99
      |
      +--> Pi-hole
      +--> Unbound
      +--> ddclient

    CT106
    192.168.20.94
      |
      +--> Nginx
      +--> Certbot
      |
      +--> Pi-hole reverse proxy

This separation keeps DNS infrastructure independent from the central reverse proxy and TLS infrastructure.

## Security

The Pi-hole container contains DNS infrastructure and Cloudflare DDNS credentials.

Credentials must remain local to the host.

Do not document or commit:

- Cloudflare API tokens
- Passwords
- Session credentials
- Private keys
- Authentication secrets

Configuration examples should use placeholders where credentials are required.

## Troubleshooting

### Test Pi-hole DNS

From a LAN client:

    nslookup example.com 192.168.20.99

or:

    dig @192.168.20.99 example.com

### Test internal DNS

For example:

    dig @192.168.20.99 panel.robynshomelab.dev

The expected internal result is:

    192.168.20.94

### Test NetBird DNS

From a NetBird client, confirm that DNS queries are being sent to:

    192.168.20.99

### Test Unbound

From CT100:

    dig @127.0.0.1 -p 5335 example.com

### Check Pi-hole service

On CT100:

    systemctl status pihole-FTL

### Check Unbound

On CT100:

    systemctl status unbound

### Check ddclient

On CT100:

    systemctl status ddclient

## Current Architecture

    LAN Client
        |
        v
    Pi-hole
    192.168.20.99:53
        |
        +--> Local DNS overrides
        |
        +--> Unbound
        |    127.0.0.1:5335
        |
        +--> Internet DNS resolution

    Internal HTTPS request
        |
        v
    panel.robynshomelab.dev
        |
        v
    Pi-hole
        |
        | 192.168.20.94
        v
    CT106 Nginx
        |
        v
    VM108 Pterodactyl