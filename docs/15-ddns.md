# Dynamic DNS

## Overview

Dynamic DNS (DDNS) keeps the homelab's public DNS record updated when the residential WAN IP address changes.

The DDNS client runs on CT100 alongside Pi-hole and Unbound.

## Host

Container:

    CT100

Hostname:

    pihole

IP address:

    192.168.20.99

DDNS client:

    ddclient

Version:

    3.10.0

## Domain

Domain:

    robynshomelab.dev

Registrar:

    Porkbun

Authoritative DNS provider:

    Cloudflare

DDNS hostname:

    home.robynshomelab.dev

The hostname points to the current residential WAN IP address.

## Architecture

The DDNS update path is:

    Residential WAN
          |
          v
    Current public IP
          |
          v
    Cloudflare DNS
          |
          v
    home.robynshomelab.dev

CT100 periodically checks the current public IP and updates the Cloudflare DNS record when required.

    CT100
    192.168.20.99
          |
          v
       ddclient
          |
          v
      Cloudflare API
          |
          v
    home.robynshomelab.dev

## Cloudflare Record

The DDNS-managed record is:

    home.robynshomelab.dev

It resolves to the residential WAN IP.

The record is DNS-only.

Cloudflare proxying is not used for this record.

## Update Interval

ddclient checks for changes every:

    5 minutes

This provides reasonably fast recovery from a residential IP change without unnecessarily frequent API requests.

## Credentials

The Cloudflare API credential used by ddclient is stored locally on CT100.

Configuration location:

    /etc/ddclient.conf

The credential is restricted to the local system and must not be committed to GitHub.

The DDNS credential is separate from the Cloudflare API credential used by Certbot for ACME DNS-01 validation.

No Cloudflare secrets should ever be stored in the repository.

## Interaction With Other Services

DDNS maintains the public hostname:

    home.robynshomelab.dev

It is separate from the internal split-DNS records used by homelab services.

For example, internal services resolve through Pi-hole to the Nginx reverse proxy:

    jellyfin.robynshomelab.dev -> 192.168.20.94
    status.robynshomelab.dev -> 192.168.20.94
    beszel.robynshomelab.dev -> 192.168.20.94
    pihole.robynshomelab.dev -> 192.168.20.94
    panel.robynshomelab.dev -> 192.168.20.94

These records are separate from the public DDNS record.

## Relationship With Cloudflare

Cloudflare provides:

- Authoritative DNS
- DDNS API access
- ACME DNS-01 validation

Cloudflare is not being used as a reverse proxy for the homelab.

The homelab therefore remains responsible for handling inbound traffic where router port forwarding is configured.

Currently, no router port forwarding is configured for the homelab's web services.

## Verification

Check the ddclient service:

    systemctl status ddclient

Check whether it is enabled:

    systemctl is-enabled ddclient

Inspect recent logs:

    journalctl -u ddclient

Check the configured hostname:

    grep -vE 'password|token|secret' /etc/ddclient.conf

Do not print or share the unredacted configuration if it contains credentials.

## DNS Verification

From an external network, query:

    home.robynshomelab.dev

The result should match the current residential WAN IP.

From an internal client, DNS behaviour may differ depending on Pi-hole configuration and should not be assumed to represent the public Cloudflare response.

Cloudflare should be treated as the source of truth for the public record.

## Troubleshooting

### The WAN IP changed but DNS did not

Check ddclient:

    systemctl status ddclient

Then inspect logs:

    journalctl -u ddclient

Verify that:

- ddclient is running
- the Cloudflare credential is valid
- the credential has permission to modify the DNS zone
- the correct zone is configured
- the correct hostname is configured
- CT100 has Internet connectivity

### ddclient is not running

Check:

    systemctl status ddclient

If necessary, restart it:

    systemctl restart ddclient

Then verify the service:

    systemctl status ddclient

### Cloudflare authentication fails

Do not replace credentials blindly.

Verify that the configured Cloudflare API token:

- belongs to the DDNS configuration
- has permission to modify the required DNS record
- applies to the `robynshomelab.dev` zone
- has not expired or been revoked

The credential should remain separate from the Certbot ACME credential.

### DNS resolves to an old address

First determine whether the issue is local caching or the Cloudflare record itself.

Check the authoritative DNS result from an external system.

If Cloudflare still contains the old WAN IP, investigate ddclient.

If Cloudflare contains the new IP, investigate DNS caching or resolver behaviour.

## Security

The DDNS API credential should have the minimum permissions required to update the necessary DNS record.

The credential should:

- remain on CT100
- be readable only by authorised local users/services
- never be committed to Git
- never be included in documentation
- remain separate from the ACME credential

The `.gitignore` configuration should prevent accidental inclusion of local secret files where appropriate.

## Current State

Current DDNS deployment:

    CT100
    192.168.20.99
        |
        +--> ddclient 3.10.0
        |
        +--> Cloudflare API
        |
        v
    home.robynshomelab.dev

Update interval:

    5 minutes

Cloudflare remains the authoritative DNS provider.

The DDNS system is independent of the internal Pi-hole split-DNS configuration and the CT106 Nginx reverse proxy.