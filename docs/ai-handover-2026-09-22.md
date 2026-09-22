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


## Rebuild configuration backup

A rebuild-oriented configuration backup was completed on 2026-09-22 and pushed to the Git repository.

The backup lives under:

`config/`

It is intended as a **rebuild blueprint**, not a complete backup of live application state. It contains the important system/service configuration needed to recreate the current homelab, including Proxmox host/network/storage configuration, LXC/VM configuration, Nginx, Certbot, NetBird systemd configuration, Jellyfin/Beszel/Uptime Kuma services, Media Stack Compose configuration, Homepage configuration/assets, and Pterodactyl/Wings configuration and firewall rules.

Secret-bearing live files were deliberately excluded or sanitized. Examples include Homepage/Media Stack/Pterodactyl `.env` files, raw Pterodactyl Wings `config.yml`, NetBird private/auth state, Cloudflare credentials, ACME private/account keys, SSH private keys, application databases, and other runtime state. Sanitized `.env.example` and Pterodactyl configuration examples are included where useful.

The configuration backup was pushed to `main` in commit:

`cbec7f4`

### How to use the configuration backup for a future rebuild

The `config/` directory should be used as the starting point when rebuilding the homelab after a host failure, OS reinstall, or major rebuild.

Recommended process:

1. Clone the repository onto the replacement/admin machine:

```bash
git clone https://github.com/RobynTW/robyns-homelab.git
cd robyns-homelab
```

2. Read `config/README.md` first. It describes the purpose and limitations of the backup and which secret/runtime files are intentionally absent.

3. Recreate the Proxmox hosts and network/storage foundations from the corresponding files under:
   - `config/pve-1/`
   - `config/pve-2/`
   - `config/pve-1/proxmox/`
   - `config/pve-2/proxmox/`

   Do not blindly copy configuration files over a newly installed system. Use them as the known-good reference, adapting interface names, disks, hostnames, IPs, and package versions if the replacement hardware or OS differs.

4. Recreate each service using its corresponding configuration under `config/`. The directory names are intentionally grouped by service, for example:
   - `config/nginx/`
   - `config/netbird/`
   - `config/beszel/`
   - `config/uptime-kuma/`
   - `config/homepage/`
   - `config/mediastack/`
   - `config/pterodactyl/`
   - `config/jellyfin/`

5. Restore secrets separately. The repository does **not** contain the live credentials required by several services. Re-enter those credentials from the user's secure password/secret storage and recreate required credential files in their documented paths. Never replace sanitized `REDACTED` values by committing real credentials to Git.

6. Restore application data separately. Configuration files do not replace databases, media, Minecraft world data, Docker volumes, or other runtime/application state. Those require independent backups or fresh application setup.

7. Reapply systemd services and drop-ins from the relevant configuration directories, then enable/start the services after verifying their paths and dependencies.

8. Reapply firewall/NAT rules from the Pterodactyl configuration backup only after NetBird, Docker, the Minecraft server, and the relevant interfaces are present. Verify the current network topology before restoring rules.

9. Recreate DNS/reverse-proxy/TLS integration after the underlying services are working. Do not assume WAN IPs, Cloudflare records, certificates, or ACME credentials remain valid after a rebuild.

10. After the rebuild is operational, update the live configuration backup from the rebuilt systems and commit the changes so the repository once again reflects the known-good state.

The key principle is: **Git stores the reproducible configuration blueprint; secure storage and independent backups provide secrets and application data.** A future rebuild should use both rather than treating the Git repository as a full bare-metal backup.
