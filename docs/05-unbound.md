# Unbound

Unbound provides recursive DNS resolution for the homelab.

It runs alongside Pi-hole in CT100. Pi-hole remains the client-facing DNS server, while Unbound performs recursive DNS resolution.

---

## Container

```text
VMID:     100
Hostname: pihole
IP:       192.168.20.99
Host:      pve-1
```

CT100 runs:

* Pi-hole
* Unbound
* ddclient

---

# DNS Architecture

The current DNS architecture is:

```text
Client
  │
  │ DNS :53
  ▼
Pi-hole
192.168.20.99
  │
  │ filtered / local DNS
  ▼
Unbound
  │
  │ recursive DNS
  ▼
DNS hierarchy
```

Pi-hole is the only DNS service that clients are expected to use directly.

Unbound is an internal upstream resolver for Pi-hole.

---

# Why Unbound Is Used

Unbound provides recursive DNS resolution rather than relying entirely on a third-party recursive resolver.

This gives the homelab greater control over DNS resolution and allows DNSSEC validation to be performed locally.

The architecture also keeps DNS filtering and recursive resolution as separate functions:

```text
Pi-hole
├── DNS filtering
├── Local DNS records
└── Client-facing DNS

Unbound
├── Recursive resolution
└── DNSSEC validation
```

---

# Listening Address

Unbound runs locally on CT100 and is configured as the upstream resolver for Pi-hole.

The expected architecture is:

```text
192.168.20.99:53
        │
        ▼
   Pi-hole FTL
        │
        ▼
   Unbound
```

Unbound should not be exposed directly to the LAN when Pi-hole is functioning as intended.

---

# Pi-hole Integration

Pi-hole forwards external DNS queries to Unbound.

For an external hostname:

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
  ├── TLD servers
  └── Authoritative DNS servers
```

For a local homelab hostname:

```text
Client
  │
  ▼
Pi-hole
  │
  ▼
Local DNS record
```

Local records therefore do not need to pass through Unbound.

---

# DNSSEC

Unbound is responsible for DNSSEC validation.

This provides cryptographic validation of DNS data where DNSSEC is available.

DNSSEC validation occurs before a response is returned to Pi-hole.

The simplified process is:

```text
DNS query
   │
   ▼
Pi-hole
   │
   ▼
Unbound
   │
   ├── Resolve
   ├── Validate DNSSEC
   │
   ▼
Validated response
   │
   ▼
Pi-hole
   │
   ▼
Client
```

---

# NetBird DNS

NetBird clients use Pi-hole as their DNS server:

```text
192.168.20.99:53
```

The NetBird DNS path is therefore:

```text
NetBird Client
      │
      ▼
CT101
      │
      ▼
Pi-hole
192.168.20.99:53
      │
      ▼
Unbound
```

This allows remote NetBird clients to use the same DNS filtering and recursive DNS infrastructure as local LAN clients.

---

# Split DNS

Pi-hole handles internal DNS records before forwarding external queries to Unbound.

For example:

```text
panel.robynshomelab.dev
```

is resolved internally by Pi-hole to:

```text
192.168.20.94
```

This query does not need to be recursively resolved by Unbound.

External queries such as:

```text
example.com
```

are instead passed through the normal recursive path:

```text
Pi-hole
   ↓
Unbound
   ↓
DNS hierarchy
```

---

# Testing

## Check Unbound Service

From CT100:

```bash
systemctl status unbound
```

The service should report as running.

---

## Check Unbound Listening Socket

From CT100:

```bash
ss -lntup | grep unbound
```

This can be used to confirm that Unbound is listening on its configured local address and port.

---

## Test Through Pi-hole

From a client:

```bash
dig @192.168.20.99 example.com
```

A successful response confirms the client-facing DNS path is functioning.

---

## Test DNSSEC

A DNSSEC-enabled test domain can be queried through Pi-hole to verify that Unbound is performing validation.

For example:

```bash
dig @192.168.20.99 cloudflare.com
```

The response should be returned successfully when the DNSSEC chain validates.

---

# Troubleshooting

If DNS resolution fails, troubleshoot the chain from the outside inward.

### 1. Check Pi-hole

```bash
systemctl status pihole-FTL
```

### 2. Check Unbound

```bash
systemctl status unbound
```

### 3. Check listening sockets

```bash
ss -lntup | grep -E ':53|:5335'
```

### 4. Test Pi-hole

```bash
dig @192.168.20.99 example.com
```

### 5. Test Unbound directly

If Unbound is configured to listen on localhost port 5335:

```bash
dig @127.0.0.1 -p 5335 example.com
```

The exact listening address and port should be confirmed against the active Unbound configuration before modifying it.

---

# Common Failure Modes

## Pi-hole Running, Unbound Stopped

Clients can reach Pi-hole, but external DNS resolution may fail because Pi-hole's configured upstream resolver is unavailable.

## Unbound Running, Pi-hole Unavailable

Clients configured to use Pi-hole will not be able to use the homelab DNS service even though Unbound itself is operational.

## NetBird DNS Failure

If CT101 cannot route traffic to:

```text
192.168.20.99/32
```

NetBird clients may lose access to the homelab DNS server.

This should be distinguished from an actual Pi-hole or Unbound failure.

---

# Security Considerations

Unbound should remain an internal resolver.

It should not be exposed directly to the public Internet.

The current architecture intentionally places Pi-hole in front of Unbound:

```text
LAN / NetBird
      │
      ▼
Pi-hole :53
      │
      ▼
Unbound
```

This provides a clear boundary between client DNS requests and recursive DNS resolution.

---

# Operational Role

Unbound is a supporting infrastructure service rather than the primary client-facing DNS service.

The responsibilities are intentionally separated:

| Component  | Responsibility                               |
| ---------- | -------------------------------------------- |
| Pi-hole    | Client-facing DNS, filtering, local records  |
| Unbound    | Recursive DNS and DNSSEC validation          |
| Cloudflare | Authoritative DNS for `robynshomelab.dev`    |
| ddclient   | Dynamic WAN IP updates                       |
| NetBird    | Private remote connectivity and DNS delivery |

---

# Future Improvements

Potential future improvements include:

* Secondary recursive DNS
* Redundant Pi-hole/Unbound infrastructure
* Improved DNS monitoring
* Dedicated DNS/network VLAN
* More detailed DNS performance monitoring
* Automated configuration backups

These features should only be documented as deployed after they have been implemented and tested.
