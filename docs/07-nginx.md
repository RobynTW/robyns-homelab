# Nginx

## Overview

CT106 provides the homelab's central Nginx reverse proxy and TLS termination.

Hostname:

    nginx

IP address:

    192.168.20.94

VMID:

    CT106

Primary services:

- Nginx
- Certbot

Nginx provides the central HTTPS entry point for internal homelab services.

## Architecture

The current reverse-proxy architecture is:

    Client
      |
      | HTTPS
      v
    CT106 Nginx
    192.168.20.94
      |
      +--> Jellyfin
      |    192.168.20.98:8096
      |
      +--> Uptime Kuma
      |    192.168.20.95:3001
      |
      +--> Beszel
      |    192.168.20.96:8090
      |
      +--> Pi-hole
      |    192.168.20.99:8080
      |
      +--> Pterodactyl Panel
           192.168.20.111:80

Nginx terminates HTTPS and proxies requests to the internal service over HTTP.

## Service Routing

Current reverse-proxy hostnames:

| Hostname | Backend | Purpose |
|---|---|---|
| `jellyfin.robynshomelab.dev` | `192.168.20.98:8096` | Jellyfin |
| `status.robynshomelab.dev` | `192.168.20.95:3001` | Uptime Kuma |
| `beszel.robynshomelab.dev` | `192.168.20.96:8090` | Beszel |
| `pihole.robynshomelab.dev` | `192.168.20.99:8080` | Pi-hole |
| `panel.robynshomelab.dev` | `192.168.20.111:80` | Pterodactyl Panel |

All of these hostnames resolve internally to:

    192.168.20.94

Pi-hole provides the internal split-DNS records.

## Pterodactyl Panel

The Pterodactyl Panel is hosted on VM108:

    192.168.20.111

The Panel's configured public hostname is:

    panel.robynshomelab.dev

The request path is:

    Client
      |
      | HTTPS
      v
    CT106
    192.168.20.94
      |
      | HTTP
      v
    VM108
    192.168.20.111
      |
      v
    Pterodactyl Panel

The Panel itself does not terminate HTTPS.

CT106 provides TLS termination.

## Panel Backend

The VM108 local Nginx server listens on:

    192.168.20.111:80

CT106 proxies Panel requests to this backend.

The backend remains HTTP because the connection is entirely within the homelab LAN.

The external client-facing connection remains HTTPS.

## TLS

TLS certificates are managed by Certbot on CT106.

Cloudflare is used for DNS-01 validation.

The ACME flow is:

    CT106 Certbot
        |
        v
    Cloudflare DNS
        |
        v
    Let's Encrypt
        |
        v
    CT106
        |
        v
    Nginx HTTPS

The Cloudflare API credential used for ACME is stored locally on CT106.

It is not stored in GitHub.

## Certificates

Current certificates managed by CT106 include:

    jellyfin.robynshomelab.dev
    status.robynshomelab.dev
    beszel.robynshomelab.dev
    pihole.robynshomelab.dev

The Pterodactyl Panel uses:

    panel.robynshomelab.dev

The Panel certificate is part of the current HTTPS deployment.

## HTTP and HTTPS

Nginx listens on:

    80
    443

HTTP is used for certificate validation and HTTP-to-HTTPS handling where required.

Normal service access should use HTTPS.

Example:

    https://panel.robynshomelab.dev

## Internal DNS

Pi-hole provides split DNS for the reverse-proxy hostnames.

For example:

    panel.robynshomelab.dev
        |
        v
    192.168.20.94

The same pattern applies to the other internal services.

This allows clients on the LAN and NetBird network to use consistent hostnames while keeping service traffic inside the homelab.

## NetBird

NetBird clients can reach CT106 through the existing NetBird routing peer.

Current route:

    NetBird Client
        |
        v
    CT101
    192.168.20.97
        |
        | 192.168.20.94/32
        v
    CT106 Nginx
    192.168.20.94
        |
        v
    Internal service

The Pterodactyl Panel therefore does not currently require a direct NetBird route to VM108.

The existing route to CT106 is sufficient for Panel access.

VM108 will eventually receive its own NetBird peer for game-server networking.

## Security

The reverse proxy is intended to provide a controlled entry point to internal services.

Services should not be directly exposed through router port forwarding unless explicitly required.

The current architecture does not use router port forwarding for the Panel.

The Pterodactyl Panel is intended to remain accessible through:

- LAN
- NetBird

It is not intended to become a directly internet-accessible service.

## Configuration

Nginx configuration is stored under the standard Nginx configuration directories on CT106.

Site-specific configurations should be kept separate where practical.

Configuration changes should be tested before reloading Nginx.

Recommended validation:

    nginx -t

If the configuration test succeeds:

    systemctl reload nginx

## Service Status

Check Nginx:

    systemctl status nginx

Check Certbot's renewal timer:

    systemctl status certbot.timer

Check listening ports:

    ss -lntup | grep -E ':80|:443'

## Verification

### Test the local Nginx server

On CT106:

    curl -I http://127.0.0.1

### Test the Panel backend

From CT106:

    curl -I -H "Host: panel.robynshomelab.dev" http://192.168.20.111

A successful HTTP response confirms that CT106 can reach the Panel backend.

### Test HTTPS

From an internal client:

    curl -I https://panel.robynshomelab.dev

The response should be served by CT106 with the appropriate TLS certificate.

### Test DNS

From an internal client:

    dig panel.robynshomelab.dev

The expected internal address is:

    192.168.20.94

## Troubleshooting

### DNS resolves incorrectly

Check Pi-hole first.

    dig @192.168.20.99 panel.robynshomelab.dev

Expected:

    192.168.20.94

### Nginx configuration fails

Run:

    nginx -t

Do not reload Nginx until the configuration test succeeds.

### Backend connection fails

From CT106:

    curl -I http://192.168.20.111

If this fails, investigate VM108's local Nginx or Pterodactyl installation.

### HTTPS certificate problems

Check:

- DNS resolution
- Certbot configuration
- Cloudflare DNS-01 credentials
- Certificate expiry
- Nginx certificate paths
- Nginx configuration

Certbot status:

    certbot certificates

## Historical Architecture

Nginx and Certbot were previously hosted on CT100.

That architecture has been retired.

CT100 is now dedicated to:

    Pi-hole
    Unbound
    ddclient

CT106 is now dedicated to:

    Nginx
    Certbot

This separation is intentional and should be maintained unless the architecture is explicitly redesigned.

## Current State

CT106 is the central reverse proxy and TLS termination point for the homelab.

Current architecture:

    Internal Client
        |
        | DNS
        v
    Pi-hole
    192.168.20.99
        |
        | 192.168.20.94
        v
    CT106 Nginx
    192.168.20.94
        |
        +--> CT102 Jellyfin
        |
        +--> CT104 Beszel
        |
        +--> CT105 Uptime Kuma
        |
        +--> CT100 Pi-hole
        |
        +--> VM108 Pterodactyl Panel

The reverse proxy provides a consistent HTTPS interface while keeping the underlying services on their private LAN addresses.