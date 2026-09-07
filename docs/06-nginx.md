# Nginx Reverse Proxy & HTTPS

## Overview

Nginx provides the reverse-proxy and HTTPS layer for the homelab.

Nginx runs in its own dedicated Proxmox LXC:

```text
Proxmox pve-1
└── CT 106
    ├── Hostname: nginx
    ├── IP: 192.168.20.94
    ├── Nginx
    └── Certbot
```

Separating Nginx from the Pi-hole container means that DNS, monitoring, and reverse-proxy services are independently managed.

Nginx receives requests for the homelab's HTTPS hostnames and forwards them to the appropriate internal service.

## Network Details

| Component   | Address              |
| ----------- | -------------------- |
| CT106       | `192.168.20.94`      |
| HTTP        | `80/tcp`             |
| HTTPS       | `443/tcp`            |
| Pi-hole     | `192.168.20.99:8080` |
| Jellyfin    | `192.168.20.98:8096` |
| Uptime Kuma | `192.168.20.95:3001` |
| Beszel      | `192.168.20.96:8090` |

## Hostnames

The following services are currently reverse-proxied through Nginx:

| Hostname                     | Backend              |
| ---------------------------- | -------------------- |
| `jellyfin.robynshomelab.dev` | `192.168.20.98:8096` |
| `status.robynshomelab.dev`   | `192.168.20.95:3001` |
| `beszel.robynshomelab.dev`   | `192.168.20.96:8090` |
| `pihole.robynshomelab.dev`   | `192.168.20.99:8080` |

Pi-hole provides the internal DNS records for these hostnames, with all four resolving to `192.168.20.94`.

## Request Flow

For a local client:

```text
Client
  │
  │ DNS query
  ▼
Pi-hole
192.168.20.99
  │
  │ returns 192.168.20.94
  ▼
Nginx
192.168.20.94
  │
  ├── jellyfin.robynshomelab.dev
  │       └── 192.168.20.98:8096
  │
  ├── status.robynshomelab.dev
  │       └── 192.168.20.95:3001
  │
  ├── beszel.robynshomelab.dev
  │       └── 192.168.20.96:8090
  │
  └── pihole.robynshomelab.dev
          └── 192.168.20.99:8080
```

HTTP requests are redirected to HTTPS.

## Nginx Configuration

Nginx site configurations are stored in:

```text
/etc/nginx/sites-available/
```

Enabled configurations are linked into:

```text
/etc/nginx/sites-enabled/
```

Current sites:

```text
/etc/nginx/sites-available/
├── jellyfin
├── status
├── beszel
└── pihole
```

The default Nginx site has been removed.

### Jellyfin

```nginx
server {
    listen 80;
    listen [::]:80;

    server_name jellyfin.robynshomelab.dev;

    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name jellyfin.robynshomelab.dev;

    ssl_certificate /etc/letsencrypt/live/jellyfin.robynshomelab.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jellyfin.robynshomelab.dev/privkey.pem;

    location / {
        proxy_pass http://192.168.20.98:8096;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_buffering off;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

### Uptime Kuma

```nginx
server {
    listen 80;
    listen [::]:80;

    server_name status.robynshomelab.dev;

    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name status.robynshomelab.dev;

    ssl_certificate /etc/letsencrypt/live/status.robynshomelab.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/status.robynshomelab.dev/privkey.pem;

    location / {
        proxy_pass http://192.168.20.95:3001;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_buffering off;
    }
}
```

### Beszel

```nginx
server {
    listen 80;
    listen [::]:80;

    server_name beszel.robynshomelab.dev;

    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name beszel.robynshomelab.dev;

    ssl_certificate /etc/letsencrypt/live/beszel.robynshomelab.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beszel.robynshomelab.dev/privkey.pem;

    location / {
        proxy_pass http://192.168.20.96:8090;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_buffering off;
    }
}
```

### Pi-hole

```nginx
server {
    listen 80;
    listen [::]:80;

    server_name pihole.robynshomelab.dev;

    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name pihole.robynshomelab.dev;

    ssl_certificate /etc/letsencrypt/live/pihole.robynshomelab.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pihole.robynshomelab.dev/privkey.pem;

    location / {
        proxy_pass http://192.168.20.99:8080;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_buffering off;
    }
}
```

## HTTPS Certificates

Certificates are managed by Certbot and stored under:

```text
/etc/letsencrypt/
```

Nginx references the certificates using the `live/` symlinks.

The certificates are issued using Cloudflare DNS-01 validation. Certificate management is documented separately in `07-certbot.md`.

Private keys must never be committed to Git.

## Testing

After changing an Nginx configuration, test the syntax before reloading:

```bash
nginx -t
```

A successful result should contain:

```text
syntax is ok
test is successful
```

Reload Nginx:

```bash
systemctl reload nginx
```

Check that Nginx is running:

```bash
systemctl status nginx
```

Check listening sockets:

```bash
ss -tlnp | grep -E ':80|:443'
```

## Local Hostname Testing

The configured hostname can be tested against the local Nginx listener:

```bash
curl -Ik -H "Host: jellyfin.robynshomelab.dev" https://127.0.0.1
```

Equivalent tests can be performed for the other services:

```bash
curl -Ik -H "Host: status.robynshomelab.dev" https://127.0.0.1
curl -Ik -H "Host: beszel.robynshomelab.dev" https://127.0.0.1
curl -Ik -H "Host: pihole.robynshomelab.dev" https://127.0.0.1
```

Expected responses are service-dependent. For example, Jellyfin and Uptime Kuma normally return redirects, while Beszel may return `200 OK` and Pi-hole may redirect to `/admin/`.

## Client-Side Testing

Confirm internal DNS resolution:

```bash
dig +short jellyfin.robynshomelab.dev
dig +short status.robynshomelab.dev
dig +short beszel.robynshomelab.dev
dig +short pihole.robynshomelab.dev
```

All four should resolve to:

```text
192.168.20.94
```

Test HTTPS from a client:

```bash
curl -I https://jellyfin.robynshomelab.dev
curl -I https://status.robynshomelab.dev
curl -I https://beszel.robynshomelab.dev
curl -I https://pihole.robynshomelab.dev
```

## Troubleshooting

### Nginx configuration fails

Run:

```bash
nginx -t
```

Do not reload Nginx until the configuration test succeeds.

### HTTPS certificate error

Check the certificate:

```bash
openssl x509 \
    -in /etc/letsencrypt/live/jellyfin.robynshomelab.dev/cert.pem \
    -noout -subject -dates
```

Check that the hostname being accessed matches the certificate.

### Backend unavailable

Test the backend directly from CT106:

```bash
curl -I http://192.168.20.98:8096
curl -I http://192.168.20.95:3001
curl -I http://192.168.20.96:8090
curl -I http://192.168.20.99:8080
```

### Check Nginx logs

```bash
journalctl -u nginx --no-pager
```

Access and error logs are also available under:

```text
/var/log/nginx/
```

## Security Notes

Nginx is currently an internal reverse proxy. The homelab does not rely on router port forwarding for these services.

Cloudflare DNS contains only the public DDNS hostname. Internal RFC1918 addresses such as `192.168.20.94` are provided by Pi-hole and are not published publicly.

The Cloudflare API credential used by Certbot is stored separately from the Nginx configuration and is excluded from Git.

## Key Commands

| Command                                          | Purpose                                     |
| ------------------------------------------------ | ------------------------------------------- |
| `nginx -t`                                       | Validate Nginx configuration                |
| `systemctl reload nginx`                         | Reload configuration without stopping Nginx |
| `systemctl restart nginx`                        | Restart Nginx                               |
| `systemctl status nginx`                         | Check Nginx service state                   |
| `ss -tlnp \| grep -E ':80\|:443'`                | Check HTTP/HTTPS listeners                  |
| `curl -I https://hostname`                       | Test HTTPS response                         |
| `curl -Ik -H "Host: hostname" https://127.0.0.1` | Test a specific Nginx virtual host locally  |
| `journalctl -u nginx --no-pager`                 | View Nginx service logs                     |
| `openssl x509 ...`                               | Inspect certificate information             |

## Current State

Nginx migration is complete.

The reverse proxy previously ran inside CT100 alongside Pi-hole. It has been removed from CT100 and now runs exclusively in CT106.

Current architecture:

```text
CT100 pihole
├── Pi-hole
├── Unbound
└── ddclient

CT106 nginx
├── Nginx
└── Certbot
```

All four HTTPS services were tested after the migration and confirmed to be served by CT106.
