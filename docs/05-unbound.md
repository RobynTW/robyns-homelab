# Unbound

## Overview

Unbound provides recursive DNS resolution for the homelab.

It runs inside **CT 100** on the Dell OptiPlex 3060 alongside Pi-hole and ddclient.

```text
VMID:     100
Hostname: pihole
IP:       192.168.20.99
```

Unbound is used as the upstream DNS resolver for Pi-hole.

Rather than forwarding DNS requests to a conventional third-party resolver such as Google or Cloudflare, Unbound performs recursive DNS resolution directly against the DNS hierarchy.

---

## DNS Architecture

The homelab uses a two-stage DNS architecture:

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
  │ Recursive resolution
  ▼
Root DNS servers
  │
  ▼
TLD servers
  │
  ▼
Authoritative DNS servers
```

Pi-hole is responsible for:

* Client-facing DNS
* DNS filtering
* Local DNS records
* Query statistics

Unbound is responsible for:

* Recursive DNS resolution
* DNSSEC validation
* Resolving external domains without relying on a third-party recursive resolver

---

## Installation

Unbound is installed inside Debian 12 **CT 100**.

The container also hosts:

* Pi-hole
* ddclient

Nginx and Certbot were previously hosted in this container but have since been moved to the dedicated **CT 106** Nginx container.

The current infrastructure separation is:

```text
CT 100 — pihole
├── Pi-hole
├── Unbound
└── ddclient

CT 106 — nginx
├── Nginx
└── Certbot
```

---

## Network Configuration

Unbound deliberately does not listen on the normal DNS port.

It listens only on the loopback interface:

```text
127.0.0.1:5335
```

This means Unbound is only accessible from the Pi-hole container itself.

The relevant configuration is:

```text
interface: 127.0.0.1
port: 5335
```

Unbound therefore cannot be queried directly by other devices on the LAN.

The DNS flow is:

```text
LAN client
    │
    ▼
Pi-hole :53
    │
    ▼
Unbound 127.0.0.1:5335
```

This provides a clear security boundary between the client-facing DNS service and the recursive resolver.

---

## Configuration

The primary Unbound configuration used by the homelab is:

```text
/etc/unbound/unbound.conf.d/pi-hole.conf
```

The current configuration is:

```text
server:
    verbosity: 0

    interface: 127.0.0.1
    port: 5335

    do-ip4: yes
    do-udp: yes
    do-tcp: yes

    do-ip6: yes
    prefer-ip6: no

    harden-glue: yes
    harden-dnssec-stripped: yes

    edns-buffer-size: 1232
    prefetch: yes

    num-threads: 1
    so-rcvbuf: 1m

    private-address: 192.168.0.0/16
    private-address: 169.254.0.0/16
    private-address: 172.16.0.0/12
    private-address: 10.0.0.0/8
    private-address: fd00::/8
    private-address: fe80::/10

    private-address: 192.0.2.0/24
    private-address: 198.51.100.0/24
    private-address: 203.0.113.0/24
    private-address: 255.255.255.255/32
    private-address: 2001:db8::/32
```

---

## Configuration Options

### Loopback interface

```text
interface: 127.0.0.1
```

Restricts Unbound to the local machine.

This prevents other devices from directly accessing the recursive resolver.

---

### Non-standard DNS port

```text
port: 5335
```

Unbound uses port `5335` rather than port `53`.

Port 53 is reserved for Pi-hole, which acts as the client-facing DNS service.

---

### IPv4 and IPv6

```text
do-ip4: yes
do-udp: yes
do-tcp: yes

do-ip6: yes
prefer-ip6: no
```

IPv4 and IPv6 DNS transport are enabled.

IPv6 is supported but not preferred for upstream resolution.

Both UDP and TCP DNS transport are enabled.

---

### DNS hardening

```text
harden-glue: yes
harden-dnssec-stripped: yes
```

These options enable additional protections during DNS resolution.

In particular, `harden-dnssec-stripped` helps prevent DNSSEC validation from being bypassed when DNSSEC information has been removed from a response.

---

### EDNS buffer size

```text
edns-buffer-size: 1232
```

The EDNS buffer size is limited to 1232 bytes.

This is a commonly used conservative value intended to reduce problems caused by fragmented DNS responses.

---

### Prefetching

```text
prefetch: yes
```

Unbound can refresh cached records before they expire when they are being actively queried.

This can improve response times for frequently accessed domains.

---

### Threading

```text
num-threads: 1
```

Unbound currently uses a single worker thread.

This is appropriate for the relatively small homelab workload.

---

### Socket receive buffer

```text
so-rcvbuf: 1m
```

Sets the UDP socket receive buffer to approximately 1 MiB.

---

## Private Address Protection

The configuration contains several `private-address` entries.

These identify address ranges that should be treated as private or reserved and prevent inappropriate resolution of these addresses through external DNS.

RFC1918 private IPv4 ranges are included:

```text
192.168.0.0/16
172.16.0.0/12
10.0.0.0/8
```

IPv6 local ranges are also included:

```text
fd00::/8
fe80::/10
```

Other reserved documentation and special-use ranges are included as well:

```text
169.254.0.0/16
192.0.2.0/24
198.51.100.0/24
203.0.113.0/24
255.255.255.255/32
2001:db8::/32
```

These settings provide additional protection against resolving inappropriate private or reserved addresses from external DNS.

---

## Pi-hole Integration

Pi-hole is configured to use Unbound as its upstream resolver.

The configured Pi-hole upstream is:

```text
127.0.0.1#5335
```

The Pi-hole configuration was set using:

```bash
pihole-FTL --config dns.upstreams '[ "127.0.0.1#5335" ]'
```

The resulting DNS flow is:

```text
Client
  │
  │ :53
  ▼
Pi-hole
  │
  │ :5335
  ▼
Unbound
  │
  ▼
DNS hierarchy
```

Pi-hole therefore remains the only DNS server that clients need to know about.

---

## DNSSEC

Unbound performs DNSSEC validation for domains that support DNSSEC.

A successful DNSSEC validation can be tested with:

```bash
dig +ad dnssec.works @127.0.0.1 -p 5335
```

The response should contain:

```text
ad
```

The `ad` flag indicates that the response data was authenticated according to DNSSEC validation.

A deliberately broken DNSSEC domain can be used to verify that invalid DNSSEC responses are rejected:

```bash
dig fail01.dnssec.works @127.0.0.1 -p 5335
```

The expected result is:

```text
SERVFAIL
```

This confirms that Unbound is not simply returning an invalid DNSSEC response.

---

## Testing

### Validate Configuration

Before restarting or reloading Unbound after configuration changes, validate the configuration:

```bash
unbound-checkconf
```

A successful check should report no configuration errors.

---

### Check Service Status

Check whether Unbound is running:

```bash
systemctl status unbound
```

A healthy installation should show:

```text
active (running)
```

---

### Check Listening Port

Verify that Unbound is listening on its configured loopback address and port:

```bash
ss -tulpn | grep ':5335'
```

The expected listener is:

```text
127.0.0.1:5335
```

Unbound should not be listening on the LAN-facing address.

---

### Test Recursive Resolution

Query Unbound directly:

```bash
dig pi-hole.net @127.0.0.1 -p 5335
```

A successful response confirms that Unbound can perform recursive DNS resolution.

---

### Test DNSSEC

Valid DNSSEC:

```bash
dig +ad dnssec.works @127.0.0.1 -p 5335
```

Expected:

```text
NOERROR
```

with the `ad` flag present.

Invalid DNSSEC:

```bash
dig fail01.dnssec.works @127.0.0.1 -p 5335
```

Expected:

```text
SERVFAIL
```

---

### Test Pi-hole → Unbound

To test the complete local DNS chain:

```bash
dig en.wikipedia.org @127.0.0.1
```

This sends the query to Pi-hole on port 53.

Pi-hole should then forward the request to:

```text
127.0.0.1:5335
```

where Unbound performs the recursive lookup.

A successful response confirms that the Pi-hole → Unbound integration is functioning.

---

## Troubleshooting

### Unbound is not running

Check the service:

```bash
systemctl status unbound
```

If the service has failed, inspect the recent logs:

```bash
journalctl -u unbound -n 50 --no-pager
```

Validate the configuration:

```bash
unbound-checkconf
```

---

### Port 5335 is unavailable

Check whether anything is listening on the port:

```bash
ss -tulpn | grep ':5335'
```

The expected listener is:

```text
127.0.0.1:5335
```

If another process has claimed the port, identify it before making configuration changes.

---

### Unbound cannot resolve domains

Test Unbound directly:

```bash
dig pi-hole.net @127.0.0.1 -p 5335
```

If this fails, the problem is within Unbound or its upstream recursive communication rather than Pi-hole.

Check:

```bash
systemctl status unbound
unbound-checkconf
journalctl -u unbound -n 50 --no-pager
```

---

### Pi-hole cannot reach Unbound

First test Unbound directly:

```bash
dig pi-hole.net @127.0.0.1 -p 5335
```

If this succeeds, check Pi-hole's configured upstream:

```bash
pihole-FTL --config dns.upstreams
```

It should reference:

```text
127.0.0.1#5335
```

Then test Pi-hole:

```bash
dig en.wikipedia.org @127.0.0.1
```

---

## Security Considerations

Unbound is intentionally bound only to:

```text
127.0.0.1:5335
```

It is therefore not directly exposed to the LAN or Internet.

Clients communicate with Pi-hole instead:

```text
Client → Pi-hole → Unbound
```

This prevents the recursive resolver from becoming an independently accessible DNS service.

DNSSEC validation provides additional protection against forged or invalid DNS responses for signed domains.

The Unbound configuration should not be changed without first validating it with:

```bash
unbound-checkconf
```

---

## Key Commands

| Command                                      | Purpose                                     |
| -------------------------------------------- | ------------------------------------------- |
| `unbound-checkconf`                          | Validate the Unbound configuration          |
| `systemctl status unbound`                   | Check Unbound's service state               |
| `systemctl restart unbound`                  | Restart Unbound after configuration changes |
| `journalctl -u unbound -n 50 --no-pager`     | View recent Unbound logs                    |
| `ss -tulpn \| grep ':5335'`                  | Check the Unbound listening socket          |
| `dig example.com @127.0.0.1 -p 5335`         | Query Unbound directly                      |
| `dig +ad dnssec.works @127.0.0.1 -p 5335`    | Test successful DNSSEC validation           |
| `dig fail01.dnssec.works @127.0.0.1 -p 5335` | Test rejection of invalid DNSSEC            |
| `dig en.wikipedia.org @127.0.0.1`            | Test Pi-hole → Unbound integration          |

### Important `dig` options

```text
@server
```

Specifies the DNS server that receives the query.

For example:

```bash
dig example.com @127.0.0.1
```

queries the local DNS service.

```text
-p port
```

Specifies a non-standard DNS port.

For example:

```bash
dig example.com @127.0.0.1 -p 5335
```

queries Unbound directly.

```text
+ad
```

Requests that the DNSSEC authenticated-data status be displayed.

For example:

```bash
dig +ad dnssec.works @127.0.0.1 -p 5335
```

can be used to verify DNSSEC validation.

---

## Current Architecture

The final DNS architecture is:

```text
                         ┌─────────────────────┐
                         │       Clients       │
                         └──────────┬──────────┘
                                    │
                                    │ DNS :53
                                    ▼
                         ┌─────────────────────┐
                         │       Pi-hole      │
                         │      CT 100         │
                         │   192.168.20.99     │
                         └──────────┬──────────┘
                                    │
                                    │ 127.0.0.1:5335
                                    ▼
                         ┌─────────────────────┐
                         │       Unbound      │
                         │      CT 100         │
                         │   Recursive DNS     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                             DNS hierarchy
```

Remote NetBird clients use the same Pi-hole endpoint:

```text
Remote device
      │
      │ NetBird
      ▼
CT 101 — NetBird
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

This provides a consistent DNS architecture for both local and authorised remote clients.

---

## Future Updates

This document should be updated when:

* Unbound configuration changes
* DNSSEC behaviour changes
* The recursive resolver is moved to another container or host
* Pi-hole's upstream DNS configuration changes
* Additional DNS security measures are implemented
* IPv6 DNS behaviour is changed
* The homelab DNS architecture changes
