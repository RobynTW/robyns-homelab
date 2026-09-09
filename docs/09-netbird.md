# NetBird

## Overview

NetBird provides the homelab's private overlay network and remote access.

The primary NetBird routing peer is CT101.

Hostname:

    netbird

IP address:

    192.168.20.97

VMID:

    CT101

NetBird version:

    0.78.1

NetBird provides remote clients with access to selected homelab services without requiring router port forwarding.

## Network

NetBird assigns peers addresses from the NetBird network.

CT101 currently has:

    IPv4: 100.113.51.59/16
    IPv6: fda0:124:5d3a:d4ae:ed2e:853c:913a:4d70/64

NetBird FQDN:

    netbird.netbird.cloud

WireGuard port:

    51820

The NetBird interface uses the kernel WireGuard implementation.

## Routing Peer

CT101 acts as the routing peer between NetBird and selected services on the LAN.

Current routes:

    192.168.20.94/32
    192.168.20.99/32

These provide access to:

    192.168.20.94
        CT106 Nginx

    192.168.20.99
        CT100 Pi-hole

Only the required addresses are routed through CT101.

## Current Routing Architecture

The current architecture is:

    NetBird Client
          |
          v
    NetBird Overlay
          |
          v
    CT101
    192.168.20.97
          |
          +----------------------+
          |                      |
          v                      v
    CT106                  CT100
    192.168.20.94           192.168.20.99
    Nginx                    Pi-hole
          |                      |
          |                      v
          |                   Unbound
          |
          +--> Internal services
          |
          +--> VM108 Panel

## DNS

NetBird clients use Pi-hole for DNS.

DNS server:

    192.168.20.99:53

The NetBird global/default nameserver is configured as:

    192.168.20.99:53

for:

    [.]

This means general DNS queries from NetBird clients are sent through Pi-hole.

The DNS path is:

    NetBird Client
          |
          v
    Pi-hole
    192.168.20.99:53
          |
          +--> Local DNS records
          |
          +--> Filtering
          |
          v
    Unbound
    127.0.0.1:5335

## Internal Hostnames

Pi-hole provides internal DNS overrides for homelab services.

Current internal service names resolve to CT106:

    jellyfin.robynshomelab.dev -> 192.168.20.94
    status.robynshomelab.dev  -> 192.168.20.94
    beszel.robynshomelab.dev  -> 192.168.20.94
    pihole.robynshomelab.dev  -> 192.168.20.94
    panel.robynshomelab.dev   -> 192.168.20.94

This allows NetBird clients to use the same service hostnames as LAN clients.

## Pterodactyl Panel

The Pterodactyl Panel is hosted on VM108:

    192.168.20.111

The current NetBird access path is:

    NetBird Client
          |
          v
    CT101
    192.168.20.97
          |
          | 192.168.20.94/32
          v
    CT106 Nginx
    192.168.20.94
          |
          | HTTP
          v
    VM108
    192.168.20.111
          |
          v
    Pterodactyl Panel

No direct NetBird route to `192.168.20.111` is currently required for Panel access.

The route to CT106 provides the necessary path.

The Panel remains private and is not intended to be directly exposed to the public Internet.

## Pi-hole Access

NetBird clients can also reach Pi-hole directly through the routed address:

    192.168.20.99

This is required for the NetBird DNS configuration.

The Pi-hole web interface is normally accessed through:

    pihole.robynshomelab.dev

which resolves internally to CT106.

## iPhone Example

An iPhone has previously been observed as a NetBird peer with the address:

    100.113.124.99

Another observed peer address was:

    100.113.48.198

Peer addresses may change and should not be treated as permanent identifiers.

## DNS Verification

DNS traffic from NetBird clients to Pi-hole has been verified previously.

The expected path is:

    NetBird Client
          |
          v
    192.168.20.99:53

Pi-hole should then process the query normally.

A blocked DNS request may return:

    0.0.0.0

or:

    ::

This is expected Pi-hole filtering behaviour and does not necessarily indicate a NetBird or DNS failure.

## Service Access

From a NetBird client, internal services should be reachable using their normal hostnames.

For example:

    https://panel.robynshomelab.dev

The expected flow is:

    NetBird Client
          |
          v
    NetBird
          |
          v
    CT101
          |
          v
    CT106
          |
          v
    VM108

Other reverse-proxied services follow the same general pattern.

## System Service

NetBird runs as a systemd service on CT101.

Check its status with:

    systemctl status netbird

The service is enabled so that it starts automatically with the container.

## Verification

### Check NetBird status

On CT101:

    netbird status

### Check systemd

    systemctl status netbird

### Check NetBird IP

    ip addr

The NetBird interface should have the assigned overlay address.

### Check routes

On CT101:

    ip route

Verify that the required LAN routes are present.

### Test Pi-hole

From a NetBird client:

    ping 192.168.20.99

Then test DNS:

    nslookup example.com 192.168.20.99

### Test Nginx

From a NetBird client:

    ping 192.168.20.94

Then test the reverse proxy:

    curl -I https://panel.robynshomelab.dev

### Test Panel backend path

The expected path is:

    NetBird Client
        ->
    CT101
        ->
    192.168.20.94
        ->
    VM108 192.168.20.111

The Panel does not require a direct NetBird route to VM108 at this stage.

## Troubleshooting

### NetBird is disconnected

On CT101:

    systemctl status netbird

Then:

    netbird status

Check the service logs if required:

    journalctl -u netbird

### Pi-hole cannot be reached

Test:

    ping 192.168.20.99

Then:

    dig @192.168.20.99 example.com

If the address is unreachable, investigate the CT101 route before troubleshooting DNS itself.

### Internal hostnames do not resolve

Test:

    dig @192.168.20.99 panel.robynshomelab.dev

Expected result:

    192.168.20.94

If this works but HTTPS does not, investigate CT106 rather than Pi-hole.

### Panel hostname resolves but Panel is unreachable

Check the path in order:

1. NetBird connection.
2. CT101 routing.
3. CT106 reachability.
4. CT106 Nginx.
5. VM108 reachability.
6. VM108 local Nginx.
7. Pterodactyl Panel.

## Security

NetBird is used to avoid exposing internal management services directly to the Internet.

The current architecture does not require router port forwarding for:

- Pi-hole
- Nginx
- Pterodactyl Panel
- Proxmox management
- Other internal management services

Access should be granted through the LAN or NetBird as appropriate.

NetBird credentials and private configuration data must not be committed to GitHub.

## Future VM108 Peer

VM108 will eventually run NetBird directly.

This is intentionally separate from CT101.

The future architecture is:

    VM108
      |
      +--> NetBird Peer
      |
      +--> Wings
            |
            +--> Docker
                  |
                  +--> Game Servers

The VM108 NetBird peer will be used primarily for game-server networking.

It will not replace CT101 as the existing LAN routing peer.

## Future Game-Server Networking

The planned game-server architecture is:

    Internet
       |
       v
    NetBird Reverse Proxy
       |
       v
    NetBird Tunnel
       |
       v
    VM108
       |
       v
    Wings
       |
       v
    Specific Game Server

Game-server networking will be configured after Wings and the first game server are deployed.

Only the required game allocations should be exposed.

The Pterodactyl Panel should remain separate from the public game-server access path.

## Session Persistence

NetBird is configured as a systemd service and has been verified to persist across normal service restarts and container operation.

Long-term authentication-session persistence should not be assumed beyond the configured NetBird authentication/session behaviour without verification.

If authentication expires, re-authentication may be required.

## Current State

CT101 is the active NetBird routing peer.

Current routed addresses:

    192.168.20.94/32
    192.168.20.99/32

Current DNS server:

    192.168.20.99:53

Current Panel access:

    NetBird Client
        |
        v
    CT101
        |
        v
    CT106 Nginx
        |
        v
    VM108 Pterodactyl Panel

Future game-server networking will use a dedicated NetBird peer on VM108.