# Beszel

## Overview

Beszel provides lightweight system monitoring for the homelab.

Hostname:

    beszel

IP address:

    192.168.20.96

VMID:

    CT104

Beszel is deployed as an LXC container on `pve-1`.

## Role

Beszel provides monitoring and resource visibility for homelab systems.

It is intended to provide visibility into:

- CPU usage
- Memory usage
- Disk usage
- Network activity
- System health
- Resource trends

Additional monitored systems can be added as the homelab expands.

## Network

LAN:

    192.168.20.0/24

Beszel:

    192.168.20.96

Reverse proxy:

    192.168.20.94

The Beszel service is accessed through the central Nginx reverse proxy.

## Reverse Proxy

Beszel is accessed through:

    beszel.robynshomelab.dev

Pi-hole provides the internal DNS record:

    beszel.robynshomelab.dev -> 192.168.20.94

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
    CT104 Beszel
    192.168.20.96:8090

Nginx provides TLS termination.

Beszel's backend does not need to manage the public certificate.

## DNS

Pi-hole provides split DNS for the Beszel hostname.

Internal resolution:

    beszel.robynshomelab.dev
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

NetBird clients can access Beszel through CT101's existing route to CT106.

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
    CT104 Beszel
    192.168.20.96

No direct NetBird route to CT104 is currently required.

## Monitoring Architecture

Beszel is part of the homelab's monitoring layer.

Current monitoring-related services include:

    CT104
    192.168.20.96
        |
        +--> Beszel

    CT105
    192.168.20.95
        |
        +--> Uptime Kuma

These services have different roles.

Beszel focuses primarily on system/resource monitoring.

Uptime Kuma focuses primarily on service availability and uptime monitoring.

## Pterodactyl Monitoring

Pterodactyl VM108 is not yet fully integrated into the homelab monitoring architecture.

Future monitoring should cover:

- VM108 resource usage
- Docker
- Wings
- Game-server resource consumption
- Game-server availability
- Storage usage

Monitoring requirements should be reviewed after Wings and the first game server are deployed.

## Storage Monitoring

As the 4 TB HDD on `pve-2` is not yet installed, its long-term monitoring requirements have not yet been implemented.

Once deployed, monitoring should include:

- Disk capacity
- Filesystem usage
- Disk health where practical
- NFS availability
- Media storage consumption

## Security

Beszel should remain a private management service.

Access should be restricted to:

- LAN
- NetBird

The backend service should not be directly exposed through router port forwarding.

The reverse proxy provides the preferred HTTPS access path.

## Verification

### Check container

From Proxmox:

    pct status 104

### Check Beszel service

The exact service name depends on the installed Beszel component.

Check the container's running services as required.

### Test backend connectivity

From CT106:

    curl -I http://192.168.20.96:8090

A successful response confirms that Nginx can reach Beszel.

### Test DNS

From an internal client:

    dig @192.168.20.99 beszel.robynshomelab.dev

Expected result:

    192.168.20.94

### Test HTTPS

From an internal client:

    curl -I https://beszel.robynshomelab.dev

The request should terminate TLS on CT106.

## Troubleshooting

### Beszel is unreachable

Check the container:

    pct status 104

Then investigate the Beszel service inside CT104.

### Beszel works directly but not through the hostname

Check DNS:

    dig @192.168.20.99 beszel.robynshomelab.dev

Expected:

    192.168.20.94

If DNS is correct, investigate CT106 Nginx.

### Nginx cannot reach Beszel

From CT106:

    curl -I http://192.168.20.96:8090

If this fails, investigate:

- CT104 networking
- Beszel service status
- Container firewall configuration
- Listening address
- Port configuration

### NetBird client cannot access Beszel

Verify:

1. NetBird is connected.
2. CT101 is routing `192.168.20.94/32`.
3. `beszel.robynshomelab.dev` resolves to `192.168.20.94`.
4. CT106 Nginx is running.
5. CT106 can reach CT104.

## Current State

Beszel is deployed on CT104.

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
    CT104 Beszel
    192.168.20.96:8090

Beszel is part of the current monitoring infrastructure.

Additional Pterodactyl and storage monitoring will be configured as those components are deployed.