# Gluetun and Bazarr+

Documentation for the VPN-routed qBittorrent configuration and the migration from standard Bazarr to Bazarr+ on CT103.

---

## Overview

The media stack on CT103 uses Gluetun as the VPN network namespace for qBittorrent.

The important design principle is:

```text
qBittorrent
    │
    │ network_mode: service:gluetun
    ▼
Gluetun
    │
    ├── VPN tunnel
    └── published WebUI port 8080
```

qBittorrent does not have its own Docker network namespace. Its network traffic is forced through Gluetun.

The other media applications — Prowlarr, Sonarr, Radarr, Bazarr+, Seerr and FlareSolverr — remain on the normal Docker Compose network.

No VPN credentials or private configuration values are stored in this repository.

---

# Gluetun

## Purpose

Gluetun provides the VPN network namespace used by qBittorrent.

This keeps the download client isolated from the normal Docker network path while still allowing the rest of the media stack to communicate with qBittorrent through Gluetun.

The architecture is:

```text
Internet
   │
   ▼
VPN provider
   │
   ▼
Gluetun
   │
   └── qBittorrent
```

qBittorrent uses:

```yaml
network_mode: service:gluetun
```

This means qBittorrent shares Gluetun's network namespace.

---

## Container

The Gluetun container is part of the CT103 Docker Compose deployment.

The container currently receives the qBittorrent WebUI port:

```text
Host:      8080
Container: 8080
```

The WebUI is therefore reached through Gluetun rather than through a separately published qBittorrent container port.

Local access:

```text
http://192.168.20.93:8080
```

The WebUI returns qBittorrent 5.2.3.

---

## Docker Networking

The relevant relationship is:

```text
Docker host
192.168.20.93
       │
       ▼
Gluetun
172.18.0.6
       │
       │ shared network namespace
       ▼
qBittorrent
```

Other Docker services can reach qBittorrent through the Gluetun endpoint.

Examples:

```text
gluetun:8080
192.168.20.93:8080
```

The media applications use the WebUI through this exposed Gluetun port.

---

## qBittorrent Dependency

qBittorrent must remain attached to Gluetun's network namespace.

Do not add a normal `ports:` mapping directly to qBittorrent when using:

```yaml
network_mode: service:gluetun
```

Port publishing belongs on Gluetun.

This prevents accidentally bypassing the VPN network namespace.

---

## VPN Configuration

The VPN provider, country/server selection, authentication, and other sensitive Gluetun settings are supplied through the deployment configuration/environment.

Secrets must never be committed to Git.

The public documentation intentionally does not contain:

- VPN usernames
- VPN passwords
- WireGuard private keys
- OpenVPN credentials
- VPN account tokens
- provider-specific authentication secrets

---

## Operational Checks

Check the container:

```bash
docker compose ps gluetun
```

Check Gluetun logs:

```bash
docker compose logs -f gluetun
```

Check qBittorrent:

```bash
docker compose ps qbittorrent
```

Check qBittorrent logs:

```bash
docker compose logs -f qbittorrent
```

The expected relationship is that Gluetun is healthy/running and qBittorrent is running with:

```text
network_mode = service:gluetun
```

---

# Bazarr+

## Why Bazarr+

Bazarr was migrated from the LinuxServer Bazarr image to Bazarr+ to provide access to the additional Provider Hub subtitle providers.

The migration was performed without replacing the existing Bazarr configuration.

The existing configuration directory was backed up before the image change.

---

## Container

Bazarr+ currently uses:

```text
Image:  ghcr.io/lavx/bazarr:latest
Port:   6767
```

The container is managed by the existing Docker Compose project:

```text
/opt/media-stack
```

The application remains available at:

```text
http://192.168.20.93:6767
```

Bazarr+ currently reports version:

```text
2.6.2
```

---

## Migration Method

The original container used:

```text
lscr.io/linuxserver/bazarr:latest
```

The replacement image is:

```text
ghcr.io/lavx/bazarr:latest
```

The migration was implemented with a Compose override:

```yaml
services:
  bazarr:
    image: ghcr.io/lavx/bazarr:latest
```

The override is stored at:

```text
/opt/media-stack/bazarr-plus.override.yml
```

The existing Bazarr configuration directory was retained:

```text
/opt/media-stack/config/bazarr
```

A backup was created before migration.

The migration therefore changed the application image without rebuilding the application configuration from scratch.

---

# Bazarr+ Provider Hub

Bazarr+ provides a Provider Hub system for additional subtitle providers.

Installed providers currently include:

- Kitsunekko
- SubDL
- SubtitleCat
- TVsubtitles
- OpenSubtitles.org

OpenSubtitles.com remains configured through Bazarr's built-in provider integration.

Provider Hub plugins must be both installed and enabled as search providers before Bazarr will use them.

Installing a Provider Hub plugin alone does not make it active.

---

## Current Subtitle Providers

The primary providers of interest for English anime subtitles are:

### OpenSubtitles.com

OpenSubtitles.com remains an important provider for the library.

It is especially useful when subtitles are available for newer or less widely mirrored anime releases.

The provider has rate limits, so temporary throttling can occur.

---

### Kitsunekko

Kitsunekko is enabled through Provider Hub and is particularly useful for anime subtitles.

Source:

```text
https://kitsunekko.net/dirlist.php?dir=subtitles%2F
```

---

### SubDL

SubDL is enabled through Provider Hub and provides an additional subtitle source.

It can be useful as a secondary provider when OpenSubtitles is throttled or does not return a suitable result.

---

### SubtitleCat

SubtitleCat is installed through Provider Hub.

The provider has previously experienced request timeouts and may be temporarily throttled by Bazarr.

It should not be treated as a guaranteed provider.

---

### TVsubtitles

TVsubtitles is installed through Provider Hub.

The provider has previously returned HTTP 404 responses for some searches and may be temporarily throttled.

It should not be treated as a guaranteed provider.

---

### OpenSubtitles.org

OpenSubtitles.org is a separate provider from OpenSubtitles.com.

The OpenSubtitles.org integration has previously experienced scraper/service errors and is not the primary provider for the current setup.

If it is removed in the future, this does not affect the OpenSubtitles.com integration.

---

# Bazarr+ Language Configuration

The active subtitle language profile is English.

Bazarr is configured to manage subtitles for the anime library.

The current setup permits fansub subtitles where they meet the configured language and score requirements.

Automatic subtitle downloading is enabled.

The minimum accepted subtitle score was previously reduced from 90% to 80% because suitable OpenSubtitles results were commonly returned around the mid-80% range.

---

# Provider Throttling

Bazarr can temporarily throttle providers when a provider:

- reaches a rate limit
- becomes unavailable
- times out
- returns repeated HTTP errors

For example, OpenSubtitles.com has previously reached its daily subtitle limit.

When a provider is throttled, Bazarr can continue attempting searches against other enabled providers.

This is one of the reasons multiple providers are configured.

Provider-side throttling should not automatically be interpreted as a Bazarr failure.

---

# Bazarr+ and Sonarr/Radarr

Bazarr+ remains integrated with the existing media applications.

```text
Sonarr ──────┐
             │
             ▼
           Bazarr+
             │
             ▼
        Subtitle providers
```

Bazarr continues to use the existing media paths:

```text
/mnt/media
```

Because the Docker containers use the same media paths, subtitle files discovered by Bazarr are written directly alongside the corresponding media.

---

# Backup and Recovery

The Bazarr configuration was backed up before the Bazarr+ migration.

The backup is stored outside the active configuration directory.

If the Bazarr+ image needs to be reverted, the original LinuxServer image can be restored using the existing Compose deployment and the retained configuration.

Before making major changes, create another configuration backup.

Example:

```bash
cd /opt/media-stack
tar -czf config/bazarr-backup-$(date +%Y%m%d-%H%M%S).tar.gz config/bazarr
```

Do not commit the resulting archive to GitHub.

---

# Management

From CT103:

```bash
cd /opt/media-stack
```

Check status:

```bash
docker compose ps
```

Check Bazarr+:

```bash
docker compose logs -f bazarr
```

Restart Bazarr+:

```bash
docker compose restart bazarr
```

Recreate the service after an image/configuration change:

```bash
docker compose up -d bazarr
```

---

# Known Provider Issues

The following issues have been observed and should not be confused with a failure of the Bazarr+ installation itself:

```text
AniDB API
    → API client unavailable/disabled errors observed

OpenSubtitles.org
    → scraper/service availability errors observed

OpenSubtitles.com
    → rate limiting/daily quota can temporarily throttle requests

SubtitleCat
    → request timeouts observed

TVsubtitles
    → HTTP 404 responses observed
```

Bazarr+ itself is operational and connected to Sonarr and Radarr.

---

# Security

Never commit:

- VPN credentials
- WireGuard private keys
- OpenVPN credentials
- Bazarr API keys
- OpenSubtitles credentials
- SubDL API keys
- session cookies
- application secrets

This document describes the architecture and configuration without exposing credentials.

---

# Current Status

```text
Gluetun              DEPLOYED / VERIFIED
qBittorrent VPN path DEPLOYED / VERIFIED
qBittorrent WebUI    DEPLOYED / VERIFIED
Bazarr+              DEPLOYED / VERIFIED
Sonarr integration   DEPLOYED / VERIFIED
Radarr integration   DEPLOYED / VERIFIED
English subtitles    CONFIGURED
Automatic downloads  ENABLED
```

The media stack can continue operating if an individual subtitle provider becomes temporarily unavailable because multiple providers are configured.

