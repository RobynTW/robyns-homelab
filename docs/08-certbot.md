# Certbot

## Overview

Certbot manages the Let's Encrypt TLS certificates used by the homelab's Nginx reverse proxy.

Certbot runs on CT106 alongside Nginx.

Hostname:

    nginx

IP address:

    192.168.20.94

VMID:

    CT106

## Role

Certbot is responsible for:

- Obtaining Let's Encrypt certificates
- Renewing certificates
- Performing DNS-01 validation through Cloudflare
- Providing certificates for Nginx

Nginx uses the resulting certificates to provide HTTPS access to internal services.

## Architecture

The current certificate architecture is:

    CT106
    192.168.20.94
        |
        +--> Nginx
        |
        +--> Certbot
              |
              | Cloudflare API
              v
          Cloudflare DNS
              |
              | DNS-01 TXT record
              v
          Let's Encrypt

Cloudflare is used for DNS validation only.

It is not used as an HTTP/HTTPS reverse proxy.

## DNS-01

Certificates are validated using the DNS-01 challenge.

The process is:

    Certbot
       |
       | Request certificate
       v
    Let's Encrypt
       |
       | DNS-01 challenge
       v
    Cloudflare DNS
       |
       | TXT record
       v
    Let's Encrypt
       |
       | Validation successful
       v
    Certificate issued
       |
       v
    CT106
       |
       v
    Nginx

DNS-01 is useful for this homelab because certificate validation does not require the internal services themselves to be publicly accessible.

## Cloudflare Credential

Certbot uses a dedicated Cloudflare API credential for DNS-01 authentication.

The credential is stored locally on CT106 at:

    /root/.secrets/certbot/cloudflare.ini

The file is root-owned and restricted to mode `600`.

The actual API token is intentionally not documented.

The ACME credential is separate from the Cloudflare credential used by ddclient.

## Certificate Domains

Current certificates managed by CT106 include:

    jellyfin.robynshomelab.dev
    status.robynshomelab.dev
    beszel.robynshomelab.dev
    pihole.robynshomelab.dev

The Pterodactyl Panel uses:

    panel.robynshomelab.dev

The Panel certificate is managed through the same Cloudflare DNS-01 architecture.

## Pterodactyl Panel

The Panel is hosted on VM108:

    192.168.20.111

The client-facing hostname is:

    panel.robynshomelab.dev

The certificate is terminated by Nginx on CT106.

The traffic path is:

    Client
      |
      | HTTPS
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

The Panel does not need its own public-facing TLS service.

## Certificate Storage

Let's Encrypt certificates and keys are stored on CT106 under the standard Certbot directories.

Typical locations include:

    /etc/letsencrypt/live/
    /etc/letsencrypt/archive/
    /etc/letsencrypt/renewal/

Private keys in these directories must never be committed to GitHub.

## Renewal

Certbot uses its systemd timer for automated renewal.

Check the timer with:

    systemctl status certbot.timer

List certificates with:

    certbot certificates

Certbot normally attempts renewal when certificates are sufficiently close to expiry.

Successful renewal updates the certificate files used by Nginx.

## Renewal Testing

A dry-run can be used to verify that the renewal process works without requesting a real certificate.

On CT106:

    certbot renew --dry-run

A successful dry-run indicates that the renewal configuration and ACME authentication are functioning correctly.

A dry-run should be preferred when testing changes to the renewal configuration.

## Nginx Integration

After certificates are issued, Nginx references the certificate files under:

    /etc/letsencrypt/live/

Nginx provides the client-facing HTTPS connection.

When certificate files are renewed, Nginx may need to reload so that the running process uses the updated certificate.

A configuration test should be performed before reloading:

    nginx -t

If successful:

    systemctl reload nginx

## Verification

### Check Certbot

On CT106:

    certbot --version

### List certificates

    certbot certificates

### Check renewal timer

    systemctl status certbot.timer

### Test renewal

    certbot renew --dry-run

### Check Nginx configuration

    nginx -t

### Check HTTPS

From an internal client:

    curl -I https://panel.robynshomelab.dev

The connection should use the certificate issued for the Panel hostname.

## Troubleshooting

### Certificate issuance fails

Check:

1. Cloudflare DNS configuration.
2. Cloudflare API credential permissions.
3. Credential file permissions.
4. DNS propagation.
5. Certbot logs.
6. Domain spelling.
7. Nginx configuration.

Check the credential file permissions:

    stat /root/.secrets/certbot/cloudflare.ini

The file should be accessible only by root.

### DNS-01 challenge fails

Verify that the Cloudflare API credential used by Certbot is valid and has the required permissions.

Do not replace the ACME credential with the ddclient credential unless the architecture is deliberately changed.

### Nginx does not use a renewed certificate

First verify that the certificate itself has renewed:

    certbot certificates

Then test Nginx:

    nginx -t

If the configuration is valid, reload Nginx:

    systemctl reload nginx

### HTTPS hostname does not resolve internally

Check Pi-hole:

    dig @192.168.20.99 panel.robynshomelab.dev

The expected internal result is:

    192.168.20.94

This is a DNS issue rather than a Certbot issue.

## Security

The following must never be committed to GitHub:

- Cloudflare API tokens
- Let's Encrypt private keys
- Certificate files
- Certbot credentials
- Nginx private keys
- Passwords
- Other authentication secrets

Only document credential locations and their purpose.

## Historical Architecture

Certbot was previously associated with CT100 when Nginx was hosted there.

That architecture is no longer current.

Current architecture:

    CT100
      |
      +--> Pi-hole
      +--> Unbound
      +--> ddclient

    CT106
      |
      +--> Nginx
      +--> Certbot

Certbot configuration and certificate management should remain on CT106 unless the reverse-proxy architecture is deliberately changed.

## Current State

Certbot is deployed on CT106.

Current certificate architecture:

    Client
       |
       | HTTPS
       v
    CT106 Nginx
       |
       | certificate
       v
    Let's Encrypt certificate
       ^
       |
    Certbot
       |
       | DNS-01
       v
    Cloudflare

Cloudflare provides DNS validation while CT106 remains responsible for TLS termination.

The Pterodactyl Panel uses the same architecture as the other reverse-proxied services.