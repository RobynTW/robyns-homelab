# Beszel Monitoring

## Overview

Beszel is the homelab's lightweight system-monitoring platform.

It runs in a dedicated Proxmox LXC:

```text
Proxmox pve-1
└── CT104
    ├── Hostname: beszel
    ├── IP: 192.168.20.96
    ├── 1 vCPU
    ├── 512 MB RAM
    ├── 256 MB swap
    └── 8 GB disk
```

The container hosts the Beszel Hub and the Beszel agent.

Beszel is used to monitor the health and resource usage of the homelab infrastructure.

## Network Details

| Component   | Address              |
| ----------- | -------------------- |
| Beszel LXC  | `192.168.20.96`      |
| Beszel Hub  | `192.168.20.96:8090` |
| Nginx       | `192.168.20.94`      |
| Proxmox     | `192.168.20.100`     |
| Pi-hole     | `192.168.20.99`      |
| NetBird     | `192.168.20.97`      |
| Jellyfin    | `192.168.20.98`      |
| Uptime Kuma | `192.168.20.95`      |

The Beszel web interface is accessed through Nginx:

```text
https://beszel.robynshomelab.dev
```

## Architecture

Beszel uses a hub-and-agent model.

```text
                    Beszel Hub
                 CT104 / .96
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
      Proxmox      Pi-hole     NetBird
      .100           .99         .97
          │
          ├── Jellyfin .98
          ├── Uptime Kuma .95
          └── other infrastructure
```

The Beszel agent provides system-level metrics from monitored hosts.

## Host Resources

The Beszel container is intentionally small because the monitoring service itself has relatively low resource requirements.

Current allocation:

```text
1 vCPU
512 MB RAM
256 MB swap
8 GB disk
```

The container runs Debian 12.

## Hub

The Beszel Hub listens on:

```text
192.168.20.96:8090
```

The local service can be tested with:

```bash
curl -I http://192.168.20.96:8090
```

A successful HTTP response confirms that the Hub is responding.

The Hub is not directly exposed through the router.

Instead, Nginx provides HTTPS access.

## Reverse Proxy

Nginx runs on CT106:

```text
192.168.20.94
```

The Beszel hostname is:

```text
beszel.robynshomelab.dev
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
Beszel Hub
192.168.20.96:8090
```

Pi-hole provides the internal DNS record:

```text
beszel.robynshomelab.dev → 192.168.20.94
```

The TLS certificate is managed by Certbot.

See:

```text
06-nginx.md
07-certbot.md
```

for the reverse-proxy and certificate configuration.

## Monitored Systems

The current Beszel installation monitors the following infrastructure:

```text
Proxmox
Pi-hole / Nginx
NetBird
Jellyfin
Beszel
```

The purpose is to provide visibility into the resource usage and availability of the core homelab services.

As additional infrastructure is deployed, further hosts can be added to Beszel.

## Proxmox Monitoring

The Proxmox host is monitored as:

```text
pve-1
192.168.20.100
```

This provides visibility into the physical host running the homelab's LXCs.

Monitoring the Proxmox host is particularly useful because a host-level failure can affect multiple services simultaneously.

## Pi-hole / Nginx Monitoring

The Pi-hole infrastructure is monitored through its host:

```text
192.168.20.99
```

The Nginx reverse proxy runs separately on:

```text
192.168.20.94
```

This distinction is important when troubleshooting.

A failure of Pi-hole can affect DNS for the entire homelab, while a failure of Nginx can affect HTTPS access to multiple services.

## NetBird Monitoring

NetBird runs on:

```text
192.168.20.97
```

Monitoring this host helps identify failures in the private remote-access infrastructure.

The NetBird container is separate from the future NetBird installation planned for the 9020 Pterodactyl VM.

## Jellyfin Monitoring

Jellyfin runs on:

```text
192.168.20.98
```

Beszel provides host-level resource monitoring for the Jellyfin container.

This is useful when investigating:

* CPU usage
* memory usage
* system load
* resource pressure during transcoding
* unexpected service behaviour

Jellyfin's Intel GPU is separately used for hardware acceleration.

## Beszel Monitoring

Beszel also monitors its own host:

```text
192.168.20.96
```

Self-monitoring provides visibility into the health of the monitoring service itself.

## Alerts

The current alert thresholds are:

| Metric      | Threshold |    Duration |
| ----------- | --------: | ----------: |
| CPU         |       90% |   5 minutes |
| Memory      |       90% |   5 minutes |
| Temperature |      80°C |   5 minutes |
| Offline     |         — | 2–3 minutes |

The duration requirements help prevent transient spikes from generating unnecessary alerts.

For example, a short CPU spike during a package update should not normally produce the same alert as sustained 90%+ utilisation.

## CPU Alerts

Current threshold:

```text
90% for 5 minutes
```

This is intended to identify sustained CPU pressure rather than momentary activity.

When investigating a CPU alert, first determine which service or workload caused the sustained utilisation.

## Memory Alerts

Current threshold:

```text
90% for 5 minutes
```

High memory usage may indicate:

* an unusually heavy workload
* a memory leak
* insufficient container allocation
* multiple processes competing for available memory

Memory pressure should be considered alongside swap usage.

## Temperature Alerts

Current threshold:

```text
80°C for 5 minutes
```

Temperature monitoring is particularly useful for the physical Proxmox host.

A sustained temperature alert may indicate:

* high CPU load
* inadequate airflow
* dust buildup
* fan problems
* high ambient temperature

## Offline Alerts

Hosts are considered problematic when they remain offline for approximately:

```text
2–3 minutes
```

This prevents very short interruptions from immediately generating alerts.

An offline alert should first be correlated with Uptime Kuma and Proxmox status to determine whether the problem is isolated to one service or affects the wider infrastructure.

## Monitoring Philosophy

Beszel and Uptime Kuma serve different purposes.

### Beszel

Beszel focuses primarily on:

```text
System health
Resource usage
CPU
Memory
Temperature
Disk/system metrics
```

### Uptime Kuma

Uptime Kuma focuses primarily on:

```text
Service availability
HTTP endpoints
TCP services
DNS services
Ping/reachability
```

Using both provides complementary monitoring.

For example:

```text
Jellyfin process running
        │
        ├── Beszel → system/resource health
        │
        └── Uptime Kuma → service availability
```

A service can therefore be running while experiencing resource problems, or a host can be healthy while an individual service has stopped responding.

## Troubleshooting

### Beszel Hub is unavailable

Check the service/process:

```bash
systemctl status beszel
```

If the service name differs, identify the running process:

```bash
ps aux | grep -i beszel
```

Check whether port 8090 is listening:

```bash
ss -tlnp | grep 8090
```

Test locally:

```bash
curl -I http://127.0.0.1:8090
```

### Nginx cannot reach Beszel

From CT106:

```bash
curl -I http://192.168.20.96:8090
```

If this fails, troubleshoot Beszel or the network before changing Nginx.

If it succeeds, check Nginx:

```bash
nginx -t
systemctl status nginx
```

### HTTPS access fails

Test:

```bash
curl -I https://beszel.robynshomelab.dev
```

Confirm DNS:

```bash
dig +short beszel.robynshomelab.dev
```

Expected:

```text
192.168.20.94
```

Then check the Nginx certificate and configuration.

### Agent is not reporting

Check the agent process on the monitored host.

Also verify basic connectivity between the monitored host and Beszel Hub.

Check network connectivity:

```bash
ping 192.168.20.96
```

Check the Hub:

```bash
curl -I http://192.168.20.96:8090
```

If the host is reachable but the agent is not reporting, investigate the agent service and its configuration.

### Monitoring shows unexpectedly high resource usage

Compare Beszel against Uptime Kuma and the relevant service's own logs.

For example, for Jellyfin:

```bash
systemctl status jellyfin
journalctl -u jellyfin --no-pager
```

For Proxmox, inspect the host and individual container workloads.

## Key Commands

| Command                                    | Purpose                          |
| ------------------------------------------ | -------------------------------- |
| `systemctl status beszel`                  | Check Beszel service status      |
| `ss -tlnp \| grep 8090`                    | Check the Beszel Hub listener    |
| `curl -I http://192.168.20.96:8090`        | Test the Hub directly            |
| `curl -I https://beszel.robynshomelab.dev` | Test HTTPS through Nginx         |
| `dig +short beszel.robynshomelab.dev`      | Verify internal DNS              |
| `ping 192.168.20.96`                       | Test network connectivity        |
| `ps aux \| grep -i beszel`                 | Check running Beszel processes   |
| `journalctl -u beszel --no-pager`          | View Beszel service logs         |
| `nginx -t`                                 | Validate the Nginx configuration |
| `systemctl status nginx`                   | Check the reverse proxy          |

## Future Monitoring

As the homelab expands, Beszel can be extended to monitor:

```text
Dell OptiPlex 9020
NAS
Pterodactyl VM
Media-stack containers
Additional infrastructure
```

The 9020 and its future services should be added after they are deployed rather than creating placeholder monitoring entries.

This keeps the monitoring configuration representative of the actual infrastructure.

## Relationship With Uptime Kuma

Beszel and Uptime Kuma are intentionally retained as separate monitoring systems.

The desired monitoring architecture is:

```text
                 Monitoring
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
       Beszel              Uptime Kuma
          │                     │
          │                     │
    System health          Service health
    Resource metrics       Availability
    CPU / RAM / temp       HTTP / TCP / DNS
```

This provides redundancy in monitoring methodology without requiring both systems to perform the same job.

## Current State

Beszel is operational on CT104:

```text
CT104 beszel
├── Debian 12
├── 192.168.20.96
├── 1 vCPU
├── 512 MB RAM
├── 256 MB swap
└── 8 GB disk
```

The Hub is available locally on:

```text
192.168.20.96:8090
```

HTTPS access is provided through Nginx:

```text
https://beszel.robynshomelab.dev
```

Current monitoring covers the core Proxmox infrastructure and service containers.

The current alert thresholds are:

```text
CPU:         90% / 5 min
Memory:      90% / 5 min
Temperature: 80°C / 5 min
Offline:     2–3 min
```

Uptime Kuma remains the complementary service-availability monitoring platform.
