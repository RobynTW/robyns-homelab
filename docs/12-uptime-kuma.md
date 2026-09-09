# Uptime Kuma

## Overview

Uptime Kuma provides service availability and uptime monitoring for the homelab.

Hostname:

    uptime-kuma

IP address:

    192.168.20.95

VMID:

    CT105

Uptime Kuma is deployed as an LXC container on `pve-1`.

## Role

Uptime Kuma is used to monitor whether services are reachable and responding.

It complements Beszel:

- Uptime Kuma — service availability and uptime
- Beszel — system and resource monitoring

This separation provides both service-level and infrastructure-level visibility.

## Network

LAN:

    192.168.20.0/24

Uptime Kuma:

    192.168.20.95

Reverse proxy:

    192.168.20.94

The Uptime Kuma interface is accessed through the central Nginx reverse proxy.

Uptime Kuma's backend port is:

    3001

## Reverse Proxy

Uptime Kuma is accessed through:

    status.robynshomelab.dev

Pi-hole provides the internal DNS record:

    status.robynshomelab.dev -> 192.168.20.94

The traffic path is:

    Client
      |
      | HTTPS
      v
    CT106 Nginx
    192.168.20.94
      |
      | HTTP
      v
    CT105 Uptime Kuma
    192.168.20.95:3001

Nginx provides TLS termination.

## DNS

Internal DNS is provided by Pi-hole.

    status.robynshomelab.dev
        |
        v
    192.168.20.94

The DNS path is:

    Client
      |
      v
    Pi-hole
    192.168.20.99
      |
      v
    CT106 Nginx
    192.168.20.94

## NetBird Access

NetBird clients can access Uptime Kuma through CT101's existing route to CT106.

The path is:

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
    CT105 Uptime Kuma
    192.168.20.95:3001

No direct NetBird route to CT105 is currently required.

## Monitoring Targets

Uptime Kuma should monitor important homelab services rather than only the Uptime Kuma application itself.

Current and appropriate targets include:

- Jellyfin
- Beszel
- Pi-hole
- Nginx
- Pterodactyl Panel
- Other critical services as they are deployed

Monitoring should normally use the same service hostname that users use.

For example:

    https://jellyfin.robynshomelab.dev

This tests more of the actual service path than simply checking whether the backend host responds.

## Pterodactyl Monitoring

The Pterodactyl Panel on VM108 should be monitored through:

    https://panel.robynshomelab.dev

The Panel is currently part of the homelab's service architecture.

Additional monitoring should be added when Wings and game servers are deployed.

Future monitoring targets may include:

- Pterodactyl Panel
- Wings
- Game-server ports
- Game-server availability
- VM108 availability
- Docker availability

Game-server monitoring should be added only after the actual server allocations and networking are established.

## Monitoring the Monitoring Services

The monitoring layer should be treated as infrastructure.

Uptime Kuma should monitor important services, while Beszel should monitor the host/container resources supporting them.

A complete monitoring architecture will eventually include:

    Infrastructure
         |
         +--> Beszel
         |
         +--> Uptime Kuma
                   |
                   +--> Service availability

## Security

Uptime Kuma is a management interface and should remain private.

Access should be restricted to:

- LAN
- NetBird

The backend port:

    192.168.20.95:3001

should not be directly exposed through router port forwarding.

The preferred access path is through CT106 Nginx.

## Verification

### Check container

From Proxmox:

    pct status 105

### Test Uptime Kuma backend

From CT106:

    curl -I http://192.168.20.95:3001

A successful response confirms that CT106 can reach Uptime Kuma.

### Test DNS

From an internal client:

    dig @192.168.20.99 status.robynshomelab.dev

Expected result:

    192.168.20.94

### Test HTTPS

From an internal client:

    curl -I https://status.robynshomelab.dev

The request should terminate TLS on CT106 and be proxied to CT105.

## Troubleshooting

### Uptime Kuma is unreachable

Check the container:

    pct status 105

Then investigate the Uptime Kuma service inside CT105.

### Uptime Kuma works directly but not through the hostname

Check DNS:

    dig @192.168.20.99 status.robynshomelab.dev

Expected:

    192.168.20.94

If DNS is correct, investigate CT106 Nginx.

### Nginx cannot reach Uptime Kuma

From CT106:

    curl -I http://192.168.20.95:3001

If this fails, investigate:

- CT105 networking
- Uptime Kuma service status
- Container firewall configuration
- Listening address
- Port configuration

### NetBird client cannot access Uptime Kuma

Verify:

1. NetBird is connected.
2. CT101 is routing `192.168.20.94/32`.
3. `status.robynshomelab.dev` resolves to `192.168.20.94`.
4. CT106 Nginx is running.
5. CT106 can reach CT105.

## Current State

Uptime Kuma is deployed on CT105.

Current access path:

    Client
      |
      v
    Pi-hole
    192.168.20.99
      |
      v
    CT106 Nginx
    192.168.20.94
      |
      v
    CT105 Uptime Kuma
    192.168.20.95:3001

Uptime Kuma provides service-level availability monitoring.

Beszel provides complementary system/resource monitoring.

Additional Pterodactyl and game-server monitoring will be configured as those components are deployed.