# Jellyfin

## Overview

Jellyfin provides the homelab's self-hosted media server.

Hostname:

    jellyfin

IP address:

    192.168.20.98

VMID:

    CT102

Jellyfin runs as an LXC container on `pve-1`.

## Network

LAN:

    192.168.20.0/24

Jellyfin:

    192.168.20.98

Reverse proxy:

    192.168.20.94

Jellyfin's native HTTP port:

    8096

The Jellyfin backend is not intended to be directly exposed to the Internet.

## Reverse Proxy

Jellyfin is accessed through the central Nginx reverse proxy on CT106.

Hostname:

    jellyfin.robynshomelab.dev

The internal DNS record points the hostname to:

    192.168.20.94

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
    CT102 Jellyfin
    192.168.20.98:8096

Nginx provides TLS termination.

Jellyfin itself does not need to manage the public certificate.

## DNS

Pi-hole provides the internal DNS record:

    jellyfin.robynshomelab.dev -> 192.168.20.94

This allows LAN and NetBird clients to use the same hostname.

The DNS path for an internal client is:

    Client
      |
      v
    Pi-hole
    192.168.20.99
      |
      v
    192.168.20.94
      |
      v
    Nginx

## NetBird Access

NetBird clients can access Jellyfin through the existing CT101 routing peer.

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
    CT102 Jellyfin
    192.168.20.98

No direct NetBird route to CT102 is currently required.

## Storage

Jellyfin's current application and media storage configuration should be treated separately from the planned bulk-storage project.

A WD Blue 4 TB (`WD40EZRZ`) HDD is planned for direct installation into `pve-2`.

The intended future storage architecture is:

    pve-2
      |
      +--> 4 TB HDD
            |
            +--> Host filesystem
            |
            +--> NFS/fileshare
                    |
                    +--> Media stack
                    +--> Jellyfin

The 4 TB HDD has not yet been installed and NFS has not yet been configured.

Therefore, documentation should not assume that Jellyfin currently depends on the future NFS storage.

## Media Stack Integration

A separate media automation stack is planned for VM103.

Planned components include:

- Seerr/Jellyseerr
- Sonarr
- Radarr
- Prowlarr
- Bazarr
- qBittorrent

The future media stack will use the 4 TB storage on `pve-2` through NFS.

Jellyfin will consume the resulting media library.

The media automation stack is not yet deployed.

## Security

Jellyfin should remain behind the reverse proxy rather than being directly exposed through router port forwarding.

The intended access methods are:

- LAN
- NetBird
- Other explicitly configured private access paths

The backend address:

    192.168.20.98:8096

should not be exposed publicly unless the architecture is deliberately changed.

## Verification

### Check Jellyfin container

From Proxmox:

    pct status 102

### Test Jellyfin directly

From the LAN:

    curl -I http://192.168.20.98:8096

A successful response confirms that the Jellyfin service is reachable directly.

### Test Nginx backend

From CT106:

    curl -I http://192.168.20.98:8096

### Test DNS

From an internal client:

    dig @192.168.20.99 jellyfin.robynshomelab.dev

Expected result:

    192.168.20.94

### Test HTTPS

From an internal client:

    curl -I https://jellyfin.robynshomelab.dev

The request should terminate TLS on CT106 and be proxied to CT102.

## Troubleshooting

### Jellyfin is unreachable directly

Check the container:

    pct status 102

Then check the Jellyfin service inside CT102.

### Jellyfin works directly but not through the hostname

Check DNS:

    dig @192.168.20.99 jellyfin.robynshomelab.dev

Expected:

    192.168.20.94

If DNS is correct, investigate CT106 Nginx.

### Nginx cannot reach Jellyfin

From CT106:

    curl -I http://192.168.20.98:8096

If this fails, investigate:

- CT102 networking
- Jellyfin service status
- Container firewall configuration
- Jellyfin listening address

### NetBird client cannot access Jellyfin

Check the route through CT101:

    192.168.20.94/32

Then verify that:

    jellyfin.robynshomelab.dev

resolves to:

    192.168.20.94

## Current State

Jellyfin is deployed on CT102 and is available through the central Nginx reverse proxy.

Current architecture:

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
    CT102 Jellyfin
    192.168.20.98:8096

The future 4 TB storage and media automation stack remain separate planned projects.