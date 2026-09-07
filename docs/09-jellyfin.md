# Jellyfin Media Server

## Overview

Jellyfin is the homelab's media server.

It currently runs in a dedicated Proxmox LXC:

```text
Proxmox pve-1
└── CT102
    ├── Hostname: jellyfin
    ├── IP: 192.168.20.98
    ├── 4 vCPU
    ├── 4 GB RAM
    ├── 32 GB root disk
    ├── 512 MB swap
    └── Intel iGPU passthrough
        └── /dev/dri/renderD128
```

Jellyfin is intentionally kept separate from the future media-management stack and NAS.

The current architecture is:

```text
                    Nginx
               192.168.20.94
                      │
                      │ HTTPS
                      ▼
                  Jellyfin
               192.168.20.98
                      │
                      │ future NFS
                      ▼
               Dell OptiPlex 9020
                    NAS
```

The 9020 NAS and media-management stack are planned but are not yet connected.

## Operating System

CT102 runs:

```text
Debian 12 Bookworm
```

The container is unprivileged.

The container has:

```text
4 vCPU
4 GB RAM
32 GB root filesystem
512 MB swap
```

The root filesystem is intended for the operating system and Jellyfin application rather than the eventual media library.

## Jellyfin Version

The current installed Jellyfin version is:

```text
10.11.11+deb12
```

Check the installed package:

```bash
dpkg -l | grep jellyfin
```

Check the service:

```bash
systemctl status jellyfin
```

## Network

Jellyfin has a static LAN address:

```text
192.168.20.98
```

The native Jellyfin HTTP service listens on:

```text
8096/tcp
```

The service is accessed locally through:

```text
http://192.168.20.98:8096
```

External-facing access within the homelab uses the Nginx reverse proxy instead:

```text
https://jellyfin.robynshomelab.dev
```

## Reverse Proxy

Nginx runs separately in CT106:

```text
CT106
192.168.20.94
```

Nginx terminates HTTPS and proxies requests to Jellyfin:

```text
Client
  │
  │ HTTPS
  ▼
Nginx
192.168.20.94:443
  │
  │ HTTP
  ▼
Jellyfin
192.168.20.98:8096
```

The Nginx configuration includes WebSocket support and extended proxy timeouts because Jellyfin maintains long-lived connections.

The relevant hostname is:

```text
jellyfin.robynshomelab.dev
```

The TLS certificate is managed by Certbot.

See:

```text
06-nginx.md
07-certbot.md
```

for the reverse-proxy and certificate configuration.

## Internal DNS

Pi-hole provides the internal DNS record:

```text
jellyfin.robynshomelab.dev → 192.168.20.94
```

The request therefore resolves to Nginx rather than directly to the Jellyfin container.

The flow is:

```text
Client
  │
  │ DNS
  ▼
Pi-hole
192.168.20.99
  │
  │ 192.168.20.94
  ▼
Nginx
192.168.20.94
  │
  │ proxy
  ▼
Jellyfin
192.168.20.98:8096
```

This provides a consistent hostname for local and NetBird-connected clients.

## Hardware Acceleration

The Jellyfin container has access to the Intel integrated GPU from the Proxmox host.

The exposed render device is:

```text
/dev/dri/renderD128
```

The Proxmox LXC configuration contains:

```text
dev0: /dev/dri/renderD128,gid=104,mode=0660
```

The underlying processor is an:

```text
Intel Core i5-8500T
```

with:

```text
Intel UHD Graphics 630
```

## VA-API

VA-API is available inside the Jellyfin container.

The Intel media driver is:

```text
iHD
```

Hardware acceleration was verified with:

```bash
vainfo
```

The successful `vainfo` output confirms that the Intel VA-API stack is available to the container.

The relevant architecture is:

```text
Proxmox host
    │
    │ /dev/dri/renderD128
    ▼
Jellyfin LXC
    │
    ▼
VA-API
    │
    ▼
Intel iHD driver
    │
    ▼
Intel UHD 630
```

## Why Hardware Acceleration Is Used

Hardware acceleration allows compatible video transcoding operations to be handled by the Intel iGPU rather than entirely by the CPU.

This is particularly useful when:

* a client cannot direct-play a video
* video codecs need to be converted
* resolution needs to be changed
* bitrate needs to be reduced for a client
* multiple streams require transcoding

Direct play remains preferable whenever the client supports the source media.

Hardware acceleration should therefore reduce CPU load during transcoding rather than being treated as a replacement for direct play.

## FFmpeg

The installed FFmpeg version is:

```text
7.1.4-3-bookworm
```

Check it with:

```bash
ffmpeg -version
```

Jellyfin uses FFmpeg for media processing and transcoding.

## Jellyfin Service

Check Jellyfin:

```bash
systemctl status jellyfin
```

Start Jellyfin:

```bash
systemctl start jellyfin
```

Restart Jellyfin:

```bash
systemctl restart jellyfin
```

Enable it at boot:

```bash
systemctl enable jellyfin
```

Check whether it is enabled:

```bash
systemctl is-enabled jellyfin
```

## Checking the Listening Port

Check whether Jellyfin is listening:

```bash
ss -tlnp | grep 8096
```

Expected listener:

```text
192.168.20.98:8096
```

Depending on the Jellyfin configuration, it may listen on all local interfaces rather than only the specific LAN address.

## Testing Jellyfin Directly

From another homelab host:

```bash
curl -I http://192.168.20.98:8096
```

A valid HTTP response confirms that Jellyfin is reachable.

From CT106, test the backend:

```bash
curl -I http://192.168.20.98:8096
```

If this fails, Nginx cannot successfully proxy requests to Jellyfin.

## Testing Through Nginx

Test the HTTPS endpoint:

```bash
curl -I https://jellyfin.robynshomelab.dev
```

A redirect response from Jellyfin is normal.

The Nginx virtual host can also be tested directly from CT106:

```bash
curl -Ik \
    -H "Host: jellyfin.robynshomelab.dev" \
    https://127.0.0.1
```

The current configuration returns a Jellyfin response with a redirect to:

```text
web/
```

This confirms that:

1. Nginx is listening.
2. The correct virtual host is selected.
3. The TLS certificate is being served.
4. Nginx can reach Jellyfin.
5. Jellyfin is responding.

## Jellyfin Logs

View recent Jellyfin service logs:

```bash
journalctl -u jellyfin --no-pager
```

Follow the logs live:

```bash
journalctl -u jellyfin -f
```

Depending on the Jellyfin installation, application logs are also available within the Jellyfin data directory.

## Checking GPU Access

Check the DRM devices:

```bash
ls -l /dev/dri/
```

Expected device:

```text
renderD128
```

Check the device from inside the container:

```bash
stat /dev/dri/renderD128
```

Check VA-API:

```bash
vainfo
```

If `vainfo` fails, check:

```bash
ls -l /dev/dri/
id
```

The Jellyfin process must have the permissions required to access the render device.

## Proxmox LXC Configuration

The relevant device passthrough configuration is:

```text
dev0: /dev/dri/renderD128,gid=104,mode=0660
```

This allows the container to access the Intel render device without passing through the entire PCI device.

The container remains an unprivileged LXC.

## Storage

The current Jellyfin root filesystem is:

```text
32 GB
```

This is not intended to hold the eventual media collection.

The long-term storage architecture is planned around the Dell OptiPlex 9020.

The planned arrangement is:

```text
Dell OptiPlex 9020
      │
      │ NAS
      ▼
    NFS
      │
      ▼
Jellyfin CT102
192.168.20.98
```

The 9020 will provide the bulk storage while Jellyfin remains on the 3060.

This keeps compute and media storage separate.

## Future Media Stack

The future media-management stack will run separately in CT103.

Planned applications include:

```text
Sonarr
Radarr
Prowlarr
Bazarr
qBittorrent
Jellyseerr
```

The planned media flow is:

```text
Jellyseerr
    │
    ├── Sonarr
    └── Radarr
          │
          ▼
       Prowlarr
          │
          ▼
      qBittorrent
          │
          ▼
      9020 NAS
          │
          ▼
       Jellyfin
```

CT103 is currently reserved for this future stack and has not yet been deployed as a media-management environment.

## Future NAS Integration

The Dell OptiPlex 9020 will eventually provide the media storage.

The intended sequence is:

```text
1. Configure 9020 storage
2. Deploy NAS software
3. Create NFS share
4. Mount NFS storage on the 3060
5. Configure Jellyfin to use the NAS
6. Deploy the media-management stack
```

No temporary media directory structure should be created on the Jellyfin root disk solely to avoid later migration work.

## Security

Jellyfin is not intended to be directly exposed through router port forwarding.

Access is provided through the internal Nginx reverse proxy and, for remote private access, through NetBird.

The current architecture is:

```text
Local client
    │
    ▼
Pi-hole DNS
    │
    ▼
Nginx
    │
    ▼
Jellyfin

Remote private client
    │
    ▼
NetBird
    │
    ▼
Pi-hole / Nginx
    │
    ▼
Jellyfin
```

The ISP router does not need a public port forward for Jellyfin.

## Troubleshooting

### Jellyfin is not running

Check:

```bash
systemctl status jellyfin
```

Restart:

```bash
systemctl restart jellyfin
```

Then inspect:

```bash
journalctl -u jellyfin --no-pager
```

### Port 8096 is unreachable

Check the listener:

```bash
ss -tlnp | grep 8096
```

Test locally:

```bash
curl -I http://127.0.0.1:8096
```

Test using the container's LAN address:

```bash
curl -I http://192.168.20.98:8096
```

### Nginx returns an error

Test the backend from CT106:

```bash
curl -I http://192.168.20.98:8096
```

If the backend works, check Nginx:

```bash
nginx -t
systemctl status nginx
```

Then inspect Nginx logs:

```bash
journalctl -u nginx --no-pager
```

### Hardware acceleration is unavailable

Check:

```bash
ls -l /dev/dri/
```

Then:

```bash
vainfo
```

If `/dev/dri/renderD128` is missing, inspect the LXC configuration from the Proxmox host.

The configuration should include:

```text
dev0: /dev/dri/renderD128,gid=104,mode=0660
```

### Transcoding uses too much CPU

Check whether the client is direct-playing or transcoding.

Then verify GPU access:

```bash
vainfo
```

The Jellyfin dashboard can also be used to determine whether a stream is being transcoded and which hardware acceleration method is being used.

## Key Commands

| Command                                      | Purpose                              |
| -------------------------------------------- | ------------------------------------ |
| `systemctl status jellyfin`                  | Check Jellyfin service               |
| `systemctl restart jellyfin`                 | Restart Jellyfin                     |
| `systemctl enable jellyfin`                  | Enable Jellyfin at boot              |
| `systemctl is-enabled jellyfin`              | Check boot-time enablement           |
| `ss -tlnp \| grep 8096`                      | Check Jellyfin listener              |
| `curl -I http://192.168.20.98:8096`          | Test Jellyfin directly               |
| `curl -I https://jellyfin.robynshomelab.dev` | Test HTTPS access through Nginx      |
| `vainfo`                                     | Verify VA-API and Intel media driver |
| `ls -l /dev/dri/`                            | Check GPU device access              |
| `ffmpeg -version`                            | Show installed FFmpeg version        |
| `journalctl -u jellyfin --no-pager`          | View Jellyfin logs                   |
| `journalctl -u jellyfin -f`                  | Follow Jellyfin logs                 |
| `nginx -t`                                   | Validate Nginx configuration         |

## Current State

Jellyfin is operational on CT102.

```text
CT102 jellyfin
├── Debian 12
├── 192.168.20.98
├── 4 vCPU
├── 4 GB RAM
├── Jellyfin 10.11.11
├── FFmpeg 7.1.4
└── Intel UHD 630
    └── VA-API / iHD
```

HTTPS access is provided through CT106:

```text
https://jellyfin.robynshomelab.dev
```

The Intel iGPU is successfully exposed to the container and VA-API has been verified.

The eventual media library will reside on the Dell OptiPlex 9020 NAS rather than the Jellyfin container's root filesystem.
