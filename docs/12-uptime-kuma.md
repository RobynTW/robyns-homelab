# Uptime Kuma

Uptime Kuma provides service availability and uptime monitoring for the homelab.

It runs on CT105 and is used alongside Beszel.

---

# Container

```text
VMID:     105
Hostname: uptime-kuma
IP:       192.168.20.95
Host:     pve-1
```

The web interface is available through Nginx at:

```text
https://status.robynshomelab.dev
```

---

# Role

Uptime Kuma is responsible for monitoring whether services and endpoints are reachable.

It complements Beszel:

```text
Beszel
└── System/resource monitoring

Uptime Kuma
└── Service availability monitoring
```

Beszel answers:

> Is the infrastructure healthy?

Uptime Kuma answers:

> Is the service reachable?

---

# Architecture

```text
                         Uptime Kuma
                      192.168.20.95:3001
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
          HTTP/HTTPS         TCP            Other
          monitors          monitors       endpoints
             │                │                │
             └────────────────┴────────────────┘
                              │
                         Homelab services
```

Uptime Kuma can monitor services independently of the host on which it is running.

---

# Reverse Proxy

Nginx provides the HTTPS endpoint:

```text
https://status.robynshomelab.dev
```

The internal DNS record points the hostname to:

```text
192.168.20.94
```

Nginx then proxies the request to:

```text
192.168.20.95:3001
```

The access path is:

```text
Client
  │
  ▼
Pi-hole
  │
  ▼
192.168.20.94
  │
  ▼
Nginx
  │
  ▼
192.168.20.95:3001
  │
  ▼
Uptime Kuma
```

---

# HTTPS

TLS is terminated by Nginx.

The certificate for:

```text
status.robynshomelab.dev
```

is managed by Certbot on CT106.

The certificate currently expires:

```text
2026-12-04
```

Cloudflare is used for DNS-01 certificate validation but does not proxy the application traffic.

---

# DNS

Pi-hole provides the internal DNS record:

```text
status.robynshomelab.dev
```

which resolves to:

```text
192.168.20.94
```

This allows the same hostname to be used by LAN and NetBird clients.

---

# NetBird Access

CT101 advertises the Nginx address:

```text
192.168.20.94/32
```

to NetBird clients.

The remote access path is:

```text
Remote NetBird client
        │
        ▼
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
192.168.20.95:3001
        │
        ▼
Uptime Kuma
```

Pi-hole provides DNS to the NetBird client, so the normal hostname can be used.

---

# Monitoring Targets

Uptime Kuma should be used for availability checks of important homelab services.

Potential targets include:

| Service              | Address               |
| -------------------- | --------------------- |
| Nginx                | `192.168.20.94`       |
| Pi-hole              | `192.168.20.99`       |
| NetBird routing peer | `192.168.20.97`       |
| Jellyfin             | `192.168.20.98:8096`  |
| Media Stack          | `192.168.20.93`       |
| Beszel               | `192.168.20.96:8090`  |
| Pterodactyl Panel    | `192.168.20.111:80`   |
| Wings                | `192.168.20.111:8080` |

The exact monitor list should be treated as the deployed configuration rather than assuming every endpoint above is currently configured.

---

# Recommended Monitor Types

## HTTP/HTTPS

Use HTTP(S) monitoring for web applications.

Examples:

```text
https://panel.robynshomelab.dev
https://jellyfin.robynshomelab.dev
https://beszel.robynshomelab.dev
https://status.robynshomelab.dev
```

This tests more than basic network connectivity because the HTTP service itself must respond.

---

## TCP

TCP monitoring is useful for services that do not expose an appropriate HTTP endpoint.

Examples include:

```text
192.168.20.111:8080
192.168.20.111:2022
```

depending on the desired monitoring scope.

---

# Monitoring Pterodactyl

Pterodactyl is an important future monitoring target.

The architecture is:

```text
Uptime Kuma
     │
     ├── Panel availability
     │
     └── Wings availability
             │
             ▼
        VM108 .111
```

Panel:

```text
https://panel.robynshomelab.dev
```

Wings:

```text
192.168.20.111:8080
```

The Panel and Wings should be monitored separately because the Panel can remain available while Wings is unavailable, and vice versa.

---

# Monitoring Jellyfin

Jellyfin is monitored separately from the Jellyfin host.

The preferred endpoint is:

```text
https://jellyfin.robynshomelab.dev
```

This verifies:

```text
DNS
  ↓
Nginx
  ↓
TLS
  ↓
Jellyfin
```

rather than merely checking whether CT102 responds to ping.

---

# Monitoring Pi-hole

Pi-hole provides the homelab DNS service.

The web interface is available through:

```text
https://pihole.robynshomelab.dev
```

DNS itself is provided directly by:

```text
192.168.20.99:53
```

HTTP monitoring and DNS/service monitoring serve different purposes.

A web monitor can verify the Pi-hole interface, while a DNS check can verify the actual DNS service.

---

# Monitoring Nginx

Nginx is a central dependency because several services use it.

If Nginx fails:

```text
Jellyfin
Beszel
Uptime Kuma
Pi-hole web
Pterodactyl Panel
```

may become inaccessible through their normal HTTPS hostnames.

This makes Nginx a particularly important monitoring target.

---

# Monitoring Philosophy

Monitoring should be layered.

```text
                    Homelab
                       │
          ┌────────────┴────────────┐
          │                         │
       Beszel                  Uptime Kuma
          │                         │
          ▼                         ▼
 Resource health              Availability
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
                 Troubleshooting
```

For example:

```text
Beszel:
CPU / RAM / disk abnormal

Uptime Kuma:
Service still responding
```

or:

```text
Beszel:
Host healthy

Uptime Kuma:
Service unavailable
```

These indicate different classes of problems.

---

# Troubleshooting

## Check Container

From Proxmox:

```bash
pct status 105
```

The container should be running.

---

## Check Service

Inside CT105:

```bash
systemctl status uptime-kuma
```

If the service is managed differently by the installed deployment, inspect the active process/container instead.

---

# Check Listening Port

```bash
ss -lntp | grep 3001
```

The expected service port is:

```text
3001
```

---

# Test Backend

From CT106:

```bash
curl -I http://192.168.20.95:3001
```

If this succeeds, CT105 is responding to Nginx.

---

# Test DNS

From a LAN client:

```bash
dig @192.168.20.99 status.robynshomelab.dev
```

Expected internal result:

```text
192.168.20.94
```

---

# Test HTTPS

```bash
curl -I https://status.robynshomelab.dev
```

If this fails while the backend works directly, investigate:

```text
Pi-hole
   ↓
Nginx
   ↓
TLS certificate
   ↓
Uptime Kuma
```

---

# Nginx Troubleshooting

On CT106:

```bash
nginx -t
```

Then:

```bash
systemctl status nginx
```

Check logs if required:

```bash
journalctl -u nginx
```

or:

```bash
ls -lah /var/log/nginx/
```

---

# NetBird Troubleshooting

From a remote NetBird client:

```bash
ping 192.168.20.94
```

Then:

```bash
curl -I https://status.robynshomelab.dev
```

If the Nginx address cannot be reached, troubleshoot CT101 and its advertised route before troubleshooting Uptime Kuma.

---

# Alerting

Uptime Kuma can be used to notify when monitored services become unavailable.

The exact notification channels should be documented once configured.

Potential notification methods include:

* Email
* Push notifications
* Messaging services
* Webhooks

Notifications should be configured carefully to avoid excessive alerts.

---

# Dependency Considerations

Some services depend on other infrastructure.

For example:

```text
Client
  │
  ▼
Pi-hole
  │
  ▼
Nginx
  │
  ▼
Jellyfin
```

A failure of Pi-hole can therefore make a healthy Jellyfin service appear unavailable through its hostname.

Similarly, a failure of Nginx can make several healthy backend services appear unavailable.

When investigating alerts, check infrastructure dependencies rather than assuming every alert represents an independent service failure.

---

# Security

Uptime Kuma is not directly exposed through router port forwarding.

Access is provided through:

* LAN
* Nginx
* HTTPS
* NetBird

The backend port:

```text
3001
```

should remain internal.

---

# Operational Principles

The current Uptime Kuma deployment follows these principles:

* Runs on CT105
* Uses `192.168.20.95`
* Uses port `3001`
* Uses Nginx for HTTPS access
* Uses Pi-hole split DNS
* Uses NetBird for remote private access
* Monitors service availability rather than detailed resource metrics
* Works alongside Beszel
* Does not require router port forwarding

---

# Future Improvements

Potential future improvements include:

* Complete service monitor coverage
* Pterodactyl Panel and Wings monitoring
* DNS monitoring
* NFS/storage availability checks
* Proxmox host monitoring
* Notification configuration
* Dependency-aware monitoring
* More detailed endpoint checks
* Monitoring of backup jobs

Any newly deployed monitor should be documented here once it has been tested.
