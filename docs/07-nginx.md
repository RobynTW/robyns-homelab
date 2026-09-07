# Nginx

## Overview

Nginx is the web server and reverse proxy used by the homelab.

It runs inside **CT 100** alongside Pi-hole, Unbound and ddclient:

```text
VMID:     100
Hostname: pihole-nginx
IP:       192.168.20.99
```

Nginx provides the HTTPS entry point for internal homelab services.

Its primary responsibilities are:

* HTTP → HTTPS redirection
* TLS termination
* Reverse proxying
* Routing requests based on hostname
* Providing a single HTTPS endpoint for multiple services

The current architecture is:

```text
Client
   │
   │ HTTPS :443
   ▼
Nginx
192.168.20.99
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

---

# Why Nginx Is Used

Without a reverse proxy, each service would need to be accessed using its own IP address and port.

For example:

```text
http://192.168.20.98:8096
http://192.168.20.95:3001
http://192.168.20.96:8090
```

Nginx allows the services to instead be accessed using consistent hostnames:

```text
https://jellyfin.robynshomelab.dev
https://status.robynshomelab.dev
https://beszel.robynshomelab.dev
https://pihole.robynshomelab.dev
```

The client connects to Nginx, and Nginx determines which backend should receive the request.

---

# Port Architecture

Nginx owns the standard web ports:

```text
HTTP   :80
HTTPS  :443
```

Pi-hole's web interface was moved to:

```text
HTTP   :8080
```

This avoids a port conflict between Pi-hole's web server and Nginx.

The resulting arrangement is:

```text
192.168.20.99

Port 53    → Pi-hole DNS
Port 80    → Nginx
Port 443   → Nginx HTTPS
Port 8080  → Pi-hole Web UI
Port 5335  → Unbound
```

This separation allows Nginx to provide HTTPS access to Pi-hole without interfering with Pi-hole's DNS service.

---

# Nginx Configuration Structure

Nginx configuration is stored under:

```text
/etc/nginx/
```

The homelab uses the Debian-style:

```text
/etc/nginx/sites-available/
/etc/nginx/sites-enabled/
```

structure.

Each service has its own configuration file.

Current configurations:

```text
/etc/nginx/sites-available/jellyfin
/etc/nginx/sites-available/status
/etc/nginx/sites-available/beszel
/etc/nginx/sites-available/pihole
```

Enabled configurations are represented by symlinks in:

```text
/etc/nginx/sites-enabled/
```

This makes it possible to enable or disable individual services without modifying the main Nginx configuration.

---

# HTTP to HTTPS Redirect

Each service has an HTTP server block similar to:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name jellyfin.robynshomelab.dev;
    return 301 https://$host$request_uri;
}
```

The purpose is to redirect:

```text
http://...
```

to:

```text
https://...
```

The original hostname and URI are preserved.

For example:

```text
http://jellyfin.robynshomelab.dev/library
```

becomes:

```text
https://jellyfin.robynshomelab.dev/library
```

---

# TLS Certificates

Nginx uses Let's Encrypt certificates issued through Certbot.

Certificates were obtained using Cloudflare DNS-01 validation.

The certificates currently used by Nginx are:

```text
jellyfin.robynshomelab.dev
status.robynshomelab.dev
beszel.robynshomelab.dev
pihole.robynshomelab.dev
```

Certificates are stored under:

```text
/etc/letsencrypt/live/
```

For example:

```text
/etc/letsencrypt/live/jellyfin.robynshomelab.dev/
```

Each certificate provides:

```text
fullchain.pem
privkey.pem
```

Nginx references these files in the HTTPS server block.

Private keys must never be committed to Git.

---

# Jellyfin Reverse Proxy

Jellyfin is located in CT 102:

```text
192.168.20.98:8096
```

The Nginx configuration is:

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

### Jellyfin-specific considerations

The configuration uses HTTP/1.1 and WebSocket-related headers:

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

These are important for applications that use persistent connections.

Buffering is also disabled:

```nginx
proxy_buffering off;
```

and long proxy timeouts are configured:

```nginx
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;
```

This is appropriate for a media application where connections may remain open for extended periods.

---

# Uptime Kuma Reverse Proxy

Uptime Kuma runs in CT 105:

```text
192.168.20.95:3001
```

The Nginx configuration is:

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

Uptime Kuma uses persistent connections for its web interface, so the WebSocket headers are retained.

---

# Beszel Reverse Proxy

Beszel runs in CT 104:

```text
192.168.20.96:8090
```

The Nginx configuration is:

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

---

# Pi-hole Reverse Proxy

Pi-hole is hosted in the same CT as Nginx:

```text
192.168.20.99
```

Its web interface listens on:

```text
192.168.20.99:8080
```

Nginx provides the HTTPS endpoint:

```text
https://pihole.robynshomelab.dev
```

The configuration is:

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

Because the backend is on the same container, this is effectively:

```text
Client
  │
  ▼
Nginx :443
  │
  ▼
Pi-hole :8080
```

---

# Hostname-Based Routing

Nginx determines the backend using the requested hostname.

For example:

```text
jellyfin.robynshomelab.dev
        │
        ▼
Nginx
        │
        └── 192.168.20.98:8096
```

while:

```text
status.robynshomelab.dev
        │
        ▼
Nginx
        │
        └── 192.168.20.95:3001
```

This allows multiple services to share ports 80 and 443 without requiring separate public IP addresses.

---

# Local DNS Integration

The service hostnames are resolved by Pi-hole.

Current records include:

```text
jellyfin.robynshomelab.dev → 192.168.20.99
status.robynshomelab.dev   → 192.168.20.99
beszel.robynshomelab.dev   → 192.168.20.99
pihole.robynshomelab.dev   → 192.168.20.99
```

Therefore, an internal client follows this path:

```text
Client
  │
  │ DNS
  ▼
Pi-hole
  │
  └── service hostname → 192.168.20.99
                         │
                         ▼
                       Nginx
                         │
                         ▼
                     Backend LXC
```

This is an example of split-horizon-style DNS behaviour: the internal DNS server provides private service addresses while the public Cloudflare zone does not publish the internal IP addresses.

---

# NetBird Integration

NetBird private remote access allows remote clients to reach the internal Nginx endpoints without exposing them publicly.

The architecture is:

```text
Remote device
      │
      │ NetBird
      ▼
CT 101 NetBird
      │
      ▼
192.168.20.99
      │
      ▼
Nginx :443
      │
      ▼
Internal service
```

This means a remote device can access the normal HTTPS service hostname while remaining within the private homelab access architecture.

Nginx itself does not need to know whether the client is local or arriving through NetBird.

---

# Configuration Validation

Nginx configuration should always be tested before restarting the service.

Use:

```bash
nginx -t
```

A successful result should indicate that the syntax is valid and the configuration test succeeded.

Only after a successful test should Nginx be reloaded or restarted.

---

# Reloading Nginx

After changing an Nginx configuration:

```bash
systemctl reload nginx
```

A reload is generally preferable to a full restart because it allows existing connections to continue while the new configuration is loaded.

For larger changes or when troubleshooting startup problems:

```bash
systemctl restart nginx
```

Check the resulting service state with:

```bash
systemctl status nginx
```

---

# Testing HTTPS

The service can be tested from a client using:

```bash
curl -I https://jellyfin.robynshomelab.dev
```

The same approach can be used for:

```bash
curl -I https://status.robynshomelab.dev
curl -I https://beszel.robynshomelab.dev
curl -I https://pihole.robynshomelab.dev
```

This verifies that the HTTPS endpoint is reachable.

---

# Testing the Backend Directly

When troubleshooting a reverse proxy, it is useful to bypass Nginx and test the backend directly.

For example, Jellyfin:

```bash
curl -I http://192.168.20.98:8096
```

Uptime Kuma:

```bash
curl -I http://192.168.20.95:3001
```

Beszel:

```bash
curl -I http://192.168.20.96:8090
```

Pi-hole:

```bash
curl -I http://192.168.20.99:8080
```

This helps identify whether a problem exists with:

1. The backend application
2. Network connectivity
3. Nginx
4. TLS
5. DNS

---

# Troubleshooting Method

When an HTTPS service stops working, troubleshoot from the inside out.

### 1. Check the backend

```bash
curl -I http://BACKEND_IP:PORT
```

If the backend does not respond, Nginx is not the immediate problem.

### 2. Check Nginx configuration

```bash
nginx -t
```

### 3. Check Nginx service

```bash
systemctl status nginx
```

### 4. Check listening ports

```bash
ss -tulpn | grep -E ':80|:443'
```

### 5. Check DNS

```bash
dig jellyfin.robynshomelab.dev
```

### 6. Test HTTPS

```bash
curl -I https://jellyfin.robynshomelab.dev
```

This layered approach prevents changing multiple components at once and makes troubleshooting much easier.

---

# Logs

Nginx logs are stored under:

```text
/var/log/nginx/
```

The main files are:

```text
/var/log/nginx/access.log
/var/log/nginx/error.log
```

The access log shows requests received by Nginx.

The error log is particularly useful when troubleshooting:

* Failed upstream connections
* TLS problems
* Configuration issues
* Permission problems
* Proxy failures

Logs can be monitored with:

```bash
tail -f /var/log/nginx/error.log
```

and:

```bash
tail -f /var/log/nginx/access.log
```

---

# Security Considerations

Nginx is currently an **internal reverse proxy**.

The service hostnames resolve internally through Pi-hole and are not published with private IP addresses through Cloudflare.

Nginx therefore provides HTTPS and hostname-based routing without requiring the services themselves to be publicly exposed.

TLS private keys are stored under:

```text
/etc/letsencrypt/
```

and must never be committed to Git.

The Nginx configuration can safely be versioned because it contains no private key material or API credentials.

---

# Current Nginx Architecture

The complete current arrangement is:

```text
                         Internal client
                               │
                               │ DNS
                               ▼
                         Pi-hole :53
                               │
                               │
                    service → 192.168.20.99
                               │
                               ▼
                         Nginx :443
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
          Jellyfin          Kuma             Beszel
        192.168.20.98    192.168.20.95     192.168.20.96
           :8096            :3001             :8090
                              
                         ┌─────────────┐
                         │   Pi-hole   │
                         │ 192.168.20.99
                         │    :8080    │
                         └─────────────┘
```

The important separation is:

```text
Pi-hole :53
    ↓
DNS

Nginx :80/:443
    ↓
HTTPS / Reverse Proxy

Pi-hole :8080
    ↓
Web interface

Unbound :5335
    ↓
Recursive DNS
```

---

# Future Updates

This document should be updated when:

* A new reverse-proxied service is added
* An existing backend address or port changes
* TLS configuration changes
* Additional security headers are introduced
* Nginx is moved to another container
* Public service exposure is introduced
* Nginx is replaced with another reverse proxy
* Authentication is added in front of services
* Additional monitoring is added

