# Certbot & Let's Encrypt

## Overview

Certbot manages the TLS certificates used by the homelab's Nginx reverse proxy.

Certbot now runs exclusively on **CT106 (`nginx`)**. It previously ran on the Pi-hole container but was removed after the reverse-proxy migration.

```text
Proxmox pve-1
└── CT106 nginx
    ├── Nginx
    └── Certbot
        └── Let's Encrypt certificates
```

Certificates are issued by Let's Encrypt using the **Cloudflare DNS-01 challenge**.

This allows certificates to be issued without exposing the homelab services directly to the public internet.

## Domain and DNS

The homelab uses:

```text
robynshomelab.dev
```

The domain registrar is Porkbun, while authoritative DNS is provided by Cloudflare.

Cloudflare nameservers:

```text
coby.ns.cloudflare.com
jamie.ns.cloudflare.com
```

The Cloudflare zone is intentionally kept free of internal RFC1918 addresses.

For example, addresses such as:

```text
192.168.20.94
192.168.20.95
192.168.20.96
192.168.20.98
192.168.20.99
```

are **not published publicly in Cloudflare DNS**.

Internal clients resolve service hostnames through Pi-hole instead.

## Current Certificates

Four individual certificates are currently managed:

| Certificate                  | Service     |
| ---------------------------- | ----------- |
| `jellyfin.robynshomelab.dev` | Jellyfin    |
| `status.robynshomelab.dev`   | Uptime Kuma |
| `beszel.robynshomelab.dev`   | Beszel      |
| `pihole.robynshomelab.dev`   | Pi-hole     |

The certificates currently expire on:

```text
2026-12-04
```

Certbot's automatic renewal process is enabled.

## Why DNS-01?

The DNS-01 challenge proves control of the domain by creating a temporary TXT record in Cloudflare DNS.

The process is approximately:

```text
Certbot
   │
   │ API request
   ▼
Cloudflare DNS
   │
   │ temporary _acme-challenge TXT record
   ▼
Let's Encrypt
   │
   │ validates domain ownership
   ▼
Certificate issued
```

This avoids requiring HTTP port 80 to be reachable from the public internet for certificate validation.

It also allows certificates to be issued for services that remain entirely internal.

## Cloudflare API Token

Certbot uses a dedicated Cloudflare API token.

The token is restricted to:

```text
Zone: robynshomelab.dev
Permission: DNS → Edit
```

The token is stored on CT106 at:

```text
/root/.secrets/certbot/cloudflare.ini
```

The file must be owned by root and readable only by root.

Expected permissions:

```text
-rw------- 1 root root
```

Check them with:

```bash
ls -l /root/.secrets/certbot/cloudflare.ini
```

The actual token must **never** be committed to Git or included in documentation.

The credential file is excluded by the repository's `.gitignore`.

## Cloudflare Credentials File

The credentials file has the following general structure:

```ini
dns_cloudflare_api_token = <token>
```

The actual token is intentionally omitted from this documentation.

## Certbot Installation

Certbot and the Cloudflare DNS plugin are installed on CT106.

The relevant packages provide:

```text
certbot
python3-certbot-dns-cloudflare
```

Check the installed version:

```bash
certbot --version
```

Check installed Certbot packages:

```bash
dpkg -l | grep certbot
```

## Certificate Storage

Certbot stores its configuration and certificates under:

```text
/etc/letsencrypt/
```

Important directories include:

```text
/etc/letsencrypt/live/
/etc/letsencrypt/archive/
/etc/letsencrypt/renewal/
```

The `live/` directory contains the certificate paths used by Nginx.

For example:

```text
/etc/letsencrypt/live/jellyfin.robynshomelab.dev/fullchain.pem
/etc/letsencrypt/live/jellyfin.robynshomelab.dev/privkey.pem
```

The actual certificate files are maintained by Certbot, with the `live/` paths normally pointing to the current certificate version.

## Nginx Integration

Nginx references the certificates directly from Certbot's `live/` paths.

Example:

```nginx
ssl_certificate /etc/letsencrypt/live/jellyfin.robynshomelab.dev/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/jellyfin.robynshomelab.dev/privkey.pem;
```

The same arrangement is used for the other three services.

After a successful certificate renewal, Nginx may need to reload to begin using the newly issued certificate.

## Individual Certificates

The homelab intentionally uses separate certificates for each service rather than relying on one large multi-domain certificate.

Current certificates:

```text
jellyfin.robynshomelab.dev
status.robynshomelab.dev
beszel.robynshomelab.dev
pihole.robynshomelab.dev
```

Individual certificates make the configuration easier to reason about and allow services to be renewed independently.

A previous attempt to issue a multi-domain certificate encountered DNS propagation problems, so the configuration was changed to individual certificates.

## DNS Propagation

The Cloudflare DNS plugin is configured to wait for propagation before allowing Let's Encrypt validation to continue.

The renewal configuration uses:

```ini
dns_cloudflare_propagation_seconds = 30
```

This is present for all certificates.

Jellyfin originally used a shorter propagation interval, but it was increased to 30 seconds after the initial configuration.

For example, the Jellyfin renewal configuration contains:

```ini
dns_cloudflare_credentials = /root/.secrets/certbot/cloudflare.ini
dns_cloudflare_propagation_seconds = 30
```

Do not reduce the propagation delay unless there is a specific reason to do so.

## Renewal

Certbot's systemd timer is enabled and active.

Check it with:

```bash
systemctl status certbot.timer
```

Check whether it is enabled:

```bash
systemctl is-enabled certbot.timer
```

The timer runs Certbot periodically and allows certificates to be renewed automatically when they approach expiration.

List the timer schedule:

```bash
systemctl list-timers certbot.timer
```

## Renewal Configuration

Individual renewal configurations are stored under:

```text
/etc/letsencrypt/renewal/
```

Current configurations include:

```text
/etc/letsencrypt/renewal/
├── jellyfin.robynshomelab.dev.conf
├── status.robynshomelab.dev.conf
├── beszel.robynshomelab.dev.conf
└── pihole.robynshomelab.dev.conf
```

Check a renewal configuration:

```bash
cat /etc/letsencrypt/renewal/jellyfin.robynshomelab.dev.conf
```

Do not copy the Cloudflare API token into Git documentation.

The renewal configuration should reference the credentials file path rather than containing the credential itself.

## Testing Renewal

A renewal dry-run was successfully completed for all four certificates.

Run:

```bash
certbot renew --dry-run
```

A successful dry-run confirms that Certbot can:

1. Access the Cloudflare credentials.
2. Authenticate with Cloudflare.
3. Create the required DNS challenge.
4. Complete the Let's Encrypt validation.
5. Renew the certificates successfully.

The dry-run does not replace the active certificates.

## Checking Certificates

List certificates managed by Certbot:

```bash
certbot certificates
```

Inspect a specific certificate:

```bash
openssl x509 \
    -in /etc/letsencrypt/live/jellyfin.robynshomelab.dev/cert.pem \
    -noout \
    -subject \
    -issuer \
    -dates
```

Check the certificate currently presented by Nginx:

```bash
openssl s_client \
    -connect jellyfin.robynshomelab.dev:443 \
    -servername jellyfin.robynshomelab.dev \
    </dev/null 2>/dev/null \
    | openssl x509 -noout -subject -issuer -dates
```

Repeat with the appropriate hostname when checking another service.

## Certificate Permissions

Private keys are sensitive and must remain protected.

Check:

```bash
ls -l /etc/letsencrypt/live/jellyfin.robynshomelab.dev/
```

Do not change private-key permissions unnecessarily.

The Cloudflare credentials file is particularly restricted:

```text
/root/.secrets/certbot/cloudflare.ini
```

Expected:

```text
owner: root
group: root
mode: 600
```

## Certificate Migration

The certificates were originally generated on CT100 before the reverse proxy was moved to CT106.

They were migrated to CT106 using:

```bash
pct exec 100 -- tar -C /etc/letsencrypt -czf - archive renewal live | pct exec 106 -- tar -C /etc/letsencrypt -xzf -
```

After migration, the renewal configurations were updated to use the Cloudflare credentials stored on CT106.

The migration has been completed and Certbot now operates exclusively on CT106.

## Removing Certbot From CT100

Certbot and the old Let's Encrypt configuration were completely removed from CT100 after the migration.

CT100 now contains:

```text
Pi-hole
Unbound
ddclient
```

CT100 does **not** manage TLS certificates.

CT106 contains:

```text
Nginx
Certbot
Let's Encrypt certificates
```

This separation prevents certificate management from being coupled to the DNS server.

## Troubleshooting

### Certbot cannot access the Cloudflare credentials

Check that the file exists:

```bash
ls -l /root/.secrets/certbot/cloudflare.ini
```

Expected permissions:

```text
-rw------- 1 root root
```

If the file has incorrect permissions:

```bash
chmod 600 /root/.secrets/certbot/cloudflare.ini
```

Ensure it is owned by root:

```bash
chown root:root /root/.secrets/certbot/cloudflare.ini
```

### Cloudflare authentication fails

Verify that the API token:

* belongs to the Cloudflare account controlling `robynshomelab.dev`
* has DNS edit permission
* is scoped to the correct zone
* has not expired or been revoked

Do not place the token directly into a shell command or documentation.

### DNS challenge fails

Run:

```bash
certbot renew --dry-run
```

Check the relevant renewal configuration:

```bash
cat /etc/letsencrypt/renewal/jellyfin.robynshomelab.dev.conf
```

Confirm that:

```ini
dns_cloudflare_credentials = /root/.secrets/certbot/cloudflare.ini
```

and:

```ini
dns_cloudflare_propagation_seconds = 30
```

are present.

### Certificate renewed but Nginx still presents the old certificate

Reload Nginx:

```bash
systemctl reload nginx
```

Then inspect the certificate again:

```bash
openssl s_client \
    -connect jellyfin.robynshomelab.dev:443 \
    -servername jellyfin.robynshomelab.dev \
    </dev/null 2>/dev/null \
    | openssl x509 -noout -dates
```

### Check Certbot logs

Certbot logs are stored under:

```text
/var/log/letsencrypt/
```

List the logs:

```bash
ls -lah /var/log/letsencrypt/
```

## Security Considerations

The Cloudflare API token provides DNS modification access and must therefore be treated as a secret.

The following must never be committed to Git:

```text
/root/.secrets/certbot/cloudflare.ini
/etc/letsencrypt/private keys
API tokens
```

The repository `.gitignore` excludes Cloudflare credential files and private-key formats.

The Cloudflare API token used by Certbot is also separate from the token used by `ddclient`.

This separation limits the impact if either credential is compromised.

## Key Commands

| Command                                                 | Purpose                                    |
| ------------------------------------------------------- | ------------------------------------------ |
| `certbot --version`                                     | Show installed Certbot version             |
| `certbot certificates`                                  | List managed certificates                  |
| `certbot renew --dry-run`                               | Test the automatic renewal process         |
| `systemctl status certbot.timer`                        | Check the renewal timer                    |
| `systemctl is-enabled certbot.timer`                    | Check whether automatic renewal is enabled |
| `systemctl list-timers certbot.timer`                   | Show the renewal schedule                  |
| `ls -l /root/.secrets/certbot/cloudflare.ini`           | Check Cloudflare credential permissions    |
| `chmod 600 /root/.secrets/certbot/cloudflare.ini`       | Restrict credential-file permissions       |
| `chown root:root /root/.secrets/certbot/cloudflare.ini` | Ensure root owns the credentials           |
| `openssl x509 ...`                                      | Inspect certificate information            |
| `systemctl reload nginx`                                | Make Nginx use updated certificates        |

## Current State

Certificate management is fully operational on CT106.

```text
CT106 nginx
├── Nginx
│   └── HTTPS reverse proxy
│
└── Certbot
    ├── jellyfin.robynshomelab.dev
    ├── status.robynshomelab.dev
    ├── beszel.robynshomelab.dev
    └── pihole.robynshomelab.dev
```

All four certificates have been successfully tested with:

```bash
certbot renew --dry-run
```

Automatic renewal through `certbot.timer` is enabled.

The old Certbot installation on CT100 has been removed.
