# Media Stack

## Overview

The media stack is planned for CT103 on the Proxmox 3060.

It is **not currently deployed**.

The purpose of the media stack is to automate media acquisition, organisation, subtitle management, and media requests while keeping Jellyfin as the primary media playback service.

The planned architecture is:

```text
                         Media Requests
                              │
                              ▼
                            Seerr
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                 Radarr              Sonarr
                 Movies              TV Shows
                    │                   │
                    └─────────┬─────────┘
                              ▼
                          Prowlarr
                              │
                              ▼
                         qBittorrent
                              │
                              ▼
                       9020 NAS Storage
                              │
                              ▼
                          Jellyfin
```

Bazarr will provide subtitle management alongside Sonarr and Radarr.

Seerr is the current unified successor to Jellyseerr and Overseerr. The project provides media-request and discovery functionality with Jellyfin, Plex, and Emby integration, as well as Sonarr and Radarr integration.

## Planned Container

The media stack is intended to run in:

```text
Proxmox pve-1
└── CT103
    └── Media Stack
```

Current CT103 allocation:

```text
ID: 103
Purpose: Future media stack
Status: Not yet deployed
```

The exact CPU, RAM, disk, and network configuration will be determined when CT103 is created.

## Planned Services

The media stack will contain:

```text
Seerr
Sonarr
Radarr
Prowlarr
Bazarr
qBittorrent
```

The stack intentionally does not include:

```text
Lidarr
Readarr
```

Those services are not currently required for this homelab.

## Service Roles

### Seerr

Seerr will provide the user-facing media-request interface.

Users will be able to request:

```text
Movies
TV Shows
```

Seerr will then communicate with Radarr or Sonarr depending on the requested media type.

Planned flow:

```text
User
 │
 ▼
Seerr
 ├── Movie request → Radarr
 └── TV request    → Sonarr
```

Seerr will also integrate with the existing Jellyfin server so users can authenticate against Jellyfin and see which requested media is already available.

Seerr is the modern successor to Jellyseerr and Overseerr following the merger of the two projects in February 2026.

For this homelab, **Seerr should be deployed rather than the older Jellyseerr application**.

### Radarr

Radarr will manage movies.

Responsibilities include:

```text
Movie requests
Movie searching
Quality profiles
Download management
File organisation
Library imports
```

Radarr will send download searches through Prowlarr and downloads will be handled by qBittorrent.

### Sonarr

Sonarr will manage television series.

Responsibilities include:

```text
Series requests
Episode searching
Season monitoring
Quality profiles
Download management
File organisation
Library imports
```

Sonarr will use Prowlarr for indexer access and qBittorrent as the download client.

### Prowlarr

Prowlarr will manage indexers centrally.

Rather than configuring indexers independently in Sonarr and Radarr, Prowlarr will provide a central indexer configuration.

Planned relationship:

```text
                    Prowlarr
                   /        \
                  ▼          ▼
              Sonarr       Radarr
```

This reduces duplicated configuration and makes indexer management easier.

### qBittorrent

qBittorrent will be the download client.

The planned flow is:

```text
Sonarr/Radarr
      │
      ▼
  qBittorrent
      │
      ▼
Temporary downloads
      │
      ▼
Completed media
```

qBittorrent will not be used as the media library itself.

The completed files will ultimately reside on the NAS.

### Bazarr

Bazarr will manage subtitles for media managed by Sonarr and Radarr.

Its role is:

```text
Sonarr ──┐
         ├──► Bazarr ──► Subtitles
Radarr ──┘
```

Bazarr will therefore operate alongside the two library-management applications rather than directly managing the media library.

## Storage Architecture

The Dell OptiPlex 9020 is intended to provide the primary media storage.

The planned architecture is:

```text
                    Dell OptiPlex 9020
                         NAS
                          │
                          │ NFS
                          ▼
                       CT103
                    Media Stack
                          │
                          ▼
                       CT102
                       Jellyfin
```

The 9020 will be configured as the dedicated storage/NAS system before the media stack is deployed.

The current plan is to use a Linux-based NAS operating system with NFS.

The exact NAS operating system will be decided during the 9020 storage build.

## Important Storage Principle

The media directories should be designed **before** the NAS is mounted.

Temporary local storage should not be created on CT103 with the expectation that it will later be migrated into the NAS.

The goal is for the final architecture to use the NAS as the authoritative location for media from the beginning.

This avoids unnecessary migration and permission problems later.

## Planned NAS Layout

The exact directory structure will be established during the NAS configuration.

Conceptually, the NAS will provide separate areas for:

```text
Media
├── Movies
└── TV

Downloads
└── qBittorrent
```

The precise paths will depend on the final NAS filesystem and NFS export configuration.

The media stack should therefore avoid hard-coding paths until the NAS has been deployed.

## Download and Library Flow

The intended complete flow is:

```text
                    Seerr
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
       Radarr                   Sonarr
          │                       │
          └───────────┬───────────┘
                      ▼
                   Prowlarr
                      │
                      ▼
                 qBittorrent
                      │
                      ▼
                  NAS / 9020
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
       Movies                   TV Shows
          │                       │
          └───────────┬───────────┘
                      ▼
                   Jellyfin
```

Bazarr operates alongside Sonarr and Radarr to provide subtitle management.

## Jellyfin Integration

Jellyfin is already deployed separately on CT102:

```text
CT102
Jellyfin
192.168.20.98
```

The media stack will not replace Jellyfin.

Instead, Jellyfin will read the media stored on the 9020 NAS.

The intended relationship is:

```text
9020 NAS
   │
   │ NFS
   ▼
CT102 Jellyfin
   │
   ▼
Media playback
```

Seerr will integrate with Jellyfin as the user-facing media discovery and request layer.

## NFS Mounting

Once the NAS is operational, the required NFS exports will be created on the 9020.

The relevant clients will be:

```text
CT103 → Media stack
CT102 → Jellyfin
```

The final mount points should be consistent between the applications where practical.

This will simplify:

```text
File permissions
Path configuration
Library management
Troubleshooting
```

NFS configuration should not be documented as complete until the 9020 is actually deployed.

## Permissions

File ownership and permissions will need to be designed around the services accessing the NAS.

The important services are:

```text
qBittorrent
Sonarr
Radarr
Bazarr
Jellyfin
```

The final permissions model should allow:

```text
qBittorrent → write downloads
Sonarr      → read/write TV
Radarr      → read/write movies
Bazarr      → read/write subtitle files
Jellyfin    → read media
```

The exact UID/GID mapping will be established during deployment.

Permissions should be tested with actual file creation and access rather than assuming that a working NFS mount means the application permissions are correct.

## Network Architecture

The media stack will use the existing server network.

Current server addresses include:

```text
Proxmox    192.168.20.100
Nginx      192.168.20.94
Uptime     192.168.20.95
Beszel     192.168.20.96
NetBird    192.168.20.97
Jellyfin   192.168.20.98
Pi-hole    192.168.20.99
```

CT103 will receive its own static IP when it is deployed.

The media applications should communicate directly over the LAN rather than through the public internet.

## Reverse Proxy

Seerr will eventually be made available through the existing Nginx reverse proxy.

Planned hostname:

```text
request.robynshomelab.dev
```

Planned flow:

```text
Client
  │
  │ HTTPS
  ▼
Nginx
192.168.20.94
  │
  │ HTTP
  ▼
Seerr
CT103
```

The corresponding DNS record will be created in Pi-hole:

```text
request.robynshomelab.dev → 192.168.20.94
```

A TLS certificate will then be obtained through the existing Certbot/Cloudflare DNS setup.

The hostname and certificate should only be configured once Seerr has actually been deployed.

## Security Model

The media stack is intended to remain inside the homelab network.

The ISP router should not forward ports directly to:

```text
Seerr
Sonarr
Radarr
Prowlarr
Bazarr
qBittorrent
```

Instead, access should use:

```text
Internal DNS
Nginx
HTTPS
NetBird where remote private access is required
```

Administrative applications such as Prowlarr and qBittorrent should not be unnecessarily exposed.

## Future DNS

The planned internal DNS entry is:

```text
request.robynshomelab.dev → 192.168.20.94
```

Other media applications may receive hostnames later if there is a practical reason to access them through Nginx.

Examples could include:

```text
sonarr.robynshomelab.dev
radarr.robynshomelab.dev
prowlarr.robynshomelab.dev
bazarr.robynshomelab.dev
```

These are **not currently configured**.

There is no requirement for every internal application to have its own public DNS name.

## Monitoring

The media stack should eventually be added to Uptime Kuma and Beszel.

Uptime Kuma can monitor service availability:

```text
Seerr
Sonarr
Radarr
Prowlarr
Bazarr
qBittorrent
```

Beszel can monitor the CT103 system itself:

```text
CPU
Memory
Disk
Network
Temperature where available
```

The monitors should be added after the applications are actually deployed.

## Backup Considerations

The media library itself may become large and should not automatically be treated as a normal backup target.

The more important backup targets are:

```text
Application configuration
Database/configuration files
Service settings
Metadata
Custom scripts
NAS configuration
```

The exact backup strategy will be designed after the 9020 NAS is operational.

The media files and application configuration should be considered separately when designing backups.

## Deployment Order

The media stack should be deployed in stages rather than all at once.

Recommended order:

```text
1. Deploy and configure 9020 NAS
        │
        ▼
2. Create NAS filesystem/storage layout
        │
        ▼
3. Configure NFS exports
        │
        ▼
4. Mount NAS storage on CT103
        │
        ▼
5. Configure permissions
        │
        ▼
6. Deploy qBittorrent
        │
        ▼
7. Deploy Prowlarr
        │
        ▼
8. Deploy Sonarr and Radarr
        │
        ▼
9. Deploy Bazarr
        │
        ▼
10. Deploy Seerr
        │
        ▼
11. Integrate with Jellyfin
        │
        ▼
12. Configure Nginx/DNS/HTTPS
        │
        ▼
13. Add monitoring
```

This order deliberately puts storage first.

The media stack should not be built around temporary local storage on CT103.

## Current Status

The media stack is currently:

```text
Status: Planned
Container: CT103
Deployment: Not started
```

The following services are planned:

```text
Seerr
Sonarr
Radarr
Prowlarr
Bazarr
qBittorrent
```

The Dell OptiPlex 9020 will provide the planned NAS storage.

Jellyfin is already operational separately on CT102 and will eventually consume media from the NAS.

## Key Commands

No media-stack deployment commands are currently recorded because CT103 has not yet been deployed.

Once deployment begins, commands should be documented here as they are actually used.

Useful future checks will include:

```bash
# Check mounted NFS filesystems
findmnt -t nfs,nfs4

# Display mounted filesystems
df -h

# Check network connectivity to the NAS
ping <NAS-IP>

# Test NFS connectivity
showmount -e <NAS-IP>
```

The actual NAS IP and mount paths should be added to this documentation once the 9020 storage system has been configured.

## Related Documentation

The media stack depends on:

```text
01-hardware.md
02-network.md
03-proxmox.md
06-nginx.md
07-certbot.md
09-jellyfin.md
11-uptime-kuma.md
```

The NAS/storage documentation will be added when the Dell OptiPlex 9020 is configured.
