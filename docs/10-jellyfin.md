# Jellyfin

Jellyfin is the homelab's primary media server.

It runs in CT102 and provides streaming access to the media stored on the shared homelab storage.

---

# Container

```text
VMID:     102
Hostname: jellyfin
IP:       192.168.20.98
Host:     pve-1
```

CT102 runs Jellyfin on Debian 12 Bookworm.

Current Jellyfin version:

```text
10.11.11.0
```

Installed packages include:

```text
jellyfin
jellyfin-server
jellyfin-web
jellyfin-ffmpeg7
```

---

# Architecture

```text
                         Homelab Storage
                              │
                              │ NFS
                              ▼
                         pve-2 .101
                              │
                              ▼
                         pve-1 .100
                              │
                              ▼
                         CT102 .98
                          Jellyfin
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
             Clients                    Seerr
```

Jellyfin accesses the shared media through the NFS storage mounted on pve-1.

---

# Media Storage

The primary media storage is the 4TB WD Blue drive installed in pve-2.

The NFS architecture is:

```text
pve-2
192.168.20.101
    │
    │ NFS
    ▼
pve-1
192.168.20.100
    │
    │ bind mount
    ▼
CT102
192.168.20.98
```

On pve-1, the media share is mounted at:

```text
/mnt/homelab-media
```

CT102 receives this as:

```text
/mnt/media
```

---

# Media Layout

The current storage layout is:

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

Jellyfin primarily uses:

```text
/mnt/media/
├── anime/
├── books/
├── movies/
├── music/
└── tv/
```

---

# Library Organisation

The Jellyfin libraries correspond to the media directories.

The intended structure is:

| Library | Path                |
| ------- | ------------------- |
| Anime   | `/mnt/media/anime`  |
| Books   | `/mnt/media/books`  |
| Movies  | `/mnt/media/movies` |
| Music   | `/mnt/media/music`  |
| TV      | `/mnt/media/tv`     |

Only the libraries that have been configured in Jellyfin should be considered active.

---

# NFS Storage

The media share is exported from pve-2 using NFS.

The relevant export is:

```text
/mnt/homelab-data/media
```

The export is available to pve-1 and the desktop system.

pve-1 then provides the storage to CT102 through its NFS mount and LXC bind mount.

This avoids giving CT102 direct access to the physical disk.

---

# Media Access Path

A typical media file request follows this path:

```text
Jellyfin client
      │
      ▼
Jellyfin CT102
192.168.20.98
      │
      ▼
/mnt/media
      │
      ▼
pve-1 /mnt/homelab-media
      │
      ▼
NFS
      │
      ▼
pve-2 /mnt/homelab-data/media
      │
      ▼
4TB WD Blue
```

---

# Reverse Proxy

Nginx provides the HTTPS endpoint:

```text
https://jellyfin.robynshomelab.dev
```

The internal DNS record resolves the hostname to:

```text
192.168.20.94
```

Nginx then proxies the request to:

```text
192.168.20.98:8096
```

The complete path is:

```text
Client
  │
  ▼
Pi-hole
  │
  ▼
192.168.20.94
  │
  ▼
Nginx
  │
  ▼
192.168.20.98:8096
  │
  ▼
Jellyfin
```

---

# Remote Access

Remote access is provided through NetBird.

CT101 routes:

```text
192.168.20.94/32
```

to NetBird clients.

A remote client can therefore use:

```text
https://jellyfin.robynshomelab.dev
```

The DNS path is:

```text
NetBird client
      │
      ▼
Pi-hole
192.168.20.99
      │
      ▼
192.168.20.94
      │
      ▼
Nginx
      │
      ▼
Jellyfin
192.168.20.98
```

There is currently no router port forwarding for Jellyfin.

---

# Seerr Integration

Jellyfin is integrated with Seerr running on CT103.

Seerr is available at:

```text
http://192.168.20.93:5055
```

The Jellyfin server URL configured for Seerr is:

```text
http://192.168.20.98:8096
```

The public server URL configured for the integration is:

```text
http://192.168.20.98:8096
```

Seerr is responsible for media requests, while Jellyfin provides playback.

---

# Moonbase

Moonbase is installed manually because it was not available through the Jellyfin plugin catalogue.

Installation location:

```text
/var/lib/jellyfin/plugins/Moonbase
```

Current release:

```text
2.2.0.0
```

Moonbase Sync is enabled.

Jellyfin was restarted after installation and the plugin loaded successfully.

---

# Moonfin

Moonfin is used as a Jellyfin client on Android TV.

The current setup has been tested successfully.

The general architecture is:

```text
Android TV
    │
    ▼
Moonfin
    │
    ▼
Jellyfin
192.168.20.98
```

---

# Media Requests

The media request workflow is:

```text
User
 │
 ▼
Seerr
 │
 ├── Request movie
 │
 └── Request TV/anime
 │
 ▼
Media automation stack
 │
 ├── Radarr
 │
 └── Sonarr
 │
 ▼
Download
 │
 ▼
Media storage
 │
 ▼
Jellyfin
 │
 ▼
Client
```

The media automation stack runs separately in CT103.

---

# Verified Media Workflow

The end-to-end movie workflow has been tested successfully.

A test movie was imported:

```text
Disclosure Day (2026)
```

The resulting file was:

```text
/mnt/media/movies/Disclosure Day (2026)/
└── Disclosure Day (2026) [1080p] [WEBRip] [5.1].mp4
```

File size at the time of testing was approximately:

```text
2.7 GB
```

This confirmed that the media automation stack could successfully deliver media to Jellyfin's storage.

---

# Jellyfin Refresh

Jellyfin does not currently have an automated filesystem refresh configured.

A manual library scan can therefore be initiated from the Jellyfin interface when required.

A future API-based refresh can be performed using Jellyfin's `/Library/Refresh` endpoint.

Example:

```bash
curl -fsS \
  -X POST \
  -H "X-Emby-Token: ${JELLYFIN_API_KEY}" \
  "http://192.168.20.98:8096/Library/Refresh"
```

The API key must not be stored in this repository.

---

# NFS Stale Handle Incident

A previous NFS export change caused Jellyfin to encounter a stale NFS file handle.

The issue was resolved by:

1. Stopping CT102
2. Remounting the media share on pve-1
3. Restarting CT102
4. Scanning the Jellyfin library

The current NFS configuration has been corrected to use per-share exports.

The issue should only be revisited if stale NFS handles recur.

---

# Troubleshooting

## Check Jellyfin Service

On CT102:

```bash
systemctl status jellyfin
```

---

## Check Jellyfin Version

```bash
jellyfin --version
```

If that command is unavailable, check the installed package version:

```bash
dpkg -l | grep jellyfin
```

---

## Check Listening Port

```bash
ss -lntp | grep 8096
```

Jellyfin should be listening on:

```text
192.168.20.98:8096
```

---

## Test Locally

From CT102:

```bash
curl -I http://127.0.0.1:8096
```

From another LAN host:

```bash
curl -I http://192.168.20.98:8096
```

---

# Check Media Mount

On CT102:

```bash
mount | grep /mnt/media
```

Then:

```bash
ls -lah /mnt/media
```

The expected directories include:

```text
anime
books
movies
music
tv
```

---

# Check NFS Path

On pve-1:

```bash
mount | grep homelab-media
```

Then:

```bash
ls -lah /mnt/homelab-media
```

On pve-2:

```bash
mount | grep homelab-data
```

Then:

```bash
ls -lah /mnt/homelab-data/media
```

---

# Reverse Proxy Troubleshooting

If Jellyfin works directly but not through HTTPS, test:

```bash
curl -I http://192.168.20.98:8096
```

Then verify the Nginx endpoint:

```bash
curl -I https://jellyfin.robynshomelab.dev
```

Check DNS:

```bash
dig @192.168.20.99 jellyfin.robynshomelab.dev
```

The internal result should be:

```text
192.168.20.94
```

---

# NFS Performance Considerations

Jellyfin's media files are stored on the 4TB WD Blue HDD.

The current architecture prioritises storage capacity and centralised media access rather than maximum disk performance.

The NFS path adds network overhead:

```text
Jellyfin
   │
   ▼
pve-1
   │
   ▼
NFS
   │
   ▼
pve-2 HDD
```

This is suitable for the current homelab workload.

---

# Security

Jellyfin is not directly exposed through router port forwarding.

Access is provided through:

* LAN access
* Nginx reverse proxy
* HTTPS
* NetBird remote access

The backend Jellyfin port:

```text
8096
```

should remain an internal service port.

---

# Operational Principles

The current Jellyfin deployment follows these principles:

* Jellyfin runs in CT102
* Media is stored on pve-2
* Media is provided through NFS
* pve-1 provides the LXC bind mount
* Nginx provides HTTPS
* Pi-hole provides internal split DNS
* NetBird provides remote private access
* Seerr handles media requests
* Moonbase provides additional Jellyfin functionality
* Moonfin is used as an Android TV client
* No router port forwarding is required

---

# Future Improvements

Potential future improvements include:

* Automated Jellyfin library refreshes
* Additional Jellyfin clients
* Hardware transcoding if suitable hardware becomes available
* Improved media monitoring
* Jellyfin configuration backups
* Additional storage capacity
* Storage redundancy
* Monitoring of Jellyfin and NFS performance

Any future changes should be documented after deployment and verification.
