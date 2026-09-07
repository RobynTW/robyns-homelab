# Pterodactyl Game Server

## Overview

Pterodactyl is planned as the game-server management platform for the homelab.

It will run separately from the main Proxmox 3060 infrastructure on the Dell OptiPlex 9020.

The Pterodactyl deployment is **not currently deployed**.

The planned architecture is:

```text id="p2w8rj"
                    Dell OptiPlex 9020
                           │
                       Proxmox
                           │
                           ▼
                  Debian 13 KVM VM
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
            Pterodactyl            Wings
               Panel                │
                 │                   ▼
                 └────────────► Docker
                                     │
                              ┌──────┴──────┐
                              ▼             ▼
                         Game Server 1  Game Server 2
```

NetBird will provide the private networking layer for remote access and game-server exposure.

## Hardware

The Pterodactyl host will be the Dell OptiPlex 9020 SFF.

The 9020 is also intended to provide NAS/storage services, with the game-server workload running separately inside its own virtual machine.

The planned host architecture is:

```text id="e3j7tq"
Dell OptiPlex 9020
│
├── Proxmox
│
├── NAS / Storage
│
└── Pterodactyl VM
```

Keeping Pterodactyl in its own VM provides isolation from the NAS operating system.

## Planned Virtual Machine

Pterodactyl will run inside a dedicated KVM virtual machine.

Planned configuration:

```text id="u8oym5"
Operating system: Debian 13 minimal
CPU: 4 vCPU
RAM: 8 GB
Disk: 32–64 GB
Network: VirtIO
```

The final resource allocation can be adjusted depending on the number and requirements of the game servers being hosted.

The VM will receive a static DHCP lease or another stable LAN address.

The exact IP address will be documented after deployment.

## Pterodactyl Components

The planned installation will contain both the Pterodactyl Panel and Wings.

```text id="xij6hj"
Pterodactyl Panel
       │
       ▼
     Wings
       │
       ▼
    Docker
       │
       ▼
Game Servers
```

### Pterodactyl Panel

The Panel provides the web interface for managing:

```text id="w3wpxv"
Game servers
Users
Nodes
Allocations
Server resources
Backups
Server configurations
```

The Panel is intended to remain private rather than being exposed directly to the public internet.

### Wings

Wings is the Pterodactyl node daemon responsible for actually running the game servers.

It communicates with the Panel and manages the Docker containers used by the individual game servers.

The planned relationship is:

```text id="w0vtdl"
Panel
  │
  │ API
  ▼
Wings
  │
  ▼
Docker
  │
  ├── Game server
  ├── Game server
  └── Game server
```

## Docker

Wings will use Docker to isolate individual game servers.

Each game server will run inside its own container.

This provides separation between:

```text id="c9w0av"
Game server processes
Game server files
Dependencies
Resource limits
Container networking
```

Docker will therefore be installed inside the dedicated Pterodactyl VM rather than directly on the Proxmox host.

## Network Architecture

The Pterodactyl VM will connect to the homelab LAN through the Proxmox bridge.

The planned architecture is:

```text id="8p6j6x"
                         Home Network
                              │
                              ▼
                         Proxmox 9020
                              │
                              ▼
                     Pterodactyl VM
                              │
                              ▼
                            Wings
                              │
                              ▼
                           Docker
                              │
                   ┌──────────┴──────────┐
                   ▼                     ▼
              Game Server 1         Game Server 2
```

The exact VM address will be added after deployment.

## NetBird Integration

NetBird will be used separately from the existing CT101 NetBird routing peer.

The Pterodactyl VM will have its own NetBird installation.

This is intentional.

The existing NetBird LXC:

```text id="1j4o3w"
CT101
192.168.20.97
```

is dedicated to private homelab access and should not be repurposed for Pterodactyl game-server exposure.

The future Pterodactyl VM will instead use NetBird for its own service exposure.

## Private Remote Access

NetBird can provide private access to the Pterodactyl Panel.

The intended model is:

```text id="e7e0mm"
Remote Device
      │
      │ NetBird
      ▼
Pterodactyl VM
      │
      ▼
Pterodactyl Panel
```

This avoids exposing the administration interface directly to the internet.

The Panel should therefore remain accessible only through trusted network paths.

## Game Server Access

Game servers will be exposed separately from the Pterodactyl Panel.

The intended architecture is:

```text id="wqgkwv"
Player
  │
  │ NetBird
  ▼
Pterodactyl VM
  │
  ▼
Wings
  │
  ▼
Game Server
```

This allows game-server traffic to be controlled independently from Panel administration.

Game servers are intended for a limited group of friends rather than general public access.

## No Router Port Forwarding

The Pterodactyl deployment should not require direct port forwarding from the ISP router.

The preferred architecture is:

```text id="l5x1lc"
Internet
   │
   │
   X  No direct router forwarding
   │
   ▼
NetBird
   │
   ▼
Pterodactyl VM
```

This reduces the number of directly exposed services and keeps the game-server infrastructure under the homelab's existing private-access model.

## NetBird Reverse Proxy

The future Pterodactyl setup is intended to use NetBird's reverse-proxy capabilities where appropriate.

This can provide controlled access to services without exposing the homelab through traditional router port forwarding.

The exact NetBird reverse-proxy configuration will be determined during deployment.

The architecture should remain:

```text id="c2gd4k"
Trusted Player
      │
      ▼
    NetBird
      │
      ▼
Pterodactyl VM
      │
      ▼
 Game Service
```

## Game Allocations

Pterodactyl uses allocations to associate network addresses and ports with game servers.

The exact ports depend on the game being hosted.

For example:

```text id="j5k6xq"
Pterodactyl
│
├── Game Server A
│   └── Allocation: <game-specific port>
│
└── Game Server B
    └── Allocation: <game-specific port>
```

Ports should be allocated explicitly rather than opening broad port ranges unnecessarily.

The actual allocations will be documented when game servers are created.

## Pterodactyl Ports

The standard Pterodactyl components commonly use:

```text id="x3tr50"
Panel:
HTTP  → 80
HTTPS → 443

Wings:
HTTP/API → 8080
HTTPS    → 8443

SFTP:
2022
```

Game-server ports are separate and depend on the individual game.

These ports describe the planned internal service architecture and should not be interpreted as router port-forwarding requirements.

The final configuration should be verified against the Pterodactyl/Wings versions installed during deployment.

## Panel Access

The Panel will be treated as an administrative interface.

It should not be directly exposed to the public internet.

Possible future access paths include:

```text id="a1qghw"
NetBird
Internal LAN
```

A dedicated hostname may be created later if required.

For example:

```text id="9txg3k"
panel.robynshomelab.dev
```

This hostname is only a potential future configuration and is not currently configured.

## DNS

If a hostname is required for the Panel, Pi-hole can provide an internal DNS record pointing to the Pterodactyl VM.

The exact record will be determined after deployment.

The public Cloudflare DNS zone should not contain private LAN addresses such as:

```text id="l2v1ns"
192.168.20.x
```

Internal service names should therefore resolve through Pi-hole where appropriate.

## Storage

Pterodactyl requires storage for:

```text id="v82xkq"
Docker images
Game-server files
Configuration
Logs
Backups
```

The Pterodactyl VM will have its own virtual disk.

The initial planned disk allocation is:

```text id="w2o2ax"
32–64 GB
```

The final storage requirement depends heavily on the games hosted.

Large game-server datasets should not automatically be placed on the NAS.

Storage requirements will be assessed after the first game servers are deployed.

## NAS Relationship

The 9020 will also provide NAS services.

The Pterodactyl VM should remain logically separated from the NAS operating system.

The intended architecture is:

```text id="5r6ez5"
9020
│
├── NAS / Storage
│
└── Pterodactyl VM
      │
      └── Docker
            └── Game Servers
```

If shared storage is required later, it should be deliberately designed rather than mounting the entire NAS filesystem into the VM.

## Resource Management

The initial VM allocation is:

```text id="qv8a2x"
4 vCPU
8 GB RAM
```

Individual game servers will then receive their own Pterodactyl resource limits.

This allows the total host workload to remain controlled.

For example:

```text id="u5f1wt"
Pterodactyl VM
│
├── Game A
│   ├── CPU limit
│   └── Memory limit
│
├── Game B
│   ├── CPU limit
│   └── Memory limit
│
└── Game C
    ├── CPU limit
    └── Memory limit
```

Actual limits should be based on the requirements of each game.

## Backups

Pterodactyl configuration and game-server data should be considered separately.

Important backup targets include:

```text id="2d4j4y"
Pterodactyl Panel configuration
Wings configuration
Game-server configuration
Important game worlds/saves
Docker/Pterodactyl metadata
```

Not every game-server file necessarily needs to be backed up.

The backup strategy should prioritise irreplaceable configuration and saved game data.

## Monitoring

The Pterodactyl VM should eventually be monitored by the existing monitoring infrastructure.

Uptime Kuma can provide service availability monitoring.

Beszel can monitor the VM's:

```text id="n8n0bj"
CPU
Memory
Disk
Network
Temperature where available
```

Potential Uptime Kuma monitors include:

```text id="1shm2h"
Pterodactyl Panel
Wings
Individual game services
```

These monitors should be added after the Pterodactyl VM is deployed.

## Security

The Pterodactyl environment should follow the principle of exposing only what is required.

The preferred model is:

```text id="3k14qv"
Panel
└── Private access only

Wings
└── Required Panel communication

Game Servers
└── NetBird/private access for intended players
```

Administrative access should not be shared with game-server users unless explicitly required.

Game servers should also be isolated from the rest of the homelab as much as practical.

## Future Firewall/VLAN Integration

The current network uses the ISP router and a flat LAN.

A future managed-switch/pfSense design is planned:

```text id="2s9j4c"
Internet
  │
  ▼
pfSense
  │
  ▼
Managed Switch
  │
  ├── VLAN 10 Trusted
  ├── VLAN 20 Servers
  ├── VLAN 30 IoT
  ├── VLAN 40 Guest
  └── VLAN 50 Management
```

The Pterodactyl VM would ultimately belong to the appropriate server/DMZ-style network depending on the final firewall design.

This is a future improvement and is not part of the current deployment.

## Deployment Order

Pterodactyl should be deployed after the basic 9020 infrastructure is operational.

Recommended order:

```text id="x4x0vl"
1. Install Proxmox on the 9020
        │
        ▼
2. Configure NAS/storage
        │
        ▼
3. Verify 9020 networking
        │
        ▼
4. Create Debian 13 KVM VM
        │
        ▼
5. Configure VM networking
        │
        ▼
6. Install Docker
        │
        ▼
7. Install Pterodactyl Panel
        │
        ▼
8. Install Wings
        │
        ▼
9. Connect Panel and Wings
        │
        ▼
10. Configure NetBird
        │
        ▼
11. Configure private access
        │
        ▼
12. Create first game server
        │
        ▼
13. Configure resource limits
        │
        ▼
14. Configure backups
        │
        ▼
15. Add Uptime Kuma/Beszel monitoring
```

This order allows each layer to be tested before adding the next.

## Current Status

Pterodactyl is currently:

```text id="c0t8f4"
Status: Planned
Host: Dell OptiPlex 9020
VM: Not yet created
Panel: Not deployed
Wings: Not deployed
Docker: Not deployed
NetBird: Not deployed on Pterodactyl VM
Game servers: None
```

The existing CT101 NetBird routing peer remains dedicated to private homelab access.

The future Pterodactyl VM will use its own NetBird installation for game-server-related access.

## Key Commands

No Pterodactyl deployment commands are currently recorded because the VM has not yet been created.

Useful future checks will include:

```bash
# Check Docker
docker version

# List running Docker containers
docker ps

# Check Docker service
systemctl status docker

# Check listening ports
ss -tulpn

# Check Wings service
systemctl status wings

# Check Wings logs
journalctl -u wings

# Check NetBird
netbird status
```

The actual commands used during deployment should be added to this document as the system is built.

## Related Documentation

The Pterodactyl deployment depends on:

```text id="9ndzpj"
01-hardware.md
02-network.md
03-proxmox.md
08-netbird.md
10-beszel.md
11-uptime-kuma.md
```

The NAS/storage documentation will also become relevant once the Dell OptiPlex 9020 is deployed.
