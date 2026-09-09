# Dynamic DNS

Dynamic DNS (DDNS) keeps the homelab's Cloudflare DNS records associated with the current WAN IP address.

The homelab uses `ddclient` running on CT100.

---

# Container

```text id="1h4m3w"
VMID:     100
Hostname: pihole
IP:       192.168.20.99
Host:     pve-1
```

The DDNS service runs alongside Pi-hole and Unbound.

---

# Role

The purpose of DDNS is to automatically update the relevant Cloudflare DNS record if the ISP-assigned WAN IP changes.

The architecture is:

```text id="2n1k0m"
ISP
 │
 ▼
WAN IP
 │
 ▼
Router
 │
 ▼
CT100
192.168.20.99
 │
 ▼
ddclient
 │
 ▼
Cloudflare DNS
```

---

# Cloudflare

Cloudflare is authoritative for:

```text id="g9pyw4"
robynshomelab.dev
```

The DDNS client communicates with Cloudflare's API to update the configured DNS record.

Cloudflare records used by the homelab are primarily DNS records rather than Cloudflare-proxied application traffic.

---

# Current DNS Architecture

The Panel hostname has a public Cloudflare DNS record:

```text id="8gzh6u"
panel.robynshomelab.dev
```

The public record contains the WAN IP and is configured as DNS-only.

Internally, Pi-hole provides split DNS so that the same hostname resolves to Nginx:

```text id="3f1f7e"
LAN / NetBird client
       │
       ▼
Pi-hole
192.168.20.99
       │
       ▼
192.168.20.94
       │
       ▼
Nginx
```

This means a changing WAN IP does not affect normal internal access.

---

# Why DDNS Is Still Used

Although internal clients use Pi-hole split DNS, maintaining the public Cloudflare record remains useful for:

* Keeping the public DNS zone current
* Maintaining a consistent public hostname
* DNS-01 ACME certificate validation
* Future changes to external connectivity

A public DNS record does not itself provide network access to the homelab.

The router currently has no port forwarding configured for the homelab services.

---

# ddclient

`ddclient` runs on CT100.

Check its service:

```bash id="6s0d6x"
systemctl status ddclient
```

Start:

```bash id="3lkl29"
systemctl start ddclient
```

Restart:

```bash id="em4lpf"
systemctl restart ddclient
```

Enable at boot:

```bash id="w1zq7a"
systemctl enable ddclient
```

---

# Configuration

The ddclient configuration is stored on CT100.

The configuration contains Cloudflare authentication information and therefore should **not** be committed to GitHub.

Do not place API tokens, API keys, or other Cloudflare credentials in this documentation.

Inspect the configuration directly on CT100 when troubleshooting.

---

# Cloudflare Authentication

The DDNS client requires permission to update the relevant Cloudflare DNS record.

The credential should follow the principle of least privilege.

A scoped Cloudflare API token is preferred over broad account credentials where supported by the existing configuration.

Credentials should be stored only on the host running ddclient.

---

# Update Process

When the WAN IP changes:

```text id="9lhw8x"
WAN IP changes
      │
      ▼
ddclient detects change
      │
      ▼
Cloudflare API
      │
      ▼
DNS record updated
```

The update process should not require any manual changes to the homelab.

---

# Checking the Current WAN IP

The current WAN address can be checked from CT100 with an external IP detection service.

For example:

```bash id="q8o9lz"
curl -4 https://icanhazip.com
```

The returned address should correspond to the current public WAN address.

---

# Checking Cloudflare DNS

From a system with DNS tools installed:

```bash id="8s3i2v"
dig panel.robynshomelab.dev
```

Because internal split DNS is in use, this may return the internal Nginx address when queried through Pi-hole.

To inspect the public Cloudflare record specifically, query an external resolver:

```bash id="r9qf5d"
dig @1.1.1.1 panel.robynshomelab.dev
```

The public result should correspond to the current WAN IP.

---

# Important Split-DNS Distinction

There are two different answers for the same hostname depending on where the DNS query originates.

Internal:

```text id="7p6i5n"
panel.robynshomelab.dev
        ↓
192.168.20.94
```

Public:

```text id="2zn5ct"
panel.robynshomelab.dev
        ↓
WAN IP
```

This is intentional.

The internal address allows clients to reach Nginx directly without hairpinning through the router.

The public record remains available through Cloudflare DNS.

---

# Troubleshooting

## Check ddclient

```bash id="k0k9qb"
systemctl status ddclient
```

Check recent logs:

```bash id="f0n7u9"
journalctl -u ddclient -n 100 --no-pager
```

Follow logs:

```bash id="4t1q5e"
journalctl -u ddclient -f
```

---

# Force an Update

If required, run ddclient manually using the installed configuration.

First inspect the available options:

```bash id="l7p4j5"
ddclient --help
```

Then perform a manual update using the appropriate configuration and flags.

Do not place credentials directly into shell commands that may be retained in shell history.

---

# Verify External Address

```bash id="v4r9t0"
curl -4 https://icanhazip.com
```

Compare the result against the public Cloudflare DNS record:

```bash id="9l2f5m"
dig @1.1.1.1 panel.robynshomelab.dev
```

If they differ after sufficient DNS propagation time, investigate ddclient and Cloudflare authentication.

---

# Common Failure Points

If DDNS stops updating, check:

```text id="y3g4jv"
CT100 running
     │
     ▼
ddclient running
     │
     ▼
Internet connectivity
     │
     ▼
WAN IP detection
     │
     ▼
Cloudflare API authentication
     │
     ▼
Cloudflare DNS record
```

---

# DDNS vs Internal DNS

DDNS and Pi-hole split DNS perform different jobs.

```text id="2dr9ra"
ddclient
└── Keeps public DNS current

Pi-hole
└── Provides internal DNS overrides
```

They should not be treated as competing DNS systems.

---

# Relationship With Certbot

The Cloudflare DNS zone is also used for DNS-01 certificate validation.

The certificate workflow is:

```text id="n5y17w"
Certbot
   │
   ▼
Cloudflare DNS
   │
   ▼
_acme-challenge record
   │
   ▼
Certificate Authority
```

DDNS updates the normal public DNS record, while Certbot temporarily manages ACME challenge records.

These are separate functions.

---

# Security

DDNS credentials are sensitive.

Do not commit:

* Cloudflare API tokens
* Cloudflare API keys
* Passwords
* Environment files containing secrets
* Full ddclient configurations containing credentials

The repository should document the configuration structure and operational behaviour without exposing authentication material.

---

# Current State

The current DDNS deployment is:

```text id="v8y0kq"
CT100
192.168.20.99
 │
 └── ddclient
       │
       ▼
   Cloudflare
       │
       ▼
panel.robynshomelab.dev
```

Internal clients use Pi-hole split DNS and resolve the Panel hostname to:

```text id="45e1vz"
192.168.20.94
```

The public Cloudflare record remains DNS-only.

---

# Operational Principles

The DDNS deployment follows these principles:

* `ddclient` runs on CT100
* Cloudflare is the authoritative DNS provider
* Public DNS is kept synchronized with the WAN IP
* Internal clients use Pi-hole split DNS
* Cloudflare proxying is not required
* Router port forwarding is not required
* Cloudflare credentials remain private
* DDNS and ACME DNS-01 are separate functions

---

# Future Improvements

Potential future improvements include:

* Verify and document the exact ddclient update interval
* Confirm the current Cloudflare API token scope
* Add monitoring for DDNS update failures
* Document the exact Cloudflare record managed by ddclient
* Add a periodic external DNS verification check
* Include DDNS health in the homelab monitoring strategy
