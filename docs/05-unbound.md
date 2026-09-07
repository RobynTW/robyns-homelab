# Unbound

## Overview

Unbound is the recursive DNS resolver used by the homelab.

It runs inside **CT 100** alongside Pi-hole, Nginx and ddclient:

```text
VMID:     100
Hostname: pihole-nginx
IP:       192.168.20.99
```

Unbound is responsible for:

* Recursive DNS resolution
* DNSSEC validation
* Resolving external DNS queries without relying on a third-party recursive resolver
* Providing the upstream DNS service for Pi-hole

Pi-hole remains the client-facing DNS server, while Unbound performs the recursive resolution.

---

## DNS Architecture

The complete DNS architecture is:

```text
Client
   │
   │ DNS :53
   ▼
Pi-hole
192.168.20.99
   │
   │ DNS :5335
   ▼
Unbound
127.0.0.1:5335
   │
   │ Recursive queries
   ▼
DNS hierarchy
```

The two services have deliberately separate responsibilities.

### Pi-hole

Pi-hole provides:

* Client-facing DNS
* Ad and tracker blocking
* Local DNS records
* Query logging and statistics
* Upstream forwarding

### Unbound

Unbound provides:

* Recursive resolution
* DNSSEC validation
* DNS caching
* DNS hardening

---

## Why Unbound Is Bound to Port 5335

Standard DNS uses port `53`.

Pi-hole FTL already owns port 53, so Unbound cannot also bind to the same address and port.

Unbound therefore listens only on:

```text
127.0.0.1:5335
```

This has two benefits:

1. Pi-hole remains the only client-facing DNS service.
2. Unbound cannot be directly queried by other devices on the LAN.

The resulting arrangement is:

```text
LAN clients
    │
    ▼
Pi-hole :53
    │
    ▼
Unbound 127.0.0.1:5335
```

---

## Installation

Unbound was installed inside CT 100.

The configuration is stored under:

```text
/etc/unbound/
```

The primary homelab-specific configuration is:

```text
/etc/unbound/unbound.conf.d/pi-hole.conf
```

---

## Configuration

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

## Configuration Explanation

### `verbosity`

```text
verbosity: 0
```

Keeps normal Unbound logging relatively quiet.

Higher verbosity levels can be temporarily enabled during troubleshooting.

---

### `interface`

```text
interface: 127.0.0.1
```

Restricts Unbound to the local loopback interface.

Only applications running inside CT 100 can directly access the resolver.

This is intentional because Pi-hole is the client-facing DNS service.

---

### `port`

```text
port: 5335
```

Moves Unbound away from the standard DNS port.

Pi-hole continues listening on port 53.

---

### IPv4 and IPv6

```text
do-ip4: yes
do-udp: yes
do-tcp: yes

do-ip6: yes
prefer-ip6: no
```

IPv4, UDP and TCP DNS queries are supported.

IPv6 is enabled, but IPv6 is not preferred when resolving upstream DNS information.

---

## DNS Hardening

The configuration includes:

```text
harden-glue: yes
harden-dnssec-stripped: yes
```

These settings provide additional protection during DNS resolution.

DNSSEC validation is particularly important because Unbound is responsible for validating signed DNS responses.

---

## EDNS Buffer Size

```text
edns-buffer-size: 1232
```

The EDNS buffer size is set to 1232 bytes.

This is a commonly used conservative value that helps reduce problems associated with fragmented DNS responses.

---

## Prefetching

```text
prefetch: yes
```

Allows Unbound to refresh frequently used cached records before they expire.

This can reduce latency for repeatedly requested DNS records.

---

## Resource Configuration

The current configuration uses:

```text
num-threads: 1
so-rcvbuf: 1m
```

The homelab does not currently generate enough DNS traffic to require multiple resolver threads.

The configuration therefore prioritises simplicity and low resource usage.

---

## Private Address Protection

Unbound is configured to recognise several private and reserved address ranges.

These include:

```text
192.168.0.0/16
10.0.0.0/8
172.16.0.0/12
fd00::/8
fe80::/10
```

as well as several reserved documentation and special-purpose networks.

This helps prevent inappropriate resolution of private or reserved addresses through external DNS.

---

## Pi-hole Upstream Configuration

Pi-hole forwards external DNS requests to Unbound.

The configured upstream is:

```text
127.0.0.1#5335
```

It was configured using:

```bash
pihole-FTL --config dns.upstreams '[ "127.0.0.1#5335" ]'
```

This creates the following chain:

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
DNS hierarchy
```

---

## Recursive DNS

Unlike a conventional configuration that forwards queries to a resolver such as Google or Cloudflare, Unbound performs recursive resolution.

Conceptually:

```text
Client
  │
  ▼
Pi-hole
  │
  ▼
Unbound
  │
  ├── Root servers
  │
  ├── TLD servers
  │
  └── Authoritative servers
```

This means the homelab's recursive DNS resolver obtains answers through the DNS hierarchy rather than simply forwarding every query to another recursive DNS provider.

---

## DNSSEC

DNSSEC allows DNS responses to be cryptographically validated.

Unbound performs DNSSEC validation before returning validated answers to Pi-hole.

A valid DNSSEC response can be tested with:

```bash
dig +ad dnssec.works @127.0.0.1 -p 5335
```

The `ad` flag indicates that the response has been authenticated through DNSSEC validation.

The test performed during setup returned a valid DNSSEC response.

---

## Testing DNSSEC Failure

A deliberately broken DNSSEC domain can be used to confirm that validation failures are rejected.

The test used was:

```bash
dig fail01.dnssec.works @127.0.0.1 -p 5335
```

The expected result is:

```text
SERVFAIL
```

This is an important test because merely receiving a DNS response does not prove that DNSSEC validation is functioning correctly.

The successful result demonstrated that:

* Valid DNSSEC responses are accepted.
* Invalid DNSSEC responses are rejected.

---

## Testing Unbound Directly

To test Unbound without involving Pi-hole:

```bash
dig pi-hole.net @127.0.0.1 -p 5335
```

This directly queries:

```text
127.0.0.1:5335
```

A successful response confirms that Unbound itself can perform recursive DNS resolution.

---

## Testing the Complete DNS Chain

To test Pi-hole and Unbound together:

```bash
dig en.wikipedia.org @127.0.0.1
```

This sends the query to Pi-hole on port 53.

The expected path is:

```text
dig
 │
 ▼
Pi-hole :53
 │
 ▼
Unbound :5335
 │
 ▼
DNS hierarchy
 │
 ▼
Response
```

This test confirms that the two DNS services work together rather than merely testing Unbound independently.

---

## Initial Port Conflict

During initial setup, Unbound failed to start because it attempted to bind to the standard DNS port and IPv6 loopback address.

Pi-hole FTL was already using port 53.

The conflict was effectively:

```text
Pi-hole FTL
127.0.0.1:53
     ▲
     │
     │ conflict
     │
Unbound
::1:53
```

The configuration was changed so that Unbound uses:

```text
127.0.0.1:5335
```

After the configuration was corrected, `unbound-checkconf` reported no configuration errors and Unbound started successfully.

This is an important example of why services providing the same protocol should have clearly defined listening addresses and ports.

---

## Configuration Validation

Before restarting or troubleshooting Unbound, the configuration can be checked with:

```bash
unbound-checkconf
```

This validates the Unbound configuration files.

A successful check should produce no configuration errors.

This is preferable to restarting a service with an unverified configuration.

---

## Service Management

Unbound is managed through systemd.

Check its status:

```bash
systemctl status unbound
```

Restart it after configuration changes:

```bash
systemctl restart unbound
```

Enable it at boot:

```bash
systemctl enable unbound
```

Check whether it is enabled:

```bash
systemctl is-enabled unbound
```

---

## Port Verification

To determine whether Unbound is listening:

```bash
ss -tulpn | grep ':5335'
```

The expected listener is:

```text
127.0.0.1:5335
```

Port 53 should remain owned by Pi-hole rather than Unbound.

This can be checked with:

```bash
ss -tulpn | grep ':53'
```

---

## Troubleshooting

### Unbound will not start

First validate the configuration:

```bash
unbound-checkconf
```

If the configuration is valid, check the service:

```bash
systemctl status unbound
```

Then inspect the listening ports:

```bash
ss -tulpn | grep -E ':53|:5335'
```

This can reveal whether another service has already claimed the required port.

---

### Unbound starts but DNS fails

Test Unbound directly:

```bash
dig pi-hole.net @127.0.0.1 -p 5335
```

If this fails, the problem is within Unbound or its ability to reach upstream authoritative DNS infrastructure.

If this succeeds, test Pi-hole:

```bash
dig pi-hole.net @127.0.0.1
```

This separates an Unbound problem from a Pi-hole upstream configuration problem.

---

### DNSSEC appears not to work

Test a known valid DNSSEC domain:

```bash
dig +ad dnssec.works @127.0.0.1 -p 5335
```

Then test a deliberately broken DNSSEC domain:

```bash
dig fail01.dnssec.works @127.0.0.1 -p 5335
```

Expected behaviour:

```text
Valid DNSSEC → successful response with AD flag
Broken DNSSEC → SERVFAIL
```

---

## Key Commands

| Command                                 | Purpose                              |
| --------------------------------------- | ------------------------------------ |
| `unbound-checkconf`                     | Validate Unbound configuration       |
| `systemctl status unbound`              | Check Unbound service state          |
| `systemctl restart unbound`             | Restart Unbound                      |
| `systemctl enable unbound`              | Enable Unbound at boot               |
| `systemctl is-enabled unbound`          | Check whether Unbound starts at boot |
| `ss -tulpn`                             | Display listening network sockets    |
| `dig example.com @127.0.0.1 -p 5335`    | Query Unbound directly               |
| `dig example.com @127.0.0.1`            | Query Pi-hole                        |
| `dig +ad ...`                           | Display DNSSEC authentication status |
| `pihole-FTL --config dns.upstreams ...` | Configure Pi-hole's upstream DNS     |

### Understanding the important `dig` options

```text
@127.0.0.1
```

Specifies the DNS server to query.

```text
-p 5335
```

Specifies Unbound's non-standard DNS port.

```text
+ad
```

Requests the authenticated-data status to be displayed.

```text
+short
```

Displays a simplified response.

These options make `dig` particularly useful for testing individual layers of the DNS architecture.

---

## Security Considerations

Unbound is not exposed directly to the LAN.

It listens only on:

```text
127.0.0.1:5335
```

Pi-hole is the only DNS service exposed to clients on the homelab network.

This reduces the attack surface and prevents clients from bypassing Pi-hole's DNS filtering and local records.

Unbound's DNSSEC validation provides additional protection against forged or invalid DNS responses.

---

## Future Updates

This document should be updated when:

* Unbound configuration changes
* DNSSEC configuration changes
* DNS architecture changes
* Additional DNS hardening is introduced
* Pi-hole is moved to another host
* Unbound is moved to a dedicated container
* DNS performance requirements increase
