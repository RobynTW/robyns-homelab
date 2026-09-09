# Media Stack

## Overview

The media stack is a planned application stack for automating media discovery, organisation, downloading, and metadata management.

The stack is intended to integrate with the existing Jellyfin server.

The media stack is **not yet deployed**.

Reserved VMID:

    VM103

Planned host:

    pve-1

## Planned Components

The planned stack includes:

| Component | Purpose | Status |
|---|---|---|
| Seerr / Jellyseerr | Media request management | Planned |
| Sonarr | TV series management | Planned |
| Radarr | Movie management | Planned |
| Prowlarr | Indexer management | Planned |
| Bazarr | Subtitle management | Planned |
| qBittorrent | Download client | Planned |

The exact final application set may change as the media architecture is implemented.

## Jellyfin Integration

Jellyfin is already deployed separately on CT102.

Jellyfin:

    192.168.20.98

The media stack will ultimately provide media to Jellyfin through a shared media library.

Current Jellyfin access:

    jellyfin.robynshomelab.dev
        |
        v
    CT106 Nginx
    192.168.20.94
        |
        v
    CT102 Jellyfin
    192.168.20.98:8096

The media automation stack does not replace Jellyfin.

Instead, it manages the media that Jellyfin serves.

## Storage

Bulk media storage is planned for `pve-2`.

A WD Blue 4 TB (`WD40EZRZ`) HDD is intended to be installed directly into the Dell OptiPlex 9020 SFF.

The HDD has not yet been installed.

The intended architecture is:

    pve-2
      |
      +--> 4 TB HDD
            |
            +--> Host filesystem
                  |
                  +--> NFS
                        |
                        +--> Media stack
                        |
                        +--> Jellyfin

The 4 TB HDD will provide bulk media storage rather than VM operating-system storage.

The Proxmox SSD remains responsible for VM and system storage.

## NFS

The planned storage architecture uses a host-mounted filesystem on `pve-2`, exported over NFS.

This avoids introducing a dedicated NAS operating system for the current homelab design.

The current storage plan is therefore:

    4 TB HDD
        |
        v
    pve-2 filesystem
        |
        v
    NFS export
        |
        +--> VM103 media stack
        |
        +--> Jellyfin

NFS has not yet been configured.

The final filesystem, mount paths, export paths, permissions, and network restrictions will be documented when the storage is deployed.

## Media Workflow

The intended workflow is:

    User
      |
      v
    Seerr / Jellyseerr
      |
      +--> Movie request
      |      |
      |      v
      |    Radarr
      |
      +--> TV request
             |
             v
           Sonarr
              |
              v
           Prowlarr
              |
              v
         Indexers
              |
              v
        qBittorrent
              |
              v
        Media Storage
              |
              v
         Sonarr/Radarr
              |
              v
          Jellyfin

Bazarr will provide subtitle management where required.

## Directory Structure

The final media directory structure has not yet been established.

It should be designed before deploying the automation applications.

The structure should separate:

- Downloads
- Movies
- TV shows
- Subtitles
- Application configuration
- Temporary/incomplete downloads

The final paths should be documented once the NFS storage is operational.

## VM103

VMID:

    103

Status:

    Reserved

Purpose:

    Future media stack

The VM has not yet been deployed.

The final VM resource allocation should be determined based on the workload and storage requirements rather than being assumed in advance.

## Network Architecture

The planned media stack will operate on the existing LAN.

LAN:

    192.168.20.0/24

The media stack will eventually communicate with:

- NFS storage on `pve-2`
- Jellyfin on CT102
- Download/indexer services
- DNS through Pi-hole
- Other required homelab services

The existing network is currently flat.

Future VLAN and firewall changes may require the media-stack network design to be updated.

## DNS and Reverse Proxy

If the media applications require web access, their hostnames should use the existing DNS and reverse-proxy architecture.

The intended pattern is:

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
    Media application

Individual hostnames will be added to Pi-hole and Nginx when the services are deployed.

No media-stack hostname should be documented as deployed until the corresponding service actually exists.

## NetBird

NetBird clients should be able to access media-management interfaces through the existing CT101 routing architecture once those services are deployed.

The existing route to CT106 is:

    192.168.20.94/32

The intended path is:

    NetBird Client
          |
          v
    CT101
    192.168.20.97
          |
          v
    CT106 Nginx
    192.168.20.94
          |
          v
    Media application

Additional routes should only be added when required.

## Security

The media stack should remain private.

Management interfaces should not be directly exposed to the public Internet.

Preferred access methods are:

- LAN
- NetBird

Download and automation services should be isolated as much as practical.

Credentials for indexers, download services, APIs, and other applications must not be committed to GitHub.

## Monitoring

The media stack should eventually be integrated with the existing monitoring infrastructure.

Potential monitoring:

- VM103 availability
- Application availability
- Storage usage
- NFS availability
- Download client availability
- Media application health

Uptime Kuma can provide service availability monitoring.

Beszel can provide system/resource monitoring.

## Backups

The media stack will require a backup strategy for application configuration.

At minimum, backups should account for:

- Sonarr configuration
- Radarr configuration
- Prowlarr configuration
- Bazarr configuration
- Seerr/Jellyseerr configuration
- qBittorrent configuration
- Application databases where applicable

The media files themselves may require a separate backup strategy due to their size.

## Current State

The current state is:

    Jellyfin
    CT102
    192.168.20.98
        |
        +--> Deployed

    VM103
        |
        +--> Reserved
        |
        +--> Media stack not deployed

    pve-2
        |
        +--> 4 TB HDD planned
        |
        +--> NFS not configured

The media automation stack remains a future project.

## Planned Deployment Order

When the media stack is eventually implemented, the preferred order is:

1. Install and verify the 4 TB HDD on `pve-2`.
2. Create and verify the host filesystem.
3. Configure NFS.
4. Deploy VM103.
5. Mount the NFS storage.
6. Establish the media directory structure.
7. Deploy qBittorrent.
8. Deploy Prowlarr.
9. Deploy Sonarr.
10. Deploy Radarr.
11. Deploy Bazarr.
12. Deploy Seerr/Jellyseerr.
13. Integrate the completed library with Jellyfin.
14. Add Nginx and Pi-hole DNS entries where required.
15. Add Uptime Kuma and Beszel monitoring.
16. Document the final configuration.

The exact order may be adjusted if implementation requirements dictate otherwise.