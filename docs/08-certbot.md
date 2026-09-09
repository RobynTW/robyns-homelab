# Certbot

Certbot manages the Let's Encrypt TLS certificates used by the homelab's Nginx reverse proxy.

It runs on CT106 alongside Nginx and uses the Cloudflare DNS API for DNS-01 certificate validation.

---

# Container

```text
VMID:     106
Hostname: nginx
IP:       192.168.20.94
Host:     pve-1
```

CT106 runs:

* Nginx
* Certbot

---

# Role

Certbot is responsible for:

* Requesting Let's Encrypt certificates
* Performing DNS-01 validation through Cloudflare
* Installing certificates for Nginx
* Renewing certificates automatically
* Providing certificate status information

The certificate architecture is:

```text
                     Cloudflare
                         │
                         │ DNS-01
                         ▼
                    Let's Encrypt
                         │
                         │ certificate
                         ▼
                      Certbot
                    CT106 .94
                         │
                         ▼
                       Nginx
                         │
                         ▼
                  Internal services
```

---

# DNS-01 Validation

The homelab uses the DNS-01 ACME challenge rather than HTTP-01.

This means Let's Encrypt validates domain ownership by checking a temporary DNS record.

The process is:

```text
Certbot
   │
   │ ACME request
   ▼
Let's Encrypt
   │
   │ requests DNS challenge
   ▼
Certbot
   │
   │ Cloudflare API
   ▼
Cloudflare DNS
   │
   │ _acme-challenge record
   ▼
Let's Encrypt
   │
   │ validation succeeds
   ▼
Certificate issued
```

This avoids requiring an Internet-accessible HTTP challenge endpoint.

---

# Cloudflare Integration

Cloudflare is authoritative for:

```text
robynshomelab.dev
```

Certbot uses the Cloudflare API to create the DNS records required for ACME validation.

Cloudflare is **not** acting as an HTTP reverse proxy.

The homelab's DNS records remain DNS-only.

---

# Current Certificates

The current certificates managed by Certbot are:

| Certificate                  | Service           | Expiry     |
| ---------------------------- | ----------------- | ---------- |
| `jellyfin.robynshomelab.dev` | Jellyfin          | 2026-12-04 |
| `status.robynshomelab.dev`   | Uptime Kuma       | 2026-12-04 |
| `beszel.robynshomelab.dev`   | Beszel            | 2026-12-04 |
| `pihole.robynshomelab.dev`   | Pi-hole           | 2026-12-04 |
| `panel.robynshomelab.dev`    | Pterodactyl Panel | 2026-12-08 |

These certificates are terminated by Nginx on:

```text
192.168.20.94:443
```

---

# Certificate Storage

Certbot stores certificates under:

```text
/etc/letsencrypt/
```

Important directories include:

```text
/etc/letsencrypt/live/
/etc/letsencrypt/archive/
/etc/letsencrypt/renewal/
```

The `live/` directory contains the active certificate paths used by services.

Certificate private keys must never be committed to Git or included in public documentation.

---

# Renewal

Certbot's automated renewal mechanism is enabled.

The system should periodically check whether certificates are approaching expiry and renew them when necessary.

Check the relevant systemd timers with:

```bash
systemctl list-timers | grep certbot
```

The timer status can also be checked with:

```bash
systemctl status certbot.timer
```

---

# Renewal Testing

A renewal dry-run has successfully completed on the current system.

To perform another dry-run:

```bash
certbot renew --dry-run
```

A successful dry-run confirms that the renewal process can complete without actually replacing the production certificates.

---

# Certificate Status

List currently managed certificates:

```bash
certbot certificates
```

This displays:

* Certificate names
* Domains
* Certificate paths
* Private-key paths
* Expiry dates

---

# Nginx Integration

Nginx uses the certificates managed by Certbot.

The general configuration is:

```text
Client
  │
  │ HTTPS :443
  ▼
Nginx
  │
  ├── Let's Encrypt certificate
  │
  └── TLS termination
       │
       ▼
Internal HTTP backend
```

The backend services do not need to independently manage publicly trusted certificates.

---

# Current Service Certificates

The certificates correspond to the following Nginx virtual hosts:

```text
jellyfin.robynshomelab.dev
status.robynshomelab.dev
beszel.robynshomelab.dev
pihole.robynshomelab.dev
panel.robynshomelab.dev
```

The corresponding backend services are:

| Hostname                     | Backend              |
| ---------------------------- | -------------------- |
| `jellyfin.robynshomelab.dev` | `192.168.20.98:8096` |
| `status.robynshomelab.dev`   | `192.168.20.95:3001` |
| `beszel.robynshomelab.dev`   | `192.168.20.96:8090` |
| `pihole.robynshomelab.dev`   | `192.168.20.99:8080` |
| `panel.robynshomelab.dev`    | `192.168.20.111:80`  |

---

# No Port Forwarding Requirement

The current certificate architecture does not require router port forwarding.

DNS-01 validation occurs through Cloudflare's DNS infrastructure rather than by connecting to the homelab over HTTP.

```text
Let's Encrypt
      │
      ▼
Cloudflare DNS
      │
      ▼
ACME DNS-01
```

The homelab does not need to expose port 80 for certificate validation.

---

# Security

Cloudflare credentials used by Certbot are sensitive.

They should:

* Never be committed to Git
* Never be placed in documentation
* Use the minimum required Cloudflare permissions
* Be stored in protected configuration files
* Be rotated if exposed

The actual API token or credentials are intentionally omitted from this document.

---

# Troubleshooting

## Check Certbot

```bash
certbot --version
```

---

## List Certificates

```bash
certbot certificates
```

---

## Check Renewal Timer

```bash
systemctl status certbot.timer
```

---

## Test Renewal

```bash
certbot renew --dry-run
```

---

## Check Renewal Logs

```bash
journalctl -u certbot
```

Depending on the installation, Certbot logs are also available under:

```text
/var/log/letsencrypt/
```

---

# If Renewal Fails

Check the following in order:

1. Confirm CT106 has Internet access.
2. Confirm Cloudflare DNS is functioning.
3. Confirm the Cloudflare API credentials remain valid.
4. Confirm the credentials have sufficient DNS permissions.
5. Run:

   ```bash
   certbot renew --dry-run
   ```
6. Inspect:

   ```bash
   /var/log/letsencrypt/
   ```
7. Check the Nginx configuration.
8. Reload Nginx after a successful certificate renewal if required.

---

# Certificate Verification

A certificate can be checked locally with:

```bash
openssl s_client \
  -connect 192.168.20.94:443 \
  -servername panel.robynshomelab.dev
```

For a hostname-based test from a client:

```bash
curl -I https://panel.robynshomelab.dev
```

The hostname should resolve through Pi-hole to:

```text
192.168.20.94
```

---

# Relationship With Other Services

Certbot sits between Cloudflare DNS and Nginx:

```text
Cloudflare
├── Authoritative DNS
├── DDNS
└── DNS-01 validation
          │
          ▼
       Certbot
          │
          ▼
        Nginx
          │
          ▼
 Internal services
```

The responsibilities are intentionally separated:

| Component     | Responsibility                    |
| ------------- | --------------------------------- |
| Cloudflare    | Authoritative DNS and DNS API     |
| Let's Encrypt | Certificate authority             |
| Certbot       | ACME client and renewal           |
| Nginx         | TLS termination and reverse proxy |
| Pi-hole       | Internal DNS/split DNS            |

---

# Operational Principles

The current certificate setup follows these principles:

* Use Let's Encrypt certificates
* Use DNS-01 validation
* Use Cloudflare for DNS validation
* Keep Cloudflare records DNS-only
* Terminate TLS at Nginx
* Automatically renew certificates
* Test renewal with dry-runs
* Keep API credentials and private keys out of Git
* Do not expose port 80 solely for ACME validation

Any new HTTPS service added behind Nginx should be added to this document after its certificate has been successfully issued and tested.
