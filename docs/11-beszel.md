# Beszel

Beszel is the homelab's lightweight monitoring system.

It runs on CT104 and provides monitoring and historical metrics for homelab infrastructure.

---

# Container

```text
VMID:     104
Hostname: beszel
IP:       192.168.20.96
Host:     pve-1
```

Beszel is accessed through Nginx using:

```text
https://beszel.robynshomelab.dev
```

---

# Architecture

```text
                         Beszel
                    192.168.20.96
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          Proxmox       Containers      VMs
          Hosts         / Services    / Services
```

Beszel uses a central hub/monitoring service with agents providing host-level metrics.

---

# Purpose

Beszel is intended to provide lightweight infrastructure monitoring without requiring a large monitoring stack.

Useful metrics include:

* CPU usage
* Memory usage
* Disk usage
* Network activity
* System load
* Host availability
* Historical resource utilisation

---

# Current Deployment

The Beszel service is hosted on CT104:

```text
192.168.20.96
```

The web interface is reverse-proxied through CT106:

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
192.168.20.96:8090
  │
  ▼
Beszel
```

The internal backend is:

```text
192.168.20.96:8090
```

---

# DNS

Pi-hole provides the internal DNS record:

```text
beszel.robynshomelab.dev
```

which resolves to:

```text
192.168.20.94
```

Nginx then proxies the request to Beszel.

This means users do not need to access the Beszel backend port directly.

---

# HTTPS

Nginx provides HTTPS for the Beszel interface:

```text
https://beszel.robynshomelab.dev
```

The TLS certificate is managed by Certbot on CT106 using Let's Encrypt DNS-01 validation through Cloudflare.

The certificate currently expires:

```text
2026-12-04
```

---

# NetBird Access

Remote access uses NetBird.

CT101 advertises:

```text
192.168.20.94/32
```

to NetBird clients.

The remote access path is therefore:

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
192.168.20.96:8090
        │
        ▼
Beszel
```

Pi-hole also provides DNS to NetBird clients, allowing the normal hostname to be used remotely.

---

# Monitoring Architecture

Beszel is intended to monitor the important infrastructure components of the homelab.

The broader monitoring architecture is:

```text
                     Monitoring
                         │
          ┌──────────────┴──────────────┐
          │                             │
        Beszel                     Uptime Kuma
          │                             │
   System metrics                  Availability
          │                             │
          └──────────────┬──────────────┘
                         │
                    Homelab hosts
```

Beszel focuses primarily on system/resource metrics.

Uptime Kuma focuses primarily on service availability and uptime.

---

# Host Monitoring

Potential monitoring targets include:

```text
pve-1
pve-2
CT100 Pi-hole
CT101 NetBird
CT102 Jellyfin
CT103 Media Stack
CT104 Beszel
CT105 Uptime Kuma
CT106 Nginx
VM108 Pterodactyl
```

The exact set of active Beszel agents should be treated as the deployed configuration rather than assuming every host above is currently monitored.

---

# Pterodactyl Monitoring

VM108 is part of the homelab infrastructure but its Beszel monitoring is not yet considered fully configured.

Future monitoring should cover:

```text
VM108
├── CPU
├── Memory
├── Disk
├── Network
├── Docker
└── Wings / game-server workload
```

This is particularly useful because Pterodactyl can generate significantly different resource usage from the other homelab services.

---

# Storage Monitoring

Storage monitoring is particularly important because the homelab uses a single 4TB HDD as its primary shared media/data storage.

The drive is located in pve-2.

```text
pve-2
  │
  ▼
4TB WD Blue
  │
  ├── media
  ├── downloads
  ├── games
  ├── backups
  └── shared
```

Monitoring should eventually include:

* Filesystem utilisation
* Disk health
* SMART status
* Available capacity
* I/O activity

Beszel provides general system metrics, while SMART health checks may require additional tooling.

---

# Monitoring Philosophy

The homelab uses two complementary monitoring systems.

## Beszel

Best suited to:

* CPU
* RAM
* Disk usage
* Network usage
* System resource trends

## Uptime Kuma

Best suited to:

* HTTP availability
* TCP availability
* Service uptime
* Endpoint monitoring
* Availability alerts

Together:

```text
Resource health
      │
      ▼
    Beszel

Service availability
      │
      ▼
 Uptime Kuma
```

---

# Access

The preferred web address is:

```text
https://beszel.robynshomelab.dev
```

The backend should normally be accessed through Nginx rather than directly using:

```text
http://192.168.20.96:8090
```

Direct backend access remains useful for troubleshooting.

---

# Troubleshooting

## Check CT104

From Proxmox:

```bash
pct status 104
```

The container should be running.

---

## Check Listening Port

Inside CT104:

```bash
ss -lntp | grep 8090
```

The Beszel service should be listening on its configured port.

---

## Test Backend

From CT106:

```bash
curl -I http://192.168.20.96:8090
```

If this succeeds but the HTTPS hostname fails, investigate Nginx or DNS.

---

## Test DNS

From a LAN client:

```bash
dig @192.168.20.99 beszel.robynshomelab.dev
```

Expected internal result:

```text
192.168.20.94
```

---

## Test HTTPS

```bash
curl -I https://beszel.robynshomelab.dev
```

If the hostname resolves correctly but HTTPS fails, check:

```text
Pi-hole
   ↓
Nginx
   ↓
Certbot certificate
   ↓
Beszel backend
```

---

# Nginx Troubleshooting

On CT106:

```bash
nginx -t
```

Then check:

```bash
systemctl status nginx
```

Review logs if necessary:

```bash
journalctl -u nginx
```

or:

```bash
ls -lah /var/log/nginx/
```

---

# NetBird Troubleshooting

From a NetBird client, verify that Nginx is reachable:

```bash
ping 192.168.20.94
```

Then test the Beszel hostname:

```bash
curl -I https://beszel.robynshomelab.dev
```

If Nginx is reachable but the Beszel service is not, troubleshoot CT104 and the Nginx backend connection.

---

# Operational Separation

Beszel should not be confused with Uptime Kuma.

```text
Beszel
└── "How is the machine performing?"

Uptime Kuma
└── "Is the service reachable?"
```

For example, a server could be:

```text
Beszel → high CPU usage
Uptime Kuma → service still online
```

Both pieces of information are useful.

---

# Security

Beszel is not directly exposed through router port forwarding.

The current access model is:

```text
LAN
 │
 ▼
Pi-hole
 │
 ▼
Nginx
 │
 ▼
Beszel
```

and remotely:

```text
NetBird
 │
 ▼
CT101
 │
 ▼
Nginx
 │
 ▼
Beszel
```

The Beszel backend port should remain internal.

---

# Future Improvements

Potential future improvements include:

* Complete monitoring coverage of all Proxmox hosts
* Add VM108/Pterodactyl monitoring
* Monitor NFS storage
* Monitor SMART health
* Monitor Docker resource usage
* Add disk-capacity alerts
* Add CPU/memory alerts
* Configure notification channels
* Improve monitoring of NetBird and network infrastructure
* Add monitoring for backup jobs

Monitoring configuration should be updated here as additional hosts and services are deployed.
