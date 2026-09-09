# Pterodactyl

Pterodactyl provides game server management through a web-based Panel and Wings daemon.

The deployment runs independently on VM108 rather than inside the Proxmox LXC media stack.

---

# Virtual Machine

```text
VMID:     108
Hostname: pterodactyl
IP:       192.168.20.111
Host:     pve-2
OS:       Debian 13 Trixie
vCPU:     6
RAM:      12 GB
Disk:     40 GB virtual disk
```

The VM also has access to the physical game-storage NFS share provided by pve-2.

---

# Architecture

```text
                         User
                           │
                           ▼
                 panel.robynshomelab.dev
                           │
                           ▼
                    Nginx / CT106
                    192.168.20.94
                           │
                           ▼
                  Pterodactyl Panel
                    VM108 / .111
                           │
                           ▼
                         Wings
                    VM108 / .111
                           │
                           ▼
                   Docker containers
                           │
                           ▼
                     Game servers
```

The Panel and Wings daemon run on the same VM but perform different roles.

---

# Software Stack

The VM currently runs:

| Component         | Version / Role        |
| ----------------- | --------------------- |
| Debian            | 13 Trixie             |
| Docker Engine     | 29.8.0                |
| containerd        | 2.3.5                 |
| runc              | 1.5.1                 |
| PHP               | 8.3.33                |
| PHP-FPM           | 8.3.33                |
| MariaDB           | 11.8.6                |
| Redis             | Installed             |
| Composer          | 2.10.3                |
| Nginx             | Installed             |
| Pterodactyl Panel | Production deployment |
| Wings             | 1.13.3                |

---

# Pterodactyl Panel

The Panel is installed at:

```text
/var/www/pterodactyl
```

The application runs in production mode:

```text
APP_ENV=production
APP_DEBUG=false
```

The application timezone is:

```text
Australia/Melbourne
```

The public application URL is:

```text
https://panel.robynshomelab.dev
```

The Panel uses the local MariaDB and Redis services on VM108.

---

# Panel Database

The Panel database is hosted locally on VM108 using MariaDB.

The database is used for Pterodactyl application state, including:

* Users
* Servers
* Nodes
* Locations
* Allocations
* Application configuration
* Other Panel metadata

Database credentials should not be stored in this documentation.

---

# Redis

Redis provides the Panel's queue/cache functionality.

The Panel is configured to use Redis for its queue backend.

Redis is local to VM108.

---

# Panel Setup

The initial Panel deployment has been completed.

The following setup tasks have been performed:

* Application installed
* Production environment configured
* Database created
* Database migrations completed
* Database seeders completed
* Administrator account created
* Storage link created
* Application URL configured
* HTTPS configured through Nginx
* Wings node configured
* Wings daemon connected to the Panel

---

# Nginx and HTTPS

The Panel is accessed through:

```text
https://panel.robynshomelab.dev
```

The request path is:

```text
Client
  │
  ▼
DNS
  │
  ▼
192.168.20.94
  │
  ▼
Nginx / CT106
  │
  ▼
192.168.20.111:80
  │
  ▼
Pterodactyl Panel
```

Nginx handles TLS termination.

The Panel backend itself listens over HTTP on the internal network.

---

# Cloudflare DNS

Cloudflare is authoritative for:

```text
robynshomelab.dev
```

The public Panel hostname is retained in Cloudflare DNS:

```text
panel.robynshomelab.dev
```

The public record is DNS-only.

It is retained primarily for:

* Public hostname consistency
* DNS-01 certificate validation
* Future access requirements

The presence of a public DNS record does **not** mean the Panel is directly reachable from the Internet.

There is currently no router port forwarding for the Panel.

---

# Internal DNS

Pi-hole provides the internal split-DNS record:

```text
panel.robynshomelab.dev
    ↓
192.168.20.94
```

This allows LAN clients to use the same hostname while traffic remains inside the homelab.

---

# NetBird Access

The Panel can be accessed remotely through NetBird.

The remote path is:

```text
NetBird client
      │
      ▼
CT101
192.168.20.97
      │
      ▼
192.168.20.94
      │
      ▼
Nginx / CT106
      │
      ▼
192.168.20.111
      │
      ▼
Pterodactyl Panel
```

CT101 advertises the Nginx address:

```text
192.168.20.94/32
```

The Panel therefore does not need to be directly exposed to the Internet.

---

# Wings

Wings is the Pterodactyl daemon responsible for actually running game servers.

Binary:

```text
/usr/local/bin/wings
```

Version:

```text
1.13.3
```

Configuration:

```text
/etc/pterodactyl/config.yml
```

The Wings configuration file is protected with:

```text
chmod 600 /etc/pterodactyl/config.yml
```

because it contains sensitive configuration.

---

# Wings systemd Service

Wings is managed by systemd.

Service:

```text
/etc/systemd/system/wings.service
```

Check the service:

```bash
systemctl status wings
```

Start:

```bash
systemctl start wings
```

Stop:

```bash
systemctl stop wings
```

Restart:

```bash
systemctl restart wings
```

Enable at boot:

```bash
systemctl enable wings
```

View logs:

```bash
journalctl -u wings
```

Follow live logs:

```bash
journalctl -u wings -f
```

---

# Pterodactyl Node

The configured node is:

```text
Name:     pterodactyl
Location: Home
```

The node is configured as private.

Node FQDN:

```text
wings.robynshomelab.dev
```

SSL is enabled.

The node is not configured as being behind a proxy.

---

# Wings Network

The Wings daemon uses:

```text
Daemon port: 8080
SFTP port:   2022
```

The SFTP service allows appropriate Pterodactyl server-file management.

The daemon port is used for Panel ↔ Wings communication.

---

# Game Server Storage

Game server data is stored under:

```text
/var/lib/pterodactyl/volumes
```

This is the Wings daemon directory for server volumes.

The VM also mounts the dedicated NFS `games` share from pve-2.

The architecture is:

```text
pve-2
  │
  ▼
/mnt/homelab-data/games
  │
  │ NFS
  ▼
VM108
  │
  ▼
Pterodactyl game storage
```

The NFS share has been tested successfully by creating a file from VM108.

---

# Game Server Containers

Pterodactyl uses Docker containers for individual game servers.

The architecture is:

```text
Wings
 │
 ├── Docker container
 │     └── Game server A
 │
 ├── Docker container
 │     └── Game server B
 │
 └── Docker container
       └── Game server C
```

Each Pterodactyl server is managed independently through the Panel.

---

# Resource Allocation

The current node configuration provides:

```text
Memory:  10240 MiB
Disk:    30720 MiB
```

The VM itself has:

```text
6 vCPU
12 GB RAM
```

The available game-server resources therefore need to remain within the VM's physical allocation.

---

# Node and Allocation Management

The Panel controls:

* Nodes
* Locations
* Allocations
* Servers
* Users
* Resource limits
* Docker images
* Startup commands
* Environment variables

Wings executes the configuration received from the Panel.

---

# Panel ↔ Wings Relationship

The Panel and Wings have separate responsibilities:

```text
Pterodactyl Panel
├── Web interface
├── User management
├── Server configuration
├── Node management
└── API

        │
        │ API / daemon communication
        ▼

Wings
├── Docker management
├── Server lifecycle
├── Console
├── File operations
└── Resource enforcement
```

If the Panel is unavailable, existing game servers managed by Wings may continue running, but Panel-based management will be unavailable.

If Wings is unavailable, the Panel may remain accessible but game-server management and execution will be affected.

---

# NetBird Configuration

VM108 runs its own NetBird client independently from CT101.

Current NetBird version:

```text
0.78.1
```

NetBird FQDN:

```text
pterodactyl.netbird.cloud
```

NetBird address:

```text
100.113.229.169/16
```

CT101 and VM108 are separate NetBird peers.

The VM does not depend on CT101 to function as a NetBird peer.

---

# Current Remote Access Architecture

The Panel uses CT101 as a routed path to Nginx:

```text
Remote device
     │
     ▼
NetBird
     │
     ▼
CT101
100.113.51.59
     │
     ▼
192.168.20.94
     │
     ▼
Nginx
     │
     ▼
192.168.20.111
```

VM108's own NetBird peer is separate and can be used for direct private access where appropriate.

---

# Firewall Status

The VM's final firewall hardening has not yet been completed.

The intended firewall implementation is **nftables** rather than UFW.

This is important because Pterodactyl relies heavily on Docker networking, and Docker can interact with firewall rules and packet forwarding.

Firewall changes should therefore be tested carefully against:

* Panel access
* Wings ↔ Panel communication
* Docker networking
* Game-server networking
* SFTP
* NFS
* NetBird

Do not assume a generic UFW configuration is appropriate for this VM.

---

# Troubleshooting

## Check Panel

Check the application directory:

```bash
cd /var/www/pterodactyl
```

Check Nginx:

```bash
nginx -t
systemctl status nginx
```

---

## Check PHP-FPM

```bash
systemctl status php8.3-fpm
```

Check PHP version:

```bash
php -v
```

---

## Check MariaDB

```bash
systemctl status mariadb
```

---

## Check Redis

```bash
systemctl status redis
```

The exact service name may be verified with:

```bash
systemctl list-units --type=service | grep -i redis
```

---

## Check Wings

```bash
systemctl status wings
```

Then inspect:

```bash
journalctl -u wings -n 100 --no-pager
```

---

## Check Docker

```bash
docker info
```

and:

```bash
docker ps
```

---

## Check NFS

```bash
findmnt
```

Look specifically for the game-storage mount.

Test access:

```bash
ls -lah /mnt/homelab-data/games
```

or the corresponding mounted path configured on VM108.

---

# Panel Access Troubleshooting

If:

```text
https://panel.robynshomelab.dev
```

does not work, check the dependency chain in order:

```text
DNS
 ↓
192.168.20.94
 ↓
Nginx
 ↓
192.168.20.111:80
 ↓
Pterodactyl Panel
 ↓
PHP-FPM
 ↓
MariaDB / Redis
```

For remote access, also verify:

```text
NetBird
 ↓
CT101
 ↓
192.168.20.94
```

---

# Wings Troubleshooting

If the Panel is accessible but Wings is offline:

```bash
systemctl status wings
```

Then:

```bash
journalctl -u wings -n 100 --no-pager
```

Check that Docker is operational:

```bash
systemctl status docker
docker info
```

Also verify that the configured Wings endpoint and SSL settings match the Panel node configuration.

---

# Security Principles

The Pterodactyl deployment follows these principles:

* Panel is accessed through HTTPS
* TLS is terminated by Nginx
* No router port forwarding is currently configured
* Internal DNS resolves the Panel hostname to Nginx
* NetBird provides private remote access
* Wings configuration is protected from other users
* Game servers run in Docker containers
* Firewall hardening will use nftables
* Secrets are not stored in this documentation

---

# Current State

The following components are deployed and operational:

```text
VM108
 ├── Debian 13
 ├── Docker
 ├── MariaDB
 ├── Redis
 ├── PHP-FPM
 ├── Nginx
 ├── Pterodactyl Panel
 ├── Wings
 ├── NetBird
 └── NFS game storage
```

The Panel is accessible through:

```text
https://panel.robynshomelab.dev
```

Wings is installed, enabled, and running.

The Pterodactyl node is configured and connected to the Panel.

---

# Future Improvements

Potential future work includes:

* Complete nftables firewall configuration
* More comprehensive Wings monitoring
* Game-server monitoring through Uptime Kuma/Beszel
* Backup strategy for Panel data
* Backup strategy for game-server data
* Resource allocation tuning
* Additional game-server deployments
* Improved remote game-server networking
* Further testing of direct NetBird access
* Documenting individual game-server configurations as they are deployed

Any future firewall or networking changes should preserve the current separation between:

```text
Panel
Wings
Docker
NFS storage
NetBird
Nginx
```
