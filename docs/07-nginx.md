# Nginx

Nginx is the homelab's internal reverse proxy and TLS termination point.

It runs on CT106 and provides HTTPS access to selected internal services through the `robynshomelab.dev` domain.

---

# Container

```text
VMID:     106
Hostname: nginx
IP:       192.168.20.94
Host:     pve-1
```

CT106 runs:

* Nginx
* Certbot

---

# Role

Nginx provides:

* Reverse proxying
* HTTPS termination
* Hostname-based routing
* Access to internal services using consistent public-style hostnames

The general architecture is:

```text
Client
  │
  │ HTTPS :443
  ▼
Nginx
192.168.20.94
  │
  ├── Jellyfin
  ├── Uptime Kuma
  ├── Beszel
  ├── Pi-hole
  └── Pterodactyl Panel
```

---

# DNS Integration

Internal DNS is provided by Pi-hole.

The following hostnames resolve internally to Nginx:

| Hostname                     | Internal address |
| ---------------------------- | ---------------- |
| `panel.robynshomelab.dev`    | `192.168.20.94`  |
| `jellyfin.robynshomelab.dev` | `192.168.20.94`  |
| `status.robynshomelab.dev`   | `192.168.20.94`  |
| `beszel.robynshomelab.dev`   | `192.168.20.94`  |
| `pihole.robynshomelab.dev`   | `192.168.20.94`  |

The Wings hostname is different:

```text
wings.robynshomelab.dev
```

It resolves internally to:

```text
192.168.20.111
```

because Wings runs directly on VM108 rather than behind Nginx.

---

# Reverse Proxy Routing

Nginx routes requests based on the requested hostname.

```text
panel.robynshomelab.dev
        │
        ▼
192.168.20.94
        │
        ▼
Nginx
        │
        ▼
192.168.20.111:80
```

```text
jellyfin.robynshomelab.dev
        │
        ▼
192.168.20.94
        │
        ▼
Nginx
        │
        ▼
192.168.20.98:8096
```

```text
status.robynshomelab.dev
        │
        ▼
192.168.20.94
        │
        ▼
Nginx
        │
        ▼
192.168.20.95:3001
```

```text
beszel.robynshomelab.dev
        │
        ▼
192.168.20.94
        │
        ▼
Nginx
        │
        ▼
192.168.20.96:8090
```

```text
pihole.robynshomelab.dev
        │
        ▼
192.168.20.94
        │
        ▼
Nginx
        │
        ▼
192.168.20.99:8080
```

---

# Current Backends

| Hostname                     | Backend              | Purpose               |
| ---------------------------- | -------------------- | --------------------- |
| `panel.robynshomelab.dev`    | `192.168.20.111:80`  | Pterodactyl Panel     |
| `jellyfin.robynshomelab.dev` | `192.168.20.98:8096` | Jellyfin              |
| `status.robynshomelab.dev`   | `192.168.20.95:3001` | Uptime Kuma           |
| `beszel.robynshomelab.dev`   | `192.168.20.96:8090` | Beszel                |
| `pihole.robynshomelab.dev`   | `192.168.20.99:8080` | Pi-hole web interface |

---

# TLS

Nginx terminates HTTPS connections.

Certificates are issued by Let's Encrypt using Certbot and Cloudflare DNS-01 validation.

The architecture is:

```text
Client
  │
  │ HTTPS
  ▼
Nginx :443
  │
  │ TLS termination
  ▼
HTTP
  │
  ▼
Internal service
```

Cloudflare is only used for DNS and ACME DNS-01 validation.

Cloudflare does **not** proxy the HTTP/HTTPS traffic.

---

# HTTP Redirect

HTTP requests are redirected to HTTPS where configured.

The intended user-facing access method is:

```text
https://service.robynshomelab.dev
```

rather than plain HTTP.

Backend services may continue to communicate with Nginx over HTTP where TLS is not required internally.

---

# Pterodactyl Panel

The Panel is hosted on VM108:

```text
192.168.20.111
```

Nginx proxies:

```text
https://panel.robynshomelab.dev
        │
        ▼
192.168.20.94:443
        │
        ▼
192.168.20.111:80
```

The Panel itself is configured with:

```text
APP_URL=https://panel.robynshomelab.dev
```

The Panel is accessible internally through LAN DNS and remotely through NetBird.

---

# Jellyfin

Jellyfin runs on CT102:

```text
192.168.20.98:8096
```

Nginx provides:

```text
https://jellyfin.robynshomelab.dev
```

The backend connection is:

```text
Nginx
  │
  ▼
192.168.20.98:8096
```

---

# Uptime Kuma

Uptime Kuma runs on CT105:

```text
192.168.20.95:3001
```

Nginx provides:

```text
https://status.robynshomelab.dev
```

---

# Beszel

Beszel runs on CT104:

```text
192.168.20.96:8090
```

Nginx provides:

```text
https://beszel.robynshomelab.dev
```

---

# Pi-hole

Pi-hole runs on CT100:

```text
192.168.20.99
```

DNS remains on:

```text
192.168.20.99:53
```

The Pi-hole web interface is separately available through:

```text
https://pihole.robynshomelab.dev
```

Nginx proxies the web interface to:

```text
192.168.20.99:8080
```

DNS traffic does **not** pass through Nginx.

```text
DNS:
Client → Pi-hole :53

Web:
Client → Nginx :443 → Pi-hole :8080
```

---

# Network Exposure

There is currently no router port forwarding for Nginx.

This is an important part of the current architecture.

```text
Internet
   │
   ▼
Cloudflare DNS
   │
   ▼
WAN IP
   │
   X
No router port forwarding
```

Therefore, creating a public Cloudflare DNS record does not by itself make the Nginx services Internet-accessible.

Internal users reach Nginx through Pi-hole split DNS.

Remote private access is provided through NetBird.

---

# NetBird Access

The primary remote-access path is:

```text
Remote NetBird client
        │
        ▼
NetBird routing peer
CT101
192.168.20.97
        │
        ▼
192.168.20.94
        │
        ▼
Nginx
        │
        ▼
Internal service
```

CT101 routes the Nginx address:

```text
192.168.20.94/32
```

This allows remote NetBird clients to use the same internal service hostnames and HTTPS endpoints as LAN clients.

---

# Configuration Location

Nginx configuration is normally located under:

```text
/etc/nginx/
```

Important locations include:

```text
/etc/nginx/nginx.conf
/etc/nginx/sites-available/
/etc/nginx/sites-enabled/
```

Certificate files managed by Certbot are stored under:

```text
/etc/letsencrypt/
```

The exact active configuration should always be verified on CT106 rather than relying solely on this document.

---

# Configuration Testing

Before reloading Nginx after configuration changes:

```bash
nginx -t
```

A successful test should report that the configuration syntax is valid.

After a successful test:

```bash
systemctl reload nginx
```

Check the service with:

```bash
systemctl status nginx
```

---

# Useful Commands

## Check Nginx Status

```bash
systemctl status nginx
```

## Test Configuration

```bash
nginx -t
```

## Reload Configuration

```bash
systemctl reload nginx
```

## Restart Nginx

```bash
systemctl restart nginx
```

## View Recent Logs

```bash
journalctl -u nginx
```

Depending on the active configuration, additional logs may be available under:

```text
/var/log/nginx/
```

---

# Troubleshooting

## Hostname Does Not Resolve

First check Pi-hole:

```bash
dig @192.168.20.99 panel.robynshomelab.dev
```

The expected internal result is:

```text
192.168.20.94
```

If the hostname resolves incorrectly, troubleshoot Pi-hole before Nginx.

---

## Nginx Does Not Respond

Check:

```bash
systemctl status nginx
```

Then:

```bash
ss -lntp | grep -E ':80|:443'
```

---

## Backend Unavailable

Test the backend directly from CT106.

For example, Jellyfin:

```bash
curl -I http://192.168.20.98:8096
```

Pi-hole:

```bash
curl -I http://192.168.20.99:8080
```

Uptime Kuma:

```bash
curl -I http://192.168.20.95:3001
```

Beszel:

```bash
curl -I http://192.168.20.96:8090
```

Pterodactyl:

```bash
curl -I http://192.168.20.111:80
```

If the backend cannot be reached directly from CT106, the problem is between Nginx and the backend rather than the reverse-proxy configuration itself.

---

# TLS Troubleshooting

If HTTPS fails:

1. Check Nginx configuration:

   ```bash
   nginx -t
   ```

2. Check certificates:

   ```bash
   certbot certificates
   ```

3. Check certificate expiry.

4. Check Nginx logs.

5. Confirm the hostname resolves to `192.168.20.94` internally.

6. Confirm the corresponding certificate exists under `/etc/letsencrypt/`.

---

# Relationship With Cloudflare

Cloudflare and Nginx have separate responsibilities.

```text
Cloudflare
├── Authoritative DNS
├── DDNS
└── ACME DNS-01

Nginx
├── HTTPS termination
├── Reverse proxy
└── Internal service routing
```

Cloudflare does not proxy the actual application traffic.

---

# Security Model

Nginx is treated as an internal infrastructure service.

The current security model relies on:

* No router port forwarding
* Pi-hole split DNS
* NetBird for remote private access
* TLS for service access
* Internal-only backend services
* Cloudflare DNS-only records
* Restricted access to the homelab LAN

Backend services should not be independently exposed to the WAN.

---

# Future Improvements

Potential future improvements include:

* Additional service reverse proxies
* More granular access controls
* Security headers
* Rate limiting where appropriate
* Centralised Nginx logging
* Monitoring of certificate validity
* Automated configuration backups
* Additional network segmentation

Any new reverse-proxied service should be documented here after deployment and verification.
