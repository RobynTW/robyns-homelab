# Homelab configuration backup

This directory is a rebuild-oriented configuration snapshot collected from
the live homelab.

It intentionally excludes live credentials and private state.

## Included

- Proxmox host networking and storage configuration
- Proxmox LXC/VM configuration
- NFS configuration
- Homepage configuration and assets
- Nginx configuration
- Certbot renewal configuration
- NetBird systemd configuration
- Jellyfin systemd configuration
- Media Stack compose configuration
- Beszel systemd configuration
- Uptime Kuma systemd configuration
- Pterodactyl/Wings configuration templates
- Firewall configuration
- Homepage custom CSS/JS and assets

## Excluded

- Passwords
- API keys
- Access tokens
- Setup keys
- Private keys
- Cloudflare credentials
- ACME private account state
- Homepage `.env`
- Homepage live `services.yaml`
- Pterodactyl Panel `.env`
- Live Wings credentials
- NetBird private/authentication state
- Application databases
- Runtime state

Files ending in `.example` are sanitized templates intended for rebuilds.

## Disaster recovery use

If the homelab suffers a catastrophic failure, clone the repository and use this directory as the known-good configuration reference while rebuilding the infrastructure. Start with the Proxmox host configuration, networking, storage, and guest definitions, then recreate services using their corresponding configuration directories.

Do not blindly copy files onto replacement systems. Verify hardware, disk names, network interfaces, OS/package versions, IP addressing, and dependencies first. Restore secrets separately from secure storage and restore application/runtime data from independent backups.

For the full recovery sequence and current homelab context, see [`docs/ai-handover-2026-09-22.md`](../docs/ai-handover-2026-09-22.md).
