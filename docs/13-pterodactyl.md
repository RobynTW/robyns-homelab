# Pterodactyl Game Server

## Overview

Pterodactyl is the game-server management platform for the homelab.

It runs on the Dell OptiPlex 9020 SFF inside a dedicated Debian 13 KVM virtual machine.

The deployment is intentionally isolated from the Proxmox host and from the future NAS/file-sharing workload.

Current architecture:

```text
Dell OptiPlex 9020
│
└── Proxmox pve-2
    │
    └── VM 108
        │
        └── Debian 13
            │
            ├── Pterodactyl Panel
            ├── MariaDB
            ├── Redis
            ├── PHP 8.3
            ├── PHP-FPM
            ├── Composer
            └── Docker
```

Wings has not yet been installed.

Game servers have not yet been created.

---

# Host

Pterodactyl runs on:

```text
Host: Dell OptiPlex 9020 SFF
Proxmox node: pve-2
Host IP: 192.168.20.101
```

The Pterodactyl workload is intentionally kept separate from the future NAS/storage workload.

The 4 TB WD Blue `WD40EZRZ` planned for the 9020 is intended for network file sharing and is not currently used by Pterodactyl.

---

# Pterodactyl VM

## VM Identification

```text
VMID:     108
Hostname: pterodactyl
IP:       192.168.20.111
```

## Operating System

```text
OS: Debian GNU/Linux 13 (Trixie)
Kernel: 6.12.107+deb13-amd64
Virtualisation: KVM
```

The VM is headless and is administered using SSH.

SSH:

```bash
ssh robyn@192.168.20.111
```

---

# VM Resource Allocation

The current VM allocation is:

```text
CPU:
    6 vCPU
    1 socket
    6 cores
    CPU type: host

Memory:
    12 GB

Disk:
    40 GB
    local-lvm
```

The VM uses:

```text
Machine: Q35
Firmware: OVMF / UEFI
SCSI: VirtIO SCSI single
Network: VirtIO
Bridge: vmbr0
QEMU Guest Agent: enabled
NUMA: disabled
Ballooning: disabled
Nested virtualisation: disabled
```

Disk options:

```text
Cache: none
Discard: enabled
IO thread: enabled
SSD emulation: enabled
Backup: enabled
```

---

# Initial Debian Configuration

The Debian installation was performed without a desktop environment.

Installed components included:

* SSH server
* Standard system utilities
* `sudo`

The primary administrative user is:

```text
robyn
```

The user was added to the sudo group.

Root access is therefore normally performed using:

```bash
sudo -i
```

or individual commands using:

```bash
sudo <command>
```

---

# Base Packages

The following base packages were installed:

```bash
curl
ca-certificates
gnupg2
sudo
lsb-release
```

These provide the utilities required for the Pterodactyl installation and repository configuration.

---

# Docker

Docker Engine was installed inside the Pterodactyl VM.

The installation used Docker's official installation mechanism:

```bash
curl -sSL https://get.docker.com/ | CHANNEL=stable bash
```

Docker was then enabled and started:

```bash
systemctl enable --now docker
```

The installed Docker environment was verified as operational.

Docker is installed inside VM 108 rather than directly on the Proxmox host.

This allows Wings to manage isolated game-server containers without placing Docker workloads directly on Proxmox.

---

# PHP

Pterodactyl requires PHP 8.3 for the current deployment.

The Debian system uses the Sury PHP repository.

Repository configuration:

```bash
echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" \
  > /etc/apt/sources.list.d/sury-php.list

curl -fsSL https://packages.sury.org/php/apt.gpg \
  | gpg --dearmor -o /etc/apt/trusted.gpg.d/sury-keyring.gpg

apt update
```

Installed PHP components include:

```text
php8.3
php8.3-common
php8.3-cli
php8.3-gd
php8.3-mysql
php8.3-mbstring
php8.3-bcmath
php8.3-xml
php8.3-fpm
php8.3-curl
php8.3-zip
```

Verified PHP version:

```text
PHP 8.3.33
```

PHP-FPM is enabled and running.

---

# MariaDB

MariaDB is used as the Pterodactyl Panel database.

Installed version:

```text
MariaDB 11.8.6
```

The MariaDB service is enabled and running.

Database:

```text
panel
```

Database user:

```text
pterodactyl
```

The user has privileges over the `panel` database.

The database account is configured for local access.

The database password is intentionally not documented.

---

# Redis

Redis is installed for Pterodactyl's caching/queue requirements.

The Redis service is enabled and running.

The installation was deliberately performed separately from the main dependency installation after the initial package installation appeared to pause during the Redis portion.

Package state was verified using:

```bash
dpkg --audit
```

and:

```bash
apt-get --fix-broken install
```

No broken packages remained.

---

# Nginx and PHP-FPM

Nginx is installed inside the Pterodactyl VM because it is part of the standard Pterodactyl Panel application stack.

However, the VM's Nginx is **not currently intended to be the public HTTPS reverse proxy**.

The homelab already has Nginx running on the existing infrastructure host:

```text
CT 100
192.168.20.99
```

The existing Nginx/Certbot infrastructure should remain the public HTTPS termination point.

The intended architecture is therefore:

```text
Internet
   │
   │ HTTPS
   ▼
CT 100
192.168.20.99
Nginx
   │
   │ HTTP/internal proxy
   ▼
VM 108
192.168.20.111
Pterodactyl Panel
```

The exact reverse-proxy configuration will be implemented later.

---

# Composer

Composer was installed for PHP dependency management.

Verified version:

```text
Composer 2.10.3
PHP 8.3.33
```

---

# Pterodactyl Panel Installation

The Panel was installed under:

```text
/var/www/pterodactyl
```

The current Panel release was downloaded from the Pterodactyl release repository and extracted into this directory.

Ownership was set to:

```text
www-data:www-data
```

Permissions were configured so that the Panel's application directories are accessible by the web service.

The writable directories include:

```text
/var/www/pterodactyl/storage
/var/www/pterodactyl/bootstrap/cache
```

---

# Composer Dependencies

Pterodactyl's PHP dependencies were installed using:

```bash
sudo -u www-data composer install --no-dev --optimize-autoloader
```

Composer successfully installed the Panel dependencies and generated the optimized autoloader.

The initial Composer run displayed an application encryption-key warning because the Panel had not yet been configured.

This was expected and was resolved during the environment configuration stage.

---

# Environment Configuration

The Panel environment file was created from the example configuration:

```bash
cp .env.example .env
```

The Laravel application key was then generated:

```bash
php artisan key:generate --force
```

The command completed successfully with:

```text
Application key set successfully.
```

The `.env` file contains the MariaDB connection details.

Database credentials are intentionally not documented.

---

# Database Migration

After configuring the database connection, the Panel database connection was tested using:

```bash
php artisan migrate:status
```

The first test successfully reached MariaDB but reported:

```text
ERROR  Migration table not found.
```

This confirmed that the database credentials and connection were functioning correctly and that the database had not yet been initialised.

The database was then initialised using:

```bash
php artisan migrate --seed --force
```

The migrations and database seed completed successfully.

---

# Administrator Account

A Pterodactyl administrator account was created using:

```bash
php artisan p:user:make
```

The account was created with administrator privileges.

The administrator account is:

```text
Username: robyn
Name: Robyn Walker
Administrator: Yes
```

The account password is intentionally not documented.

---

# Current Panel State

The Pterodactyl Panel is installed and its database is initialised.

Current state:

```text
Panel:       Installed
Database:    Configured
Migrations:  Complete
Admin user:  Created
PHP:         Operational
MariaDB:     Operational
Redis:       Operational
Composer:     Operational
Docker:      Operational
Nginx:       Installed
```

The Panel has not yet been integrated into the homelab's external HTTPS architecture.

---

# Domain

The homelab domain is:

```text
robynshomelab.dev
```

The intended Pterodactyl Panel hostname is:

```text
panel.robynshomelab.dev
```

This hostname has not yet been configured as part of the Pterodactyl deployment.

The existing homelab Nginx/Certbot infrastructure should be used for public HTTPS termination rather than creating a second independent public reverse-proxy architecture on VM 108.

---

# Network Architecture

The Pterodactyl VM is directly connected to the homelab LAN:

```text
192.168.20.0/24
```

Current VM address:

```text
192.168.20.111
```

The intended service architecture is:

```text
                         Internet
                            │
                            │ HTTPS
                            ▼
                    ┌───────────────┐
                    │ CT 100        │
                    │ Nginx/Certbot │
                    │ 192.168.20.99 │
                    └───────┬───────┘
                            │
                            │ HTTP
                            ▼
                    ┌───────────────┐
                    │ VM 108        │
                    │ Pterodactyl   │
                    │ 192.168.20.111│
                    └───────┬───────┘
                            │
                            ▼
                         Panel
```

Game-server traffic will be handled separately.

---

# NetBird Integration

The existing NetBird routing peer is:

```text
CT 101
192.168.20.97
```

It currently provides private access to the homelab.

The Pterodactyl deployment will not repurpose CT 101 for game-server workloads.

The exact Pterodactyl/NetBird design is still being finalised.

The intended separation is:

```text
Existing homelab access
        │
        ▼
CT 101 NetBird
        │
        ▼
Homelab services


Pterodactyl game access
        │
        ▼
Pterodactyl / NetBird
        │
        ▼
Wings
        │
        ▼
Docker game servers
```

No final game-server exposure configuration has yet been deployed.

---

# Wings

Wings is **not yet installed**.

Wings will be installed inside VM 108.

Its role will be:

```text
Pterodactyl Panel
       │
       │ API
       ▼
     Wings
       │
       ▼
    Docker
       │
       ├── Game Server
       ├── Game Server
       └── Game Server
```

Wings will be responsible for managing the Docker containers that run individual game servers.

---

# Game Servers

No game servers have been created yet.

The primary intended workload is modded Minecraft.

Future game servers will be created through the Pterodactyl Panel after Wings is operational.

Each server will receive explicitly configured:

* CPU allocation
* Memory allocation
* Storage allocation
* Network allocation
* Game-specific ports

---

# Storage

The current Pterodactyl VM has:

```text
40 GB virtual disk
```

on the 9020's SSD-backed Proxmox storage.

The 4 TB WD Blue HDD planned for the 9020 is **not currently attached to Pterodactyl**.

That HDD is intended for a separate network file-sharing/NFS workload.

Pterodactyl game-server storage should therefore remain on the VM unless a deliberate shared-storage architecture is designed later.

---

# Security Model

The Panel is treated as an administrative service.

It should not be unnecessarily exposed directly to the public internet.

The preferred model is:

```text
Panel
└── HTTPS through existing Nginx infrastructure

Wings
└── Only required Panel communication

Game servers
└── Controlled access through the planned NetBird architecture
```

Passwords, database credentials, application keys, API tokens and private keys must never be committed to Git.

---

# Remaining Deployment Tasks

The following tasks remain:

```text
[✓] Install Proxmox on 9020
[✓] Integrate pve-2 into homelab cluster
[✓] Create VM 108
[✓] Install Debian 13
[✓] Configure SSH/sudo
[✓] Install Docker
[✓] Install PHP 8.3
[✓] Install MariaDB
[✓] Install Redis
[✓] Install Nginx/PHP-FPM
[✓] Install Composer
[✓] Install Pterodactyl Panel
[✓] Configure .env
[✓] Generate application key
[✓] Configure MariaDB
[✓] Run migrations/seeding
[✓] Create administrator account
[ ] Configure Panel URL
[ ] Configure existing Nginx reverse proxy
[ ] Configure TLS/Certbot
[ ] Install Wings
[ ] Connect Wings to Panel
[ ] Configure Docker/Pterodactyl node
[ ] Configure NetBird game-server networking
[ ] Create first game server
[ ] Configure game-server allocations
[ ] Configure backups
[ ] Add Uptime Kuma monitoring
[ ] Add Beszel monitoring
```

---

# Deployment Order

The remaining deployment should proceed in stages:

```text
Current state
     │
     ▼
Configure Panel hostname
     │
     ▼
Configure existing Nginx reverse proxy
     │
     ▼
Configure TLS
     │
     ▼
Install Wings
     │
     ▼
Connect Wings to Panel
     │
     ▼
Verify Docker integration
     │
     ▼
Configure NetBird
     │
     ▼
Create first game server
     │
     ▼
Test remote game access
     │
     ▼
Configure monitoring
     │
     ▼
Configure backups
```

Each stage should be tested before moving to the next.

---

# Useful Commands

## Check Panel files

```bash
ls -la /var/www/pterodactyl
```

## Check PHP

```bash
php -v
```

## Check Composer

```bash
composer --version
```

## Check MariaDB

```bash
systemctl status mariadb
```

## Check Redis

```bash
systemctl status redis-server
```

## Check Nginx

```bash
systemctl status nginx
```

## Check PHP-FPM

```bash
systemctl status php8.3-fpm
```

## Check Docker

```bash
docker version
```

```bash
systemctl status docker
```

## Check listening ports

```bash
ss -tulpn
```

## Check Pterodactyl migrations

```bash
php artisan migrate:status
```

---

# Current Status

```text
Pterodactyl:
    Status: Panel installed

Host:
    Dell OptiPlex 9020
    pve-2
    192.168.20.101

VM:
    108
    pterodactyl
    192.168.20.111

OS:
    Debian 13 Trixie

Panel:
    Installed and database initialised

Database:
    MariaDB 11.8.6

Cache:
    Redis

PHP:
    8.3.33

Composer:
    2.10.3

Docker:
    Installed and operational

Wings:
    Not yet installed

NetBird:
    Pterodactyl integration not yet configured

Game servers:
    None

Panel hostname:
    panel.robynshomelab.dev
    Not yet configured

TLS:
    Not yet configured for Pterodactyl

Reverse proxy:
    To be integrated with existing CT 100 Nginx
```

---

# Related Documentation

The Pterodactyl deployment depends on:

```text
01-hardware.md
02-network.md
03-proxmox.md
08-netbird.md
10-beszel.md
11-uptime-kuma.md
```

The future NAS/NFS configuration will also be relevant if shared storage is introduced.

The existing Nginx and Certbot documentation should be consulted before configuring the Panel's external HTTPS access.
