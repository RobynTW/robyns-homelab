# AI Handover — 2026-09-22

## Checkpoint

The Homepage/dashboard phase is now considered complete enough to move on.

The old plan to deploy Homarr on VMID 107 is obsolete.

**Current state:**

```text
CT107
hostname = homepage
IP = 192.168.20.92
host = pve-1
```

VMID 107 is an LXC, not a VM.

## Homepage

Homepage version: 2.4.0

Directory: `/opt/homepage`

Compose: `/opt/homepage/docker-compose.yml`

Config: `/opt/homepage/config`

Background: `/opt/homepage/images/homepage-background.jpg`

Hostname: `homepage.robynshomelab.dev`

Reverse proxy: CT106 Nginx at `192.168.20.94`.

Local service: `192.168.20.92:3000`.

The Compose file now mounts `/opt/homepage/images:/app/public/images`.

### Homepage visual baseline

`/opt/homepage/config/settings.yaml` uses the local background and `iconStyle: theme`.

`/opt/homepage/config/widgets.yaml` contains System resources, Storage resources, and a GitHub logo widget linking directly to:

`https://github.com/RobynTW/robyns-homelab`

The old Developer/GitHub bookmark was removed.

The GitHub icon is monochrome/theme styled and is pushed to the right side of the top information-widget bar using the actual Homepage DOM.

Service groups:

```text
Infrastructure
Network
Media
Gaming
Monitoring
```

Desktop arrangement:

```text
Infrastructure  | Media | Gaming
Network         |       | Monitoring
```

The cards use a glass-style treatment and the group headings were enlarged.

### Safe custom JavaScript

`/opt/homepage/config/custom.js` is intentionally a single delayed pass with no MutationObserver, recursion, or polling.

A previous broad MutationObserver caused severe browser/PC lag and was removed.

### Custom CSS

`/opt/homepage/config/custom.css` contains the service grid, responsive layout, glass cards, larger headings, Network positioning, GitHub right alignment, and bottom visual cap.

The Network vertical offset is manually tuned and must not be casually overwritten.

The bottom cap is cosmetic and was not worth destabilising the Homepage controls to perfect.

## Proxmox dashboard API

PVE-1 and PVE-2 now use custom API widgets instead of native Glances service widgets.

Endpoints:

`http://192.168.20.100:61209/stats`

`http://192.168.20.101:61209/stats`

Files on each Proxmox host:

`/usr/local/bin/homepage-stats.py`

`/etc/systemd/system/homepage-stats.service`

Metrics include CPU, RAM, swap, temperature, uptime, root filesystem usage, and PVE-2 storage usage.

This implementation is working and should be preserved.

## Monitoring

Beszel CT104 at `192.168.20.96` now represents the major homelab systems:

1. Beszel
2. Jellyfin
3. NetBird
4. NGINX
5. Pi-Hole
6. PVE-1
7. PVE-2
8. Media Stack
9. Pterodactyl
10. Uptime Kuma

PVE-2 monitoring includes `sdb1`.

Uptime Kuma CT105 is at `192.168.20.95:3001`.

Curated status page:

`https://status.robynshomelab.dev/status/homelab`

## Current version record

| Component | Version |
| --- | --- |
| Proxmox VE | 9.2.2 |
| Homepage | 2.4.0 |
| NetBird | 0.78.1 |
| Pterodactyl Wings | 1.13.3 |
| Docker Engine VM108 | 29.8.0 |
| qBittorrent | 5.2.3 |
| Bazarr+ | 2.6.2 |
| Jellyfin | 10.11.11 |

These are point-in-time deployment records, not upstream latest-release claims.

## Broader infrastructure state

- pve-1 = `192.168.20.100`
- pve-2 = `192.168.20.101`
- CT100 Pi-hole = `192.168.20.99`
- CT101 NetBird = `192.168.20.97`
- CT102 Jellyfin = `192.168.20.98`
- CT103 Media Stack = `192.168.20.93`
- CT104 Beszel = `192.168.20.96`
- CT105 Uptime Kuma = `192.168.20.95`
- CT106 Nginx = `192.168.20.94`
- CT107 Homepage = `192.168.20.92`
- VM108 Pterodactyl = `192.168.20.111`

4TB WD Blue `WD40EZRZ` is mounted at `/mnt/homelab-data` on pve-2 and served through NFS.

Pterodactyl/Minecraft remains on VM108 with permanent NetBird Reverse Proxy exposure at `minecraft.robynshomelab.dev:17161`.

No router port forwarding is used.

## Documentation completed on 2026-09-22

- README updated for current topology and Homepage.
- `.ai-homelab-context.md` refreshed with the current state.
- `docs/17-homepage.md` created.
- This dated handover created.
- TODO reordered and Homepage marked complete.
- Current software version record added to the top-level documentation.
- VMID 107 corrected from historical Homarr/VM wording to CT107 Homepage.

## Next project phase

Current intended order:

1. Monitoring expansion as required.
2. VM108 firewall hardening.
3. Remaining service configuration/cleanup.
4. Backup improvements.
5. Extended stability testing.
6. Rebuild the architecture diagram after several months of stability.

Additional Minecraft/game-server work may occur before this sequence.

## User workflow

- Prefer complete fresh pasteable scripts.
- Always state exact file paths and where a change belongs.
- Avoid unnecessary Docker restarts.
- Avoid unnecessary diagnostic rabbit holes.
- Preserve known-good configuration.
- Do not recommend router port forwarding.
- Never store secrets in documentation.
