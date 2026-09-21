# AI Handover Update — 2026-09-21

This document is a **continuity addendum** to `.ai-homelab-context.md`.

The existing AI context file contains the broader canonical architecture. This addendum records changes completed after its previous dated state and should be read alongside it for future sessions.

---

## 1. Current repository state

GitHub repository:

```text
RobynTW/robyns-homelab
```

Default branch:

```text
main
```

The GitHub integration is now confirmed to have repository access.

Recent documentation commits include:

```text
f7dc522  Add Gluetun and Bazarr+ documentation
a090df9  Update README for Gluetun and Bazarr+ documentation
```

---

## 2. Media stack — current state

CT103 remains:

```text
mediastack
192.168.20.93
Debian 12
Docker Compose
```

Current media services:

```text
Gluetun
qBittorrent
Prowlarr
Sonarr
Radarr
Bazarr+
Seerr
FlareSolverr
```

The human documentation for this configuration is:

```text
docs/13-media-stack.md
docs/16-gluetun-bazarr-plus.md
```

---

## 3. Gluetun — DEPLOYED / VERIFIED

Gluetun is now part of the CT103 media stack.

Its purpose is to provide the VPN network namespace for qBittorrent.

The critical relationship is:

```text
Gluetun
   │
   │ shared Docker network namespace
   ▼
qBittorrent
```

qBittorrent uses:

```yaml
network_mode: service:gluetun
```

Therefore qBittorrent must not receive an independent Docker port mapping that bypasses Gluetun.

The qBittorrent WebUI is exposed through Gluetun on:

```text
192.168.20.93:8080
```

The observed Gluetun Docker address during configuration was:

```text
172.18.0.6
```

Other media services can reach qBittorrent through the Gluetun network endpoint.

### Important future troubleshooting rule

If qBittorrent loses connectivity:

1. Check Gluetun first.
2. Check the VPN tunnel/status.
3. Check Gluetun logs.
4. Check qBittorrent's shared network namespace.
5. Do not immediately rebuild qBittorrent.

The VPN credentials and provider-specific secrets are intentionally not documented.

---

## 4. qBittorrent — current networking

qBittorrent remains the download client.

WebUI:

```text
8080
```

Downloads:

```text
/mnt/downloads/incomplete
/mnt/downloads/complete
```

The WebUI is published by Gluetun because qBittorrent shares Gluetun's network namespace.

This is intentional.

Do not move the `ports:` mapping from Gluetun onto qBittorrent without deliberately redesigning the VPN architecture.

---

## 5. Bazarr → Bazarr+ migration — DEPLOYED / VERIFIED

Bazarr was successfully migrated from the LinuxServer image to Bazarr+.

Previous image:

```text
lscr.io/linuxserver/bazarr:latest
```

Current image:

```text
ghcr.io/lavx/bazarr:latest
```

Current Bazarr+ version observed:

```text
2.6.2
```

Port:

```text
6767
```

The existing application configuration was retained.

Configuration directory:

```text
/opt/media-stack/config/bazarr
```

A configuration backup was created before migration.

Migration was performed through a Compose override:

```yaml
services:
  bazarr:
    image: ghcr.io/lavx/bazarr:latest
```

Override file:

```text
/opt/media-stack/bazarr-plus.override.yml
```

The migration did not intentionally rebuild Bazarr's configuration from scratch.

---

## 6. Bazarr+ Provider Hub

Bazarr+ is now being used specifically because of its Provider Hub ecosystem.

Relevant installed/configured providers include:

```text
Kitsunekko
SubDL
SubtitleCat
TVsubtitles
OpenSubtitles.org
OpenSubtitles.com
```

Important distinction:

- Provider Hub installation does not automatically mean a provider is enabled for searches.
- Providers must be installed and enabled as search providers.
- OpenSubtitles.com is separate from OpenSubtitles.org.

### Current provider considerations

**Kitsunekko**

Useful for anime subtitles and enabled through Provider Hub.

**SubDL**

Useful as an additional subtitle source.

**OpenSubtitles.com**

Remains an important provider, particularly for newer/less widely mirrored anime.

It has previously hit provider-side daily limits and can therefore be temporarily throttled.

**SubtitleCat**

Installed but has previously experienced request timeouts.

**TVsubtitles**

Installed but has previously returned HTTP 404 responses.

**OpenSubtitles.org**

Separate from OpenSubtitles.com. Its scraper/service has previously produced errors and it is not the primary subtitle source.

### Anime subtitle configuration

The active subtitle language is English.

Fansub subtitles are acceptable where they meet the configured score/language requirements.

Automatic subtitle downloading is enabled.

The minimum accepted score was previously reduced from 90% to 80% because useful OpenSubtitles results were often returned in the mid-80% range.

---

## 7. Bazarr+ known non-fatal errors

The following have been observed and should not automatically be interpreted as a Bazarr+ installation failure:

```text
AniDB
  API client unavailable/disabled errors

OpenSubtitles.org
  scraper/service availability errors

OpenSubtitles.com
  provider throttling/rate limits

SubtitleCat
  request timeouts

TVsubtitles
  HTTP 404 responses
```

Bazarr+ itself is healthy and remains integrated with Sonarr and Radarr.

Do not restart/reinstall Bazarr+ merely because one provider is temporarily throttled or unavailable.

---

## 8. Important media-stack architecture

The current intended flow is:

```text
Seerr
  │
  ├── Radarr ──┐
  │            │
  └── Sonarr ──┤
               ▼
            Prowlarr
               │
               ▼
             Indexers
               │
               ▼
           qBittorrent
               │
               │ VPN network namespace
               ▼
            Gluetun
               │
               ▼
        /mnt/downloads
               │
               ▼
       Radarr / Sonarr
               │
               ▼
          /mnt/media
               │
               ▼
           Jellyfin
```

Bazarr+ operates alongside Sonarr/Radarr against:

```text
/mnt/media
```

The canonical media paths remain unchanged.

---

## 9. Documentation changes completed

Added:

```text
docs/16-gluetun-bazarr-plus.md
```

Updated:

```text
README.md
```

The README now lists:

- Gluetun
- Bazarr+
- the new documentation page

The new documentation intentionally excludes credentials, API keys, VPN secrets and other sensitive values.

---

## 10. GitHub workflow

The repository is now accessible through the ChatGPT GitHub integration.

This means future documentation audits can inspect the actual repository instead of relying solely on conversation memory.

The repository should still be treated as documentation/configuration source material rather than as a substitute for checking live service state when making infrastructure changes.

The user's preferred publication workflow remains:

```bash
git add .
git commit -m "Update homelab documentation"
git push origin main
```

---

## 11. Immediate project direction

The current intended order is:

1. Finish auditing/updating existing homelab documentation.
2. Ensure the AI handover/context is current.
3. Integrate all relevant services into Uptime Kuma.
4. Integrate relevant systems/services into Beszel.
5. Deploy/configure Homarr on VM107.
6. Continue remaining hardening and cleanup.
7. Rebuild the architecture diagram only after the infrastructure has remained stable long enough to represent the final topology.

---

## 12. Future handover notes

Future AI sessions should remember:

- CT103 is the media stack.
- qBittorrent traffic is intentionally routed through Gluetun.
- qBittorrent shares Gluetun's network namespace.
- Do not expose qBittorrent independently from Gluetun without an explicit architecture change.
- Bazarr is now Bazarr+, not the old LinuxServer Bazarr image.
- Bazarr+ configuration was preserved during migration.
- Provider Hub providers may fail independently without Bazarr+ itself being broken.
- OpenSubtitles.org and OpenSubtitles.com are separate integrations.
- Kitsunekko is particularly relevant to the user's English anime subtitle use case.
- The user accepts fansubs for anime subtitles.
- Automatic subtitle downloading is enabled.
- Never place VPN credentials, API keys or provider secrets in documentation.
- Prefer complete pasteable scripts when a script is required.
- Avoid asking the user to manually edit existing scripts.
- Use known current context before asking for information already established.
- Avoid unnecessary diagnostic rabbit holes.
- Preserve known-good architecture unless there is evidence it needs to change.

---

## 13. Version history

### 2026-09-21

- Confirmed ChatGPT GitHub repository access for `RobynTW/robyns-homelab`.
- Added `docs/16-gluetun-bazarr-plus.md`.
- Documented the Gluetun/qBittorrent network namespace architecture.
- Documented qBittorrent's Gluetun-provided WebUI exposure on port 8080.
- Migrated Bazarr from `lscr.io/linuxserver/bazarr:latest` to `ghcr.io/lavx/bazarr:latest`.
- Verified Bazarr+ version 2.6.2.
- Preserved the existing Bazarr configuration during migration.
- Added documentation for Bazarr+ Provider Hub.
- Documented Kitsunekko, SubDL, SubtitleCat, TVsubtitles, OpenSubtitles.org and OpenSubtitles.com.
- Documented known provider throttling/timeouts/HTTP errors as provider-specific rather than automatically treating them as Bazarr+ failures.
- Updated README media-stack documentation.
- Established the next project phase as monitoring expansion followed by Homarr.
