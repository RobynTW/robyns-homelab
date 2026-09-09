# Media Stack

The media stack runs on CT103 and provides automated media acquisition, organisation, and request management.

The stack is deployed using Docker Compose and integrates with the homelab's NFS-backed media storage and Jellyfin server.

---

# Container

```text
VMID:     103
Hostname: mediastack
IP:       192.168.20.93
Host:     pve-1
OS:       Debian 12 Bookworm
```

The container is an unprivileged LXC with nesting enabled to support Docker.

---

# Services

The current stack consists of:

| Service      | Port | Purpose                       |
| ------------ | ---: | ----------------------------- |
| qBittorrent  | 8080 | Download client               |
| Prowlarr     | 9696 | Indexer management            |
| Sonarr       | 8989 | TV and anime management       |
| Radarr       | 7878 | Movie management              |
| Bazarr       | 6767 | Subtitle management           |
| Seerr        | 5055 | Media request management      |
| FlareSolverr | 8191 | Cloudflare challenge handling |

The containers communicate using the Docker Compose network.

---

# Architecture

```text
                         User
                          │
                          ▼
                       Seerr
                    :5055 / CT103
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
          Radarr                    Sonarr
           :7878                     :8989
             │                         │
             └────────────┬────────────┘
                          │
                          ▼
                      Prowlarr
                       :9696
                          │
                          ▼
                    Indexer sources
                          │
                          ▼
                    qBittorrent
                       :8080
                          │
                          ▼
                  /mnt/downloads
                          │
                          ▼
                Media import/organisation
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
        /mnt/media/movies         /mnt/media/tv
             │                         │
             └────────────┬────────────┘
                          ▼
                       Jellyfin
                    CT102 .98:8096
```

---

# Storage Architecture

The media stack does not store the primary media library on the container's local virtual disk.

Media is stored on the physical 4TB WD Blue disk attached to pve-2.

The storage path is:

```text
pve-2
192.168.20.101
     │
     ▼
/mnt/homelab-data
     │
     ├── media
     │
     └── downloads
```

pve-2 exports these directories through NFS.

pve-1 mounts them locally:

```text
/mnt/homelab-media
/mnt/homelab-downloads
```

CT103 then receives them through LXC bind mounts:

```text
pve-1 /mnt/homelab-media
        │
        ▼
CT103 /mnt/media

pve-1 /mnt/homelab-downloads
        │
        ▼
CT103 /mnt/downloads
```

This provides a single media library shared between the media stack and other services.

---

# Storage Layout

The physical storage layout is:

```text
/mnt/homelab-data/
├── media/
│   ├── anime/
│   ├── books/
│   ├── movies/
│   ├── music/
│   └── tv/
├── downloads/
│   ├── incomplete/
│   └── complete/
├── games/
├── backups/
└── shared/
```

The media stack primarily uses:

```text
/mnt/media
/mnt/downloads
```

---

# Docker

Docker is installed from the official Docker repository.

Current components include:

```text
Docker Engine: 29.8.0
Docker Compose: 5.5.1
containerd:     2.3.5
runc:           1.5.1
```

The Docker environment uses overlayfs and systemd/cgroup v2.

---

# Compose Configuration

The stack is managed from its Docker Compose configuration.

Typical management commands are:

```bash
cd /opt/media-stack
```

Check service status:

```bash
docker compose ps
```

Start the stack:

```bash
docker compose up -d
```

Stop the stack:

```bash
docker compose down
```

Restart a service:

```bash
docker compose restart <service>
```

View logs:

```bash
docker compose logs -f <service>
```

---

# qBittorrent

qBittorrent is the download client.

```text
Port:       8080
Downloads:  /mnt/downloads
PUID:       1000
PGID:       1000
Timezone:   Australia/Melbourne
Config:     /opt/media-stack/config/qbittorrent
```

The download directory is:

```text
/mnt/downloads
```

with:

```text
/mnt/downloads/incomplete
/mnt/downloads/complete
```

---

# Prowlarr

Prowlarr manages indexers for the media applications.

```text
Port: 9696
```

Prowlarr is connected to:

* Radarr
* Sonarr

The current deployment has five configured indexers.

Three of the configured indexers are synchronised to Radarr because two are not movie-capable.

All configured indexers were verified as healthy during setup.

---

# FlareSolverr

FlareSolverr is available internally to Prowlarr:

```text
http://flaresolverr:8191
```

The Prowlarr proxy configuration is:

```text
Name: FlareSolverr
Tag:  flaresolverr
Host: http://flaresolverr:8191
```

Only indexers requiring FlareSolverr should be assigned the corresponding tag.

FlareSolverr is not intended to be used unnecessarily for indexers that work without it.

---

# Radarr

Radarr manages movies.

```text
Port: 7878
```

Media root:

```text
/mnt/media/movies
```

Downloads are available through:

```text
/mnt/downloads
```

The configured download client is qBittorrent.

Radarr is configured to:

* Monitor released movies
* Automatically search for requested/relevant releases
* Scan the movie library
* Import completed downloads
* Organise movies under `/mnt/media/movies`

---

# Sonarr

Sonarr manages television and anime.

```text
Port: 8989
```

Configured media roots:

```text
/mnt/media/tv
/mnt/media/anime
```

Downloads are available through:

```text
/mnt/downloads
```

Sonarr is configured to:

* Monitor released series
* Automatically search for relevant releases
* Scan configured libraries
* Import completed downloads
* Organise television and anime media

---

# Bazarr

Bazarr manages subtitles.

```text
Port: 6767
```

Media access:

```text
/mnt/media
```

Bazarr works alongside Sonarr and Radarr to manage subtitles for the corresponding media libraries.

---

# Seerr

Seerr provides the user-facing media request system.

```text
Port: 5055
```

Configuration:

```text
/opt/media-stack/config/seerr
```

The container runs using its own application configuration directory.

An initial permissions issue involving:

```text
/app/config/logs
```

was resolved by correcting ownership of:

```text
/opt/media-stack/config/seerr
```

to:

```text
1000:1000
```

Seerr is currently running version:

```text
3.4.1
```

---

# Seerr → Jellyfin

Seerr is integrated with Jellyfin.

Jellyfin:

```text
192.168.20.98:8096
```

No SSL is used for this internal service-to-service connection.

The integration allows Seerr to use Jellyfin's media library when processing requests.

---

# Seerr → Radarr

Radarr is configured in Seerr for movie requests.

The Radarr service is reached internally through the Docker network:

```text
radarr:7878
```

Radarr uses:

```text
/mnt/media/movies
```

as its movie root.

---

# Seerr → Sonarr

Sonarr is configured in Seerr for television requests.

The Sonarr service is reached internally through the Docker network:

```text
sonarr:8989
```

Configured roots include:

```text
/mnt/media/tv
/mnt/media/anime
```

---

# End-to-End Workflow

A typical movie request follows this path:

```text
User
 │
 ▼
Seerr
 │
 ▼
Radarr
 │
 ▼
Prowlarr
 │
 ▼
Indexer
 │
 ▼
qBittorrent
 │
 ▼
/mnt/downloads/complete
 │
 ▼
Radarr import
 │
 ▼
/mnt/media/movies
 │
 ▼
Jellyfin
```

The corresponding TV/anime path uses Sonarr.

---

# Verified Movie Workflow

The end-to-end movie workflow has been successfully tested.

A test request for:

```text
Disclosure Day (2026)
```

was successfully processed through the media stack.

The resulting file was:

```text
/mnt/media/movies/Disclosure Day (2026)/Disclosure Day (2026) [1080p] [WEBRip] [5.1].mp4
```

The file size was approximately:

```text
2.7 GB
```

This confirmed the following chain:

```text
Seerr
  ↓
Radarr
  ↓
Prowlarr
  ↓
Indexer
  ↓
qBittorrent
  ↓
Download
  ↓
Radarr import
  ↓
Media library
```

---

# Permissions

The NFS media and download shares on pve-2 use:

```text
UID: 999
GID: 990
```

The corresponding `mediastack` account on pve-2 owns the shared media/download data.

The directories are configured with group inheritance using mode:

```text
2775
```

This allows files created within the shared directories to retain the intended group.

---

# NFS Shares

pve-2 currently exports the media stack's required shares separately.

Media:

```text
/mnt/homelab-data/media
```

Downloads:

```text
/mnt/homelab-data/downloads
```

The exports use restricted client addresses rather than exposing the entire LAN unnecessarily.

The current architecture intentionally uses separate exports for separate purposes.

---

# Download and Import Paths

The download directory should remain separate from the final media library.

```text
Downloads:

/mnt/downloads/
├── incomplete/
└── complete/


Media:

/mnt/media/
├── anime/
├── books/
├── movies/
├── music/
└── tv/
```

Completed downloads are imported into their appropriate media library rather than being treated as the permanent media location.

---

# Service Dependencies

The stack has several dependencies:

```text
NFS storage
    │
    ▼
/mnt/media + /mnt/downloads
    │
    ├── qBittorrent
    ├── Sonarr
    ├── Radarr
    └── Bazarr

Prowlarr
    │
    ├── Indexers
    └── FlareSolverr

Seerr
    │
    ├── Radarr
    ├── Sonarr
    └── Jellyfin
```

A failure of NFS storage can therefore affect multiple applications simultaneously.

---

# Troubleshooting

## Check Containers

```bash
docker compose ps
```

All expected services should show as running.

---

## Check Logs

For a specific service:

```bash
docker compose logs -f <service>
```

For example:

```bash
docker compose logs -f radarr
```

---

## Check Storage

```bash
df -h /mnt/media
df -h /mnt/downloads
```

Check mounts:

```bash
findmnt /mnt/media
findmnt /mnt/downloads
```

---

## Test Media Access

```bash
ls -lah /mnt/media
ls -lah /mnt/downloads
```

If these fail, investigate the NFS/bind-mount chain before troubleshooting the Docker applications.

---

## Check Docker

```bash
docker info
```

Check containers:

```bash
docker ps
```

Check Compose configuration:

```bash
docker compose config
```

---

# NFS Failure Considerations

The media stack depends on:

```text
pve-2
  ↓
NFS
  ↓
pve-1
  ↓
LXC bind mount
  ↓
CT103
```

If NFS becomes unavailable, applications may report missing libraries, failed imports, or filesystem errors.

Do not immediately recreate the Docker containers.

First verify:

```bash
findmnt /mnt/media
findmnt /mnt/downloads
```

and then verify the NFS mounts on pve-1.

---

# Operational Principles

The current media stack follows these principles:

* Runs on CT103
* Uses Docker Compose
* Uses NFS-backed storage
* Keeps downloads separate from the final media library
* Uses Prowlarr as the indexer manager
* Uses qBittorrent as the download client
* Uses Radarr for movies
* Uses Sonarr for TV and anime
* Uses Bazarr for subtitles
* Uses Seerr for requests
* Uses FlareSolverr only where required
* Integrates with Jellyfin
* Uses internal Docker service names where appropriate
* Does not require router port forwarding

---

# Future Improvements

Potential future work includes:

* Automated Jellyfin library refresh
* More comprehensive health monitoring
* Backup of application configuration
* Improved storage monitoring
* Additional media quality profiles
* Additional subtitle configuration
* More detailed download/import automation
* Integration with the existing monitoring stack

Any future configuration should preserve the separation between:

```text
downloads
media library
application configuration
```

to keep the storage architecture predictable and recoverable.
