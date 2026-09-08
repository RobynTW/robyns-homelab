# NetBird

NetBird provides private remote access to the homelab without exposing internal services to the public internet.

## Current deployment

NetBird is deployed on **CT101** on the Dell OptiPlex 3060 Proxmox host.

| Setting | Value |
| --- | --- |
| Container | CT101 |
| Hostname | `netbird` |
| OS | Debian GNU/Linux 12 |
| LAN IP | `192.168.20.97` |
| NetBird IP | `100.113.51.59` |
| NetBird IPv6 | `fda0:124:5d3a:d4ae:ed2e:853c:913a:4d70` |
| NetBird version | `0.78.1` |
| Interface | Kernel / WireGuard |
| Management | `https://api.netbird.io:443` |
| Signal | `https://signal.netbird.io:443` |
| WireGuard port | `51820` |

CT101 acts as the dedicated NetBird routing peer for accessing selected services on the home LAN.

## Purpose

NetBird is used to provide private remote access to services that should not be exposed directly to the internet.

Current remote-access flow:

    iPhone / remote device
            │
            │ NetBird
            ▼
          CT101
        192.168.20.97
            │
            ├──► Pi-hole
            │    192.168.20.99
            │
            └──► Nginx
                 192.168.20.94

No router port forwarding is required for these services.

## Network routes

CT101 currently advertises the following NetBird routes:

| Route | Destination |
| --- | --- |
| `192.168.20.94/32` | Nginx reverse proxy |
| `192.168.20.99/32` | Pi-hole |

Only the required hosts are routed through CT101 rather than exposing the entire `192.168.20.0/24` LAN.

This keeps the remote-access scope intentionally limited.

## DNS

NetBird DNS is configured to use Pi-hole:

    192.168.20.99:53

The global NetBird DNS configuration sends DNS queries through Pi-hole.

This provides the same DNS filtering and local DNS resolution to connected NetBird clients that is available to devices on the home LAN.

Internal hostnames such as:

    pihole.robynshomelab.dev
    jellyfin.robynshomelab.dev
    beszel.robynshomelab.dev
    status.robynshomelab.dev

resolve through the existing Pi-hole local DNS configuration.

## Authentication and persistence

CT101 is registered as a permanent machine peer using a **NetBird setup key** rather than relying on interactive SSO authentication.

This is important because NetBird's periodic user-authentication/session expiration applies to peers registered through interactive user authentication. Setup-key-registered machines are intended for unattended servers and infrastructure.

The setup key used during registration was configured with:

- Reusable: enabled
- Ephemeral peer: disabled
- Key expiration: unlimited
- Usage limit: 1
- Extra DNS labels: disabled

The setup key was revoked after CT101 was successfully registered.

The setup key itself is not stored in this repository.

### Authentication verification

After migrating CT101 from the original SSO registration, the following was tested:

    netbird down
    netbird up

NetBird reconnected successfully without requesting another SSO login.

This confirms that CT101 can reconnect using its persistent machine registration without requiring an interactive user session.

## Service persistence

The NetBird daemon runs as a systemd service:

    systemctl status netbird

The service is enabled and starts automatically with Debian.

Expected state:

    Active: active (running)
    Loaded: ... enabled

This means NetBird should automatically reconnect after a CT101 reboot.

## IP forwarding

CT101 is configured to forward IPv4 traffic:

    net.ipv4.ip_forward = 1

This allows CT101 to act as the NetBird routing peer for the selected LAN destinations.

## Firewall

CT101 currently uses nftables.

The routing container is intentionally permissive because its primary purpose is forwarding NetBird traffic to the explicitly configured LAN routes.

Final restrictive firewall policy can be introduced later if the routing architecture changes.

## Security model

The homelab does not expose the following services directly through router port forwarding:

- Pi-hole
- Nginx management
- Jellyfin
- Beszel
- Uptime Kuma
- other internal services

NetBird provides the private network path instead.

Cloudflare is **not** used as a traffic proxy for NetBird or the internal services. Cloudflare remains the authoritative DNS provider for `robynshomelab.dev`.

## Current connected clients

Known NetBird clients include:

| Client | NetBird IP | Purpose |
| --- | --- | --- |
| `netbird` | `100.113.51.59` | Homelab routing peer |
| `iphone-tliam` | `100.113.124.99` | Remote mobile access |
| `blueline` | `100.113.48.198` | Personal client |

Connection type may be P2P or relayed depending on network conditions.

## Useful commands

Check overall status:

    netbird status

Show detailed peer information:

    netbird status --detail

Disconnect the client:

    netbird down

Reconnect the client:

    netbird up

Check the systemd service:

    systemctl status netbird

Restart the service:

    systemctl restart netbird

## Notes

CT101 is intentionally kept as a dedicated NetBird routing peer.

The Dell OptiPlex 3060 hosts several infrastructure services, but NetBird routing is kept separate from the application workloads.

The planned Pterodactyl VM on the Dell OptiPlex 9020 will use its own NetBird peer rather than routing through CT101.

This keeps the two Proxmox hosts and their workloads independently reachable through NetBird.

---

**Status:** 🟢 Deployed and persistent
