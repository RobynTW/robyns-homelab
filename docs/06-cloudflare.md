# Cloudflare

## Overview

Cloudflare provides the homelab's authoritative public DNS, Dynamic DNS, and DNS-01 authentication for Let's Encrypt.

Domain:

    robynshomelab.dev

Registrar:

    Porkbun

Cloudflare is authoritative for the domain.

Cloudflare is **not** currently used as a traffic proxy for homelab services.

The Cloudflare records are DNS-only.

## Cloudflare Roles

Cloudflare currently provides three main functions:

1. Authoritative public DNS.
2. Dynamic DNS updates for the home WAN address.
3. DNS-01 challenges for Let's Encrypt certificates.

Cloudflare does not currently provide:

- Reverse proxying
- Public traffic forwarding
- Direct access to internal services
- Public exposure of the Pterodactyl Panel

## Public DNS

The current public DNS records include:

| Hostname | Target | Type | Proxy |
|---|---|---|---|
| `home.robynshomelab.dev` | Home WAN IP | A | DNS-only |
| `panel.robynshomelab.dev` | Home WAN IP | A | DNS-only |

The actual WAN IP is managed dynamically.

The `home` record is updated by ddclient on CT100.

The `panel` record is intentionally retained even though the Panel is not publicly reachable.

## Why the Panel Uses the WAN IP Publicly

The public Cloudflare record for:

    panel.robynshomelab.dev

points to the home WAN IP.

This does **not** mean the Pterodactyl Panel is publicly accessible.

There is currently no router port forwarding configured to expose the Panel.

For internal clients, Pi-hole overrides the public DNS result:

    panel.robynshomelab.dev
            |
            v
    192.168.20.94

This is split DNS.

The public Cloudflare record exists primarily so that the hostname has a valid public DNS identity and can be used for ACME DNS-01 certificate issuance.

## Split DNS

Internal DNS is handled by Pi-hole on CT100.

Pi-hole:

    192.168.20.99

Internal service names resolve to the Nginx reverse proxy on CT106:

    192.168.20.94

Current internal records include:

    jellyfin.robynshomelab.dev -> 192.168.20.94
    status.robynshomelab.dev  -> 192.168.20.94
    beszel.robynshomelab.dev  -> 192.168.20.94
    pihole.robynshomelab.dev  -> 192.168.20.94
    panel.robynshomelab.dev   -> 192.168.20.94

The DNS flow for an internal client is therefore:

    Client
      |
      v
    Pi-hole
    192.168.20.99
      |
      | local DNS override
      v
    192.168.20.94
      |
      v
    Nginx

The external DNS flow is different:

    External DNS client
      |
      v
    Cloudflare
      |
      v
    Home WAN IP

Because there is no appropriate router port forwarding, external clients cannot reach the internal services through these records.

## Dynamic DNS

CT100 runs ddclient.

ddclient updates:

    home.robynshomelab.dev

with the current home WAN IP.

The DDNS service checks for changes periodically.

The current configured check interval is approximately:

    5 minutes

The Cloudflare credential used for DDNS is a dedicated API token.

The token is stored locally on CT100.

Credentials are never stored in the GitHub repository.

Further DDNS details are documented in:

    14-ddns.md

## Let's Encrypt DNS-01

Let's Encrypt certificates are managed by Certbot on CT106.

Cloudflare DNS is used for DNS-01 validation.

The flow is:

    CT106 Certbot
        |
        | Cloudflare API
        v
    Cloudflare DNS
        |
        | TXT challenge
        v
    Let's Encrypt
        |
        v
    Certificate

The ACME credential is separate from the DDNS credential.

This separation limits the permissions of each API credential.

The ACME credential is stored locally on CT106 at:

    /root/.secrets/certbot/cloudflare.ini

The file is root-owned and restricted to mode `600`.

The actual token is intentionally not documented.

## Current Certificates

Certbot on CT106 currently manages certificates for:

    jellyfin.robynshomelab.dev
    status.robynshomelab.dev
    beszel.robynshomelab.dev
    pihole.robynshomelab.dev

The Pterodactyl Panel certificate will use:

    panel.robynshomelab.dev

The Panel certificate is part of the current HTTPS deployment work.

## Cloudflare Proxy Status

Cloudflare proxying is deliberately disabled for the homelab records.

The records are:

    DNS-only

This means Cloudflare provides DNS resolution but does not sit in the HTTP/HTTPS traffic path.

The current traffic architecture is therefore:

    Client
      |
      v
    Cloudflare DNS
      |
      v
    Home WAN IP
      |
      v
    Router
      |
      v
    Internal service

For internal clients using split DNS, Cloudflare is bypassed for the DNS lookup:

    Client
      |
      v
    Pi-hole
      |
      v
    CT106 Nginx

## Security

Cloudflare API credentials must never be committed to GitHub.

Do not document:

- API tokens
- API keys
- Account credentials
- Private keys
- Certbot credentials

Only document:

- Credential purpose
- Credential location
- Required permissions
- Which service uses the credential

The DDNS and ACME credentials should remain separate.

## Verification

### Check public DNS

From a system using an external resolver:

    dig home.robynshomelab.dev

    dig panel.robynshomelab.dev

The public result should correspond to the current Cloudflare record.

### Check internal DNS

From the LAN:

    dig @192.168.20.99 panel.robynshomelab.dev

Expected result:

    192.168.20.94

Likewise:

    dig @192.168.20.99 jellyfin.robynshomelab.dev

Expected result:

    192.168.20.94

### Check DDNS

On CT100:

    systemctl status ddclient

The Cloudflare `home` record should correspond to the current WAN address.

### Check Certbot

On CT106:

    systemctl status certbot.timer

A dry-run can be performed when testing renewal configuration.

## Architecture Summary

The current Cloudflare and DNS architecture is:

    Internet
       |
       v
    Cloudflare
       |
       +--> Public DNS
       |
       +--> DNS-01
       |
       +--> DDNS record updates
       
    Internal Client
       |
       v
    Pi-hole
    192.168.20.99
       |
       +--> Split DNS
       |      |
       |      v
       |   CT106 Nginx
       |   192.168.20.94
       |
       +--> Unbound
              |
              v
          Recursive DNS

Cloudflare provides the public DNS control plane, while Pi-hole provides internal split DNS and DNS filtering.