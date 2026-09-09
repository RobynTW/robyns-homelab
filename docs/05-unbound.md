# Unbound

## Overview

Unbound provides recursive DNS resolution for the homelab.

It runs locally on CT100 alongside Pi-hole.

Hostname:

    pihole

IP address:

    192.168.20.99

Unbound listens only on the local loopback interface.

    127.0.0.1:5335

## DNS Architecture

The current DNS path is:

    LAN / NetBird Client
            |
            | DNS
            v
    Pi-hole
    192.168.20.99:53
            |
            | forwarded DNS
            v
    Unbound
    127.0.0.1:5335
            |
            v
    Authoritative DNS infrastructure
            |
            v
    Internet

Pi-hole remains the client-facing DNS service.

Unbound is not directly exposed to the LAN or NetBird network.

## Role of Pi-hole

Pi-hole provides:

- DNS filtering
- Local DNS records
- DNS access for LAN clients
- DNS access for NetBird clients

When a query is not answered by a local Pi-hole DNS record or blocked by filtering, Pi-hole forwards the query to Unbound.

For example:

    Client
      |
      | example.com
      v
    Pi-hole
      |
      | 127.0.0.1:5335
      v
    Unbound
      |
      v
    Internet DNS infrastructure

## Listening Address

Unbound is intentionally bound to:

    127.0.0.1:5335

This prevents external clients from querying Unbound directly.

Clients should use:

    192.168.20.99:53

rather than:

    192.168.20.99:5335

Pi-hole is responsible for forwarding appropriate queries to Unbound.

## Local DNS Overrides

Local homelab service names are handled by Pi-hole rather than Unbound.

Current internal service names include:

    jellyfin.robynshomelab.dev
    status.robynshomelab.dev
    beszel.robynshomelab.dev
    pihole.robynshomelab.dev
    panel.robynshomelab.dev

These resolve internally through Pi-hole to CT106:

    192.168.20.94

Unbound is therefore primarily responsible for recursive external DNS resolution.

## NetBird

NetBird clients use Pi-hole as their DNS server.

    NetBird Client
          |
          v
    192.168.20.99:53
          |
          v
    Pi-hole
          |
          v
    127.0.0.1:5335
          |
          v
    Unbound

This means NetBird clients receive the same Pi-hole filtering and internal DNS behaviour as LAN clients.

## Security

Unbound should remain locally accessible only.

The intended exposure is:

    127.0.0.1:5335

It should not be exposed through:

- The router
- Nginx
- NetBird routes
- Public DNS
- WAN port forwarding

The Pi-hole DNS service is the controlled entry point for DNS clients.

## Verification

### Check Unbound service

On CT100:

    systemctl status unbound

### Check listening sockets

On CT100:

    ss -lntup | grep 5335

The expected listener is on:

    127.0.0.1:5335

### Query Unbound directly

From CT100:

    dig @127.0.0.1 -p 5335 example.com

A successful response confirms that Unbound can perform recursive DNS resolution.

### Query Pi-hole

From CT100 or another LAN client:

    dig @192.168.20.99 example.com

This tests the client-facing DNS path.

### Test internal DNS

For example:

    dig @192.168.20.99 panel.robynshomelab.dev

The expected internal result is:

    192.168.20.94

This query should be answered by Pi-hole's local DNS configuration rather than requiring recursive resolution through Unbound.

## Troubleshooting

If external DNS resolution fails:

1. Check Pi-hole.
2. Check Unbound.
3. Confirm Unbound is listening on `127.0.0.1:5335`.
4. Test Unbound directly with `dig`.
5. Test Pi-hole separately.
6. Check Pi-hole query logs.

Useful commands:

    systemctl status pihole-FTL

    systemctl status unbound

    ss -lntup | grep 5335

    dig @127.0.0.1 -p 5335 example.com

    dig @192.168.20.99 example.com

If internal hostnames fail but external DNS works, check Pi-hole's local DNS records rather than Unbound first.

## Current State

Unbound is deployed and operational on CT100.

Current configuration:

    CT100
    192.168.20.99
        |
        +--> Pi-hole :53
        |
        +--> Unbound 127.0.0.1:5335
        |
        +--> ddclient

Unbound is not intended to be directly accessible by clients.

Pi-hole remains the authoritative client-facing DNS service for the homelab.