# Uptime Kuma Monitoring

## Overview

Uptime Kuma provides service-availability monitoring for the homelab.

It runs in a dedicated Proxmox LXC:

```text
Proxmox pve-1
└── CT105
    ├── Hostname: uptime-kuma
    ├── IP: 192.168.20.95
    ├── 1 vCPU
    ├── 512 MB RAM
    ├── 256 MB swap
    └── 8 GB disk
```

Uptime Kuma is primarily concerned with whether services are reachable and responding.

It complements Beszel, which focuses on system and resource monitoring.

## Network Details

| Component       | Address              |
| --------------- | -------------------- |
| Uptime Kuma LXC | `192.168.20.95`      |
| Uptime Kuma     | `192.168.20.95:3001` |
| Nginx           | `192.168.20.94`      |
| Proxmox         | `192.168.20.100`     |
| Pi-hole         | `192.168.20.99`      |
| NetBird         | `192.168.20.97`      |
| Jellyfin        | `192.168.20.98`      |
| Beszel          | `192.168.20.96`      |

The web interface is accessed through Nginx:

```text
https://status.robynshomelab.dev
```

## Operating System

CT105 runs:

```text
Debian 12 Bookworm
```

Current allocation:

```text
1 vCPU
512 MB RAM
256 MB swap
8 GB disk
```

## Uptime Kuma Installation

Uptime Kuma is installed under:

```text
/opt/uptime-kuma
```

The installation uses:

```text
Node.js 22.23.2
npm 10.9.8
Uptime Kuma 2.5.3
```

Check the Node.js version:

```bash
node --version
```

Check npm:

```bash
npm --version
```

Check the installed Uptime Kuma package:

```bash
cd /opt/uptime-kuma
npm list --depth=0
```

## Process Management

Uptime Kuma is managed by PM2.

PM2 keeps the application running and provides process persistence across reboots.

Check PM2:

```bash
pm2 status
```

The Uptime Kuma process should appear in the process list.

View the process logs:

```bash
pm2 logs
```

## Boot Persistence

PM2 has been configured to start automatically when the container boots.

The PM2 startup configuration was created with:

```bash
pm2 startup
```

The current PM2 process list has also been saved:

```bash
pm2 save
```

The generated systemd service is enabled.

Check it with:

```bash
systemctl is-enabled pm2-root
```

Expected result:

```text
enabled
```

This means Uptime Kuma should automatically return after a CT105 reboot.

## Starting and Stopping Uptime Kuma

Check the PM2 process:

```bash
pm2 status
```

Restart the application:

```bash
pm2 restart all
```

Stop the application:

```bash
pm2 stop all
```

Start the saved PM2 processes:

```bash
pm2 resurrect
```

The exact PM2 process name can be used instead of `all` when preferred.

## Local Web Interface

Uptime Kuma listens on:

```text
192.168.20.95:3001
```

Test it locally:

```bash
curl -I http://127.0.0.1:3001
```

Test using the container's LAN address:

```bash
curl -I http://192.168.20.95:3001
```

A successful HTTP response confirms that the application is responding.

## Reverse Proxy

Nginx runs separately on CT106:

```text
192.168.20.94
```

The public/internal service hostname is:

```text
status.robynshomelab.dev
```

The request path is:

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
Uptime Kuma
192.168.20.95:3001
```

Pi-hole provides the internal DNS record:

```text
status.robynshomelab.dev → 192.168.20.94
```

The TLS certificate is managed by Certbot.

See:

```text
06-nginx.md
07-certbot.md
```

for the reverse-proxy and certificate configuration.

## HTTPS Testing

Test the service through Nginx:

```bash
curl -I https://status.robynshomelab.dev
```

A redirect to the Uptime Kuma dashboard is expected.

The Nginx virtual host can also be tested directly from CT106:

```bash
curl -Ik \
    -H "Host: status.robynshomelab.dev" \
    https://127.0.0.1
```

The current configuration successfully returns a Uptime Kuma response.

## Internal DNS

Pi-hole resolves:

```text
status.robynshomelab.dev
```

to:

```text
192.168.20.94
```

Verify:

```bash
dig +short status.robynshomelab.dev
```

Expected:

```text
192.168.20.94
```

The hostname therefore points to Nginx rather than directly to CT105.

## Current Monitors

Uptime Kuma currently monitors eight services and infrastructure components.

### 1. Proxmox

Type:

```text
Ping
```

Target:

```text
192.168.20.100
```

This monitors the availability of the Proxmox 3060 host.

A failure indicates that the Proxmox host itself may be unreachable.

Because the majority of the current homelab services run on this host, this is an important high-level availability check.

### 2. Pi-hole DNS

Type:

```text
DNS
```

Target:

```text
192.168.20.99
```

Port:

```text
53
```

The monitor performs a DNS query against Pi-hole.

This tests the actual DNS service rather than merely checking whether the Pi-hole host responds to ping.

### 3. Pi-hole Web Interface

Type:

```text
HTTP
```

Target:

```text
http://192.168.20.99:8080/admin
```

This checks that the Pi-hole web interface is responding.

Pi-hole's web interface was moved from the standard HTTP/HTTPS ports because Nginx now owns ports 80 and 443 on CT106.

### 4. Nginx / HTTPS

The current Nginx availability monitor uses:

```text
https://pihole.robynshomelab.dev
```

This verifies that the HTTPS reverse-proxy path is functioning.

This monitor effectively tests:

```text
DNS
  │
  ▼
Nginx
  │
  ▼
Pi-hole web interface
```

It is therefore a combined Nginx + Pi-hole HTTPS-path check rather than a pure Nginx process check.

### 5. NetBird

Type:

```text
Ping
```

Target:

```text
192.168.20.97
```

This monitors the NetBird LXC.

NetBird is important because it provides private remote access to the homelab.

### 6. Jellyfin

Type:

```text
HTTP
```

Target:

```text
http://192.168.20.98:8096
```

This checks that Jellyfin is reachable and responding on its native HTTP port.

The monitor does not depend on Nginx or external DNS, which makes it useful for distinguishing a Jellyfin failure from an Nginx failure.

### 7. Beszel

Type:

```text
HTTP
```

Target:

```text
http://192.168.20.96:8090
```

This checks that the Beszel Hub is responding.

### 8. Uptime Kuma

Type:

```text
HTTP
```

Target:

```text
http://192.168.20.95:3001
```

Uptime Kuma monitors its own HTTP service.

Self-monitoring can help identify problems with the application even when the container itself remains reachable.

## Monitoring Architecture

The current monitoring arrangement is:

```text
                    Uptime Kuma
                 192.168.20.95
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
   Proxmox            Pi-hole           NetBird
   192.168.20.100     192.168.20.99     192.168.20.97
       │
       ├── Jellyfin
       │   192.168.20.98
       │
       └── other services

                    ┌──────────┐
                    │ Beszel  │
                    │  .96    │
                    └──────────┘
```

The monitored endpoints are intentionally distributed across the infrastructure.

## Uptime Kuma vs Beszel

Uptime Kuma and Beszel perform different monitoring roles.

### Uptime Kuma

Primarily monitors:

```text
Service availability
HTTP
TCP
DNS
Ping
Endpoint response
```

### Beszel

Primarily monitors:

```text
CPU
Memory
Temperature
System health
Resource utilisation
Host/agent health
```

Together:

```text
                    Monitoring
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
        Uptime Kuma              Beszel
             │                     │
       "Is it working?"      "How healthy is it?"
```

This distinction makes troubleshooting easier.

For example, if Jellyfin is down:

* Uptime Kuma should detect that the service is unavailable.
* Beszel may still show the container as healthy.
* This suggests a service-level failure rather than a host failure.

Conversely, high CPU or memory usage may appear in Beszel while Uptime Kuma remains completely green.

## Troubleshooting

### Uptime Kuma is unavailable

Check PM2:

```bash
pm2 status
```

Check the application logs:

```bash
pm2 logs
```

Check the listening port:

```bash
ss -tlnp | grep 3001
```

Test locally:

```bash
curl -I http://127.0.0.1:3001
```

### Uptime Kuma does not start after reboot

Check PM2 persistence:

```bash
pm2 status
```

Check the systemd startup service:

```bash
systemctl status pm2-root
```

Check whether it is enabled:

```bash
systemctl is-enabled pm2-root
```

If the process list has changed, save it again:

```bash
pm2 save
```

### HTTPS access fails

Check DNS:

```bash
dig +short status.robynshomelab.dev
```

Expected:

```text
192.168.20.94
```

Test the backend directly:

```bash
curl -I http://192.168.20.95:3001
```

If the backend works, investigate Nginx:

```bash
nginx -t
systemctl status nginx
```

### A monitor is red but the host is reachable

Determine whether the failure is at the host or service level.

For example, Jellyfin:

```bash
ping 192.168.20.98
curl -I http://192.168.20.98:8096
```

If ping succeeds but HTTP fails, the host may be running while Jellyfin is not responding.

Check Jellyfin:

```bash
systemctl status jellyfin
```

### Pi-hole DNS monitor fails

Test directly:

```bash
dig google.com @192.168.20.99
```

Check Pi-hole:

```bash
systemctl status pihole-FTL
```

Check whether port 53 is listening:

```bash
ss -ulnp | grep ':53'
```

### Pi-hole Web monitor fails

Pi-hole's web service currently listens on port 8080.

Test:

```bash
curl -I http://192.168.20.99:8080/admin
```

If the direct check works but the HTTPS monitor fails, investigate Nginx or DNS.

## Adding Future Monitors

When new infrastructure is deployed, monitors should be added for meaningful services rather than every individual process.

Potential future monitoring targets include:

```text
Dell OptiPlex 9020
NAS
Pterodactyl VM
Pterodactyl Panel
Game services
Media stack
Jellyseerr
Sonarr
Radarr
Prowlarr
Bazarr
qBittorrent
```

These should be added as the services are actually deployed.

Placeholder monitors should not be created for infrastructure that does not yet exist.

## Future NAS Monitoring

When the Dell OptiPlex 9020 is deployed as the NAS, it should be monitored for both availability and system health.

The preferred arrangement is:

```text
9020
 │
 ├── Uptime Kuma
 │     └── availability
 │
 └── Beszel
       └── resource/system health
```

This provides the same two-layer monitoring approach used by the current 3060 infrastructure.

## Future Pterodactyl Monitoring

The future Pterodactyl VM should similarly be monitored independently of the 3060.

Potential checks include:

```text
VM availability
Pterodactyl Panel HTTP
Wings availability
Game-server endpoints
```

The exact monitors should be added after the VM and game-server architecture are implemented.

## Security

Uptime Kuma is not directly exposed through the ISP router.

Access is provided through the internal Nginx reverse proxy and, where required, through NetBird private access.

The public-facing DNS zone does not contain the internal address:

```text
192.168.20.95
```

Instead, Pi-hole provides the internal DNS mapping:

```text
status.robynshomelab.dev → 192.168.20.94
```

Nginx then proxies the request to:

```text
192.168.20.95:3001
```

## Key Commands

| Command                                    | Purpose                           |
| ------------------------------------------ | --------------------------------- |
| `pm2 status`                               | Show Uptime Kuma process state    |
| `pm2 logs`                                 | View application logs             |
| `pm2 restart all`                          | Restart PM2-managed applications  |
| `pm2 save`                                 | Save the current PM2 process list |
| `pm2 resurrect`                            | Restore saved PM2 processes       |
| `systemctl status pm2-root`                | Check PM2 systemd integration     |
| `systemctl is-enabled pm2-root`            | Check boot persistence            |
| `ss -tlnp \| grep 3001`                    | Check Uptime Kuma listener        |
| `curl -I http://127.0.0.1:3001`            | Test Uptime Kuma locally          |
| `curl -I http://192.168.20.95:3001`        | Test Uptime Kuma over LAN         |
| `curl -I https://status.robynshomelab.dev` | Test HTTPS through Nginx          |
| `dig +short status.robynshomelab.dev`      | Verify internal DNS               |
| `nginx -t`                                 | Validate Nginx configuration      |

## Current State

Uptime Kuma is operational on CT105:

```text
CT105 uptime-kuma
├── Debian 12
├── 192.168.20.95
├── 1 vCPU
├── 512 MB RAM
├── 256 MB swap
└── 8 GB disk
```

Current software:

```text
Node.js 22.23.2
npm 10.9.8
Uptime Kuma 2.5.3
```

Uptime Kuma is installed at:

```text
/opt/uptime-kuma
```

PM2 manages the application and is configured to persist across reboots.

HTTPS access is provided through:

```text
https://status.robynshomelab.dev
```

Eight monitors are currently configured:

```text
1. Proxmox
2. Pi-hole DNS
3. Pi-hole Web
4. Nginx / HTTPS
5. NetBird
6. Jellyfin
7. Beszel
8. Uptime Kuma
```

Uptime Kuma is the homelab's service-availability monitoring layer, while Beszel provides system/resource monitoring.
