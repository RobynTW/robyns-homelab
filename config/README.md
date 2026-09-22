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
