# Pterodactyl

## Overview

Pterodactyl is the planned game-server management platform for the homelab.

The Pterodactyl Panel is currently deployed on a dedicated virtual machine.

The eventual primary workload is expected to be modded Minecraft, although additional game servers may be deployed in the future.

Current architecture:

    Client
      |
      | HTTPS
      v
    CT106 Nginx
    192.168.20.94
      |
      | HTTP
      v
    VM108 Pterodactyl
    192.168.20.111
      |
      v
    Pterodactyl Panel

Wings and game servers have not yet been deployed.

## VM108

VMID:

    108

Hostname:

    pterodactyl

Host:

    pve-2

IP address:

    192.168.20.111

Operating system:

    Debian 13 Trixie

Kernel:

    6.12.107+deb13-amd64

Virtualisation:

    KVM

CPU:

    6 vCPU
    1 socket
    6 cores
    CPU type: host

Memory:

    12 GB RAM

Storage:

    40 GB virtual disk
    local-lvm

Firmware:

    OVMF / UEFI

Machine type:

    Q35

Network:

    VirtIO on vmbr0

SCSI controller:

    VirtIO SCSI Single

QEMU Guest Agent:

    Enabled

NUMA:

    Disabled

Memory ballooning:

    Disabled

Nested virtualisation:

    Disabled

VM firewall:

    Currently disabled

The VM is headless and is administered through SSH.

SSH:

    ssh robyn@192.168.20.111

## Installed Software

The VM currently contains the software required for the Pterodactyl Panel.

Installed components include:

- Docker Engine Community
- containerd
- runc
- PHP 8.3
- PHP-FPM
- MariaDB
- Redis
- Composer
- Nginx
- Git
- curl
- ca-certificates
- gnupg2
- sudo
- lsb-release
- tar
- unzip

PHP packages are supplied through the Sury repository.

Current versions at deployment:

    Docker Engine: 29.8.0
    containerd: 2.3.5
    runc: 1.5.1
    PHP: 8.3.33
    MariaDB: 11.8.6
    Composer: 2.10.3

Versions may change through normal system updates.

## Pterodactyl Panel

Panel files are located at:

    /var/www/pterodactyl

The Panel uses:

    APP_ENV=production
    APP_DEBUG=false
    APP_TIMEZONE=Australia/Melbourne
    APP_URL=https://panel.robynshomelab.dev

The Panel uses MariaDB locally on VM108.

Database:

    panel

Database connection:

    127.0.0.1

Redis is used for the queue system.

The Laravel application key has been generated.

Database migrations and seed operations have been completed.

A Panel administrator account has been created.

Credentials are intentionally not documented.

## Local Nginx

VM108 runs a local Nginx instance in front of the Pterodactyl Laravel application.

The local backend is available at:

    http://127.0.0.1

A local request previously returned:

    HTTP 200

The service is also reachable from the LAN:

    http://192.168.20.111

A request to the LAN address previously returned:

    HTTP 200

The local Nginx configuration is responsible for serving the Panel application.

It does not provide the public TLS termination for the Panel.

## Reverse Proxy

The central reverse proxy is CT106.

CT106:

    nginx
    192.168.20.94

Pterodactyl:

    192.168.20.111

Public/internal hostname:

    panel.robynshomelab.dev

The intended traffic path is:

    Client
      |
      | HTTPS :443
      v
    CT106 Nginx
    192.168.20.94
      |
      | HTTP :80
      v
    VM108 Nginx
    192.168.20.111
      |
      v
    Pterodactyl Panel
      |
      +--> MariaDB
      |
      +--> Redis

TLS termination occurs on CT106.

Traffic between CT106 and VM108 is currently HTTP on the internal LAN.

## DNS

Pi-hole provides internal split DNS.

The internal record is:

    panel.robynshomelab.dev -> 192.168.20.94

This means internal clients reach the reverse proxy rather than connecting directly to VM108.

The public Cloudflare record remains:

    panel.robynshomelab.dev -> WAN IP

Cloudflare is DNS-only and is not acting as a traffic proxy.

The public record is retained for public DNS and ACME DNS-01 validation.

There is currently no router port forwarding exposing the Panel to the Internet.

## NetBird Access

NetBird clients access the Panel through CT101's existing route to CT106.

NetBird routing peer:

    CT101
    192.168.20.97

Route:

    192.168.20.94/32

Traffic path:

    NetBird Client
          |
          v
    CT101 NetBird
    192.168.20.97
          |
          v
    CT106 Nginx
    192.168.20.94
          |
          v
    VM108
    192.168.20.111
          |
          v
    Pterodactyl Panel

A direct NetBird route to VM108 is not required for the current Panel access architecture.

## TLS

TLS for the Panel is intended to be handled by CT106.

Certificate management is provided by Certbot using Cloudflare DNS-01.

The certificate hostname is:

    panel.robynshomelab.dev

Certbot and the Cloudflare ACME credential are located on CT106.

The Cloudflare API credential used for ACME is separate from the DDNS credential.

Secrets are not stored in GitHub.

The exact certificate deployment state should be verified on CT106 rather than assumed from the configuration alone.

## Security Model

The Pterodactyl Panel is intended to remain private.

Preferred access:

- LAN
- NetBird

There should be no direct router port forwarding to:

    192.168.20.111:80

or any other Panel management port.

The public DNS record does not by itself expose the Panel.

The Panel's administrative interface should not be directly exposed to the public Internet.

## Wings

Wings is the Pterodactyl daemon responsible for managing game-server workloads.

Wings is **not currently installed**.

The next major Pterodactyl deployment step is:

    Install Wings on VM108
        |
        v
    Register VM108 as a Pterodactyl node
        |
        v
    Connect Wings to the Panel
        |
        v
    Verify Docker integration
        |
        v
    Deploy first game server

Wings configuration should only be documented after it has actually been installed and registered.

## Game Servers

No game servers are currently deployed.

The primary planned workload is:

    Modded Minecraft

Additional game servers may be added later.

Game servers will run through Docker under Wings.

The final CPU, RAM, storage, port allocations, and container limits should be determined when the first server is deployed.

## Game Networking

Game-server networking is separate from Panel management traffic.

The intended future architecture is:

    Internet
      |
      v
    NetBird Reverse Proxy
      |
      | NetBird tunnel
      v
    VM108
      |
      v
    Wings
      |
      v
    Specific game server

The Panel remains private.

Game allocations will be exposed only through the networking architecture established for the individual game servers.

Direct router port forwarding is not part of the planned design unless explicitly introduced later.

## NetBird on VM108

VM108 is expected to become an independent NetBird peer when game-server networking is implemented.

This is separate from CT101.

Current:

    NetBird Client
        |
        v
    CT101
        |
        v
    CT106
        |
        v
    VM108 Panel

Future game-server networking:

    NetBird Reverse Proxy
        |
        v
    VM108 NetBird peer
        |
        v
    Wings
        |
        v
    Game server

The VM108 NetBird peer has not yet been configured.

## Game Allocations

Game-server allocations should be created only after Wings is operational.

Allocations will depend on the actual game servers deployed.

Only the ports required by the game servers should be exposed.

Both TCP and UDP may be required depending on the game.

The final allocation table should be added to this document once the first game server is deployed.

## Firewall

The VM firewall is currently disabled.

Firewall rules should not be finalised before Wings and the actual game-server allocations are known.

Once the Pterodactyl networking architecture is operational, firewalling should restrict access to:

- Panel management
- Wings API
- SFTP
- Game allocations
- Required internal services

The exact rules should be based on the final deployment rather than assumptions.

## SFTP

Pterodactyl uses SFTP for server file management.

The standard Pterodactyl SFTP port is planned to be:

    2022

This should remain accessible only from:

- LAN
- NetBird

The final configuration should be verified after Wings is installed.

## Storage

The current VM disk is:

    40 GB

This is sufficient for the Panel installation but should not be treated as the final storage architecture for game servers.

The future storage requirements will depend on:

- Game-server count
- World sizes
- Modpacks
- Backups
- Logs
- Docker images
- Temporary files

The future 4 TB HDD on `pve-2` is intended for general homelab bulk storage and media storage.

It is **not currently designated as Pterodactyl game-server storage**.

Any future Pterodactyl storage migration should be planned separately.

## Monitoring

Pterodactyl should eventually be integrated with the existing monitoring infrastructure.

Potential monitoring includes:

- VM108 availability
- CPU utilisation
- Memory utilisation
- Disk utilisation
- Docker health
- Wings availability
- Panel availability
- Game-server availability

Uptime Kuma can provide service availability monitoring.

Beszel can provide system/resource monitoring.

## Backups

Pterodactyl configuration and game-server data will require a dedicated backup strategy.

Future backups should account for:

- Panel configuration
- Panel database
- Wings configuration
- Game-server data
- Minecraft worlds
- Server configuration
- Modpacks
- Docker-related data where necessary

Backups should not rely solely on the same physical storage as the live workload.

The final backup strategy will be documented once game servers are deployed.

## Troubleshooting

### Panel does not load through the hostname

Check DNS:

    dig @192.168.20.99 panel.robynshomelab.dev

Expected internal result:

    192.168.20.94

Then check CT106 Nginx.

### CT106 cannot reach the Panel

From CT106:

    curl -I -H "Host: panel.robynshomelab.dev" http://192.168.20.111

A successful HTTP response indicates that CT106 can reach the VM and the local VM Nginx is responding.

### Panel works on VM108 but not through CT106

Check:

- VM108 local Nginx
- CT106 reverse-proxy configuration
- DNS
- TLS certificate
- Host header handling

### NetBird client cannot reach the Panel

Check:

1. NetBird connection.
2. CT101 route `192.168.20.94/32`.
3. Internal DNS resolution.
4. CT106 Nginx.
5. CT106 -> VM108 connectivity.

### Panel works but Wings does not

Once Wings is installed, check:

- Docker
- Wings service
- Node registration
- Panel/Wings authentication
- Firewall rules
- Required ports
- TLS configuration
- NetBird connectivity

## Deployment Plan

The remaining Pterodactyl deployment should proceed in this order:

1. Verify Panel HTTPS through CT106.
2. Install Wings on VM108.
3. Configure the Pterodactyl node.
4. Register VM108 with the Panel.
5. Connect and verify Wings.
6. Verify Docker integration.
7. Configure SFTP.
8. Install NetBird on VM108.
9. Verify VM108 NetBird connectivity.
10. Establish the game-server networking architecture.
11. Create the first game allocation.
12. Deploy the first game server.
13. Configure monitoring.
14. Configure backups.
15. Apply final firewall rules.
16. Document the final deployment.

## Current State

Current deployed components:

    VM108
      |
      +--> Debian 13
      +--> Docker
      +--> PHP / PHP-FPM
      +--> MariaDB
      +--> Redis
      +--> Composer
      +--> Nginx
      +--> Pterodactyl Panel

Current access architecture:

    LAN / NetBird
          |
          v
    CT106 Nginx
    192.168.20.94
          |
          v
    VM108
    192.168.20.111
          |
          v
    Pterodactyl Panel

Not yet deployed:

    Wings
    Pterodactyl game servers
    VM108 NetBird peer
    Game allocations
    Game-server reverse proxy
    Pterodactyl-specific firewall rules
    Pterodactyl backup system

The Panel is therefore operational, while the actual game-server infrastructure remains a future deployment.