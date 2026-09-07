# Pi-hole

## Overview

Pi-hole provides the primary DNS service for the homelab.

It runs inside **CT 100** on the Dell OptiPlex 3060:

```text
VMID:     100
Hostname: pihole-nginx
IP:       192.168.20.99
```

Pi-hole is responsible for:

* Providing DNS to local clients
* DNS filtering and blocking
* Providing local DNS records
* Forwarding external DNS queries to Unbound
* Providing DNS visibility and query statistics

Pi-hole is also the DNS endpoint used by authorised NetBird clients when accessing the homelab remotely.

---

## DNS Architecture

The homelab uses Pi-hole as the client-facing DNS server and Unbound as the recursive resolver.

```text
Client
  │
  │ DNS :53
  ▼
Pi-hole
192.168.20.99
  │
  │ 127.0.0.1:5335
  ▼
Unbound
  │
  │ Recursive DNS
  ▼
DNS hierarchy
```

This provides a clear separation between:

* **Pi-hole** — client DNS service, filtering and local records
* **Unbound** — recursive DNS resolution and DNSSEC validation

Unbound is not directly exposed to the LAN.

---

## Installation

Pi-hole is installed inside the Debian 12 CT 100 container.

The container also hosts:

* Nginx
* Unbound
* ddclient

These services were grouped together because they provide closely related network infrastructure.

---

## Network Configuration

Pi-hole listens on the standard DNS port:

```text
TCP 53
UDP 53
```

The container's address is:

```text
192.168.20.99
```

Clients therefore use:

```text
192.168.20.99
```

as their DNS server.

Pi-hole forwards external queries to Unbound:

```text
127.0.0.1#5335
```

This means the external DNS flow is:

```text
Client
  │
  ▼
192.168.20.99:53
  │
  ▼
127.0.0.1:5335
  │
  ▼
Unbound
```

---

## Pi-hole Web Interface

Pi-hole's web interface originally used the standard HTTP/HTTPS ports.

Because Nginx is used as the homelab's central reverse proxy, Pi-hole's own web server was moved to port `8080`.

The relevant configuration is:

```toml
port = "8080o"
```

Pi-hole therefore provides its local web interface at:

```text
http://192.168.20.99:8080
```

Nginx handles the public-facing HTTPS endpoint:

```text
https://pihole.robynshomelab.dev
```

The resulting flow is:

```text
Client
  │
  │ HTTPS :443
  ▼
Nginx
192.168.20.99
  │
  │ HTTP :8080
  ▼
Pi-hole
```

This prevents Pi-hole's web server from competing with Nginx for ports 80 and 443.

---

## Local DNS Records

Pi-hole provides internal DNS records for homelab services.

Current records include:

| Hostname                     |         Address | Purpose                    |
| ---------------------------- | --------------: | -------------------------- |
| `jellyfin.robynshomelab.dev` | `192.168.20.99` | Jellyfin HTTPS endpoint    |
| `status.robynshomelab.dev`   | `192.168.20.99` | Uptime Kuma HTTPS endpoint |
| `beszel.robynshomelab.dev`   | `192.168.20.99` | Beszel HTTPS endpoint      |
| `pihole.robynshomelab.dev`   | `192.168.20.99` | Pi-hole HTTPS endpoint     |

These records intentionally point to Nginx rather than directly to the backend containers.

For example:

```text
jellyfin.robynshomelab.dev
        │
        ▼
192.168.20.99
     Nginx
        │
        ▼
192.168.20.98:8096
     Jellyfin
```

This allows the same hostname to be used for the HTTPS reverse proxy regardless of the backend service's internal port.

---

## Pi-hole and NetBird

NetBird clients use Pi-hole as their DNS server when remote access is enabled.

The relevant traffic path is:

```text
Remote device
      │
      │ NetBird
      ▼
CT 101 - NetBird
      │
      ▼
192.168.20.99:53
      │
      ▼
Pi-hole
      │
      ▼
Unbound
```

This allows a remote device such as an iPhone to resolve the same internal homelab hostnames that are available from the local network.

For example:

```text
iPhone
  │
  │ NetBird
  ▼
Pi-hole
  │
  ▼
jellyfin.robynshomelab.dev
  │
  ▼
192.168.20.99
```

---

## Pi-hole and Nginx

Pi-hole and Nginx run in the same container but use different ports.

```text
Pi-hole DNS
:53

Pi-hole Web
:8080

Nginx HTTP
:80

Nginx HTTPS
:443
```

This separation allows Nginx to provide the central HTTPS endpoint while Pi-hole continues providing DNS.

---

## Pi-hole Configuration

The Pi-hole web server port is configured in:

```text
/etc/pihole/pihole.toml
```

The relevant setting is:

```toml
port = "8080o"
```

The `o` suffix specifies the HTTP interface behaviour used by Pi-hole.

Pi-hole's web server domain was also configured so that the reverse-proxied hostname is recognised correctly:

```bash
pihole-FTL --config webserver.domain "pihole.robynshomelab.dev"
```

After changing the setting, Pi-hole FTL was restarted:

```bash
systemctl restart pihole-FTL
```

This resolved the issue where the Pi-hole web interface did not correctly recognise the reverse-proxied hostname.

---

## Upstream DNS

Pi-hole uses Unbound as its upstream resolver.

The configured upstream is:

```text
127.0.0.1#5335
```

The Pi-hole configuration was changed using:

```bash
pihole-FTL --config dns.upstreams '[ "127.0.0.1#5335" ]'
```

The resulting architecture is:

```text
Client
  │
  ▼
Pi-hole :53
  │
  ▼
Unbound :5335
  │
  ▼
Internet DNS hierarchy
```

Pi-hole therefore does not rely on a conventional third-party recursive DNS resolver for external lookups.

---

## Testing

DNS functionality should be tested at several layers.

### Test Pi-hole

```bash
dig en.wikipedia.org @127.0.0.1
```

This queries the local Pi-hole DNS service.

A successful response confirms that Pi-hole is answering DNS requests.

---

### Test Unbound Directly

```bash
dig pi-hole.net @127.0.0.1 -p 5335
```

This bypasses Pi-hole and queries Unbound directly.

A successful response confirms that Unbound itself can perform recursive DNS resolution.

---

### Test Local DNS

```bash
dig jellyfin.robynshomelab.dev @127.0.0.1
```

This verifies that Pi-hole is returning the internal DNS record.

The expected address is:

```text
192.168.20.99
```

The response should also contain the `aa` flag, indicating that the answer is authoritative.

---

### Test DNSSEC

A valid DNSSEC-signed domain can be queried directly against Unbound:

```bash
dig +ad dnssec.works @127.0.0.1 -p 5335
```

The response should contain the `ad` flag when DNSSEC validation succeeds.

A deliberately broken DNSSEC test domain can be used to confirm that validation failures are rejected:

```bash
dig fail01.dnssec.works @127.0.0.1 -p 5335
```

The expected result is:

```text
SERVFAIL
```

---

## Troubleshooting

### Pi-hole DNS unavailable

Check whether Pi-hole FTL is running:

```bash
systemctl status pihole-FTL
```

Check whether port 53 is listening:

```bash
ss -tulpn | grep ':53'
```

Then test DNS locally:

```bash
dig example.com @127.0.0.1
```

---

### Unbound unavailable

Check its service:

```bash
systemctl status unbound
```

Check the configuration:

```bash
unbound-checkconf
```

A successful configuration check should report no errors.

Test Unbound directly:

```bash
dig example.com @127.0.0.1 -p 5335
```

---

### Pi-hole web interface unavailable

Check the FTL service:

```bash
systemctl status pihole-FTL
```

Check whether port 8080 is listening:

```bash
ss -tulpn | grep ':8080'
```

Test the local web interface:

```bash
curl -I http://127.0.0.1:8080
```

If the local interface works but the HTTPS hostname does not, investigate Nginx and TLS rather than Pi-hole itself.

---

### Reverse-proxy hostname problem

Check the configured Pi-hole webserver domain:

```bash
pihole-FTL --config webserver.domain
```

If necessary, set it again:

```bash
pihole-FTL --config webserver.domain "pihole.robynshomelab.dev"
```

Then restart FTL:

```bash
systemctl restart pihole-FTL
```

---

## Key Commands

| Command                              | Purpose                                  |
| ------------------------------------ | ---------------------------------------- |
| `pihole-FTL --config ...`            | Read or modify Pi-hole FTL configuration |
| `systemctl status pihole-FTL`        | Check Pi-hole's FTL service              |
| `systemctl restart pihole-FTL`       | Restart Pi-hole FTL                      |
| `dig example.com @127.0.0.1`         | Test Pi-hole DNS                         |
| `dig example.com @127.0.0.1 -p 5335` | Test Unbound directly                    |
| `ss -tulpn`                          | Show listening network sockets           |
| `curl -I http://127.0.0.1:8080`      | Test Pi-hole's local web interface       |
| `unbound-checkconf`                  | Validate Unbound configuration           |

### Important `dig` options

The DNS testing commands used throughout this homelab are worth understanding.

```text
@server
```

Specifies which DNS server should receive the query.

For example:

```bash
dig example.com @127.0.0.1
```

queries the local machine.

```text
-p port
```

Specifies a non-standard DNS port.

For example:

```bash
dig example.com @127.0.0.1 -p 5335
```

queries Unbound instead of the normal DNS service on port 53.

```text
+short
```

Displays a simplified answer.

For example:

```bash
dig jellyfin.robynshomelab.dev +short
```

is useful when only the returned IP address is required.

```text
+ad
```

Requests that the DNSSEC authenticated-data status be displayed.

---

## Security Considerations

Pi-hole is a core infrastructure service and should not be exposed directly to the public Internet.

The public Cloudflare DNS zone does not contain the internal `192.168.20.x` service addresses.

Remote access to Pi-hole is provided through the private NetBird network.

The Cloudflare API credentials used for related infrastructure are stored outside the Git repository and must never be committed.

---

## Future Updates

This document should be updated when:

* Pi-hole configuration changes
* DNS filtering policies are changed
* Additional local DNS records are created
* NetBird DNS integration changes
* Pi-hole is moved to another host
* DNS architecture changes
* Additional DNS security measures are implemented
