# Homelab TODO

## Priority 1 — Homarr

* [ ] Deploy Homarr on VM107
* [ ] Configure Homarr for the current homelab services
* [ ] Add links for commonly used services
* [ ] Add useful service/status information
* [ ] Configure authentication/access appropriately
* [ ] Verify access from LAN
* [ ] Verify access through NetBird
* [ ] Document the final Homarr deployment

---

## Priority 2 — Cleanup & Consolidation

* [ ] Clean up README typo
* [ ] Review README against the deployed topology
* [ ] Review `docs/00–15` for outdated or planned-state wording
* [ ] Verify Pterodactyl documentation reflects Panel + Wings deployment
* [ ] Verify NetBird documentation reflects the current routing and DNS configuration
* [ ] Verify NFS documentation reflects the final per-share exports
* [ ] Remove temporary NFS/Pterodactyl test files
* [ ] Review old troubleshooting remnants
* [ ] Remove unnecessary packages and services
* [ ] Review systemd services and timers
* [ ] Review Docker Compose configurations
* [ ] Verify shared-storage ownership and permissions
* [ ] Verify documented hostnames and IP addresses
* [ ] Review currently listening/exposed ports
* [ ] Remove temporary troubleshooting configuration
* [ ] Perform a general configuration/documentation consistency pass

---

## Priority 3 — Monitoring Expansion

* [ ] Add VM108/Pterodactyl to Beszel
* [ ] Add Wings monitoring
* [ ] Add storage monitoring
* [ ] Add Docker/container monitoring
* [ ] Expand Uptime Kuma service coverage
* [ ] Configure useful availability checks
* [ ] Configure useful resource alerts
* [ ] Verify alerts actually trigger correctly

---

## Priority 4 — Firewall Hardening

* [ ] Document required network flows before applying firewall rules
* [ ] Harden VM108 with nftables
* [ ] Account for Docker networking
* [ ] Allow required NFS traffic
* [ ] Allow required Panel/Wings traffic
* [ ] Allow required NetBird traffic
* [ ] Restrict unnecessary inbound traffic
* [ ] Review firewall rules on other hosts
* [ ] Test LAN access after firewall changes
* [ ] Test NetBird access after firewall changes
* [ ] Verify Pterodactyl game-server networking

---

## Priority 5 — Remaining Service Configuration

* [ ] Review all deployed services for incomplete configuration
* [ ] Finish any remaining media-stack configuration
* [ ] Review Jellyfin configuration
* [ ] Review Pterodactyl configuration
* [ ] Review NetBird configuration
* [ ] Review Nginx reverse-proxy configuration
* [ ] Review Certbot renewal configuration
* [ ] Review DDNS configuration
* [ ] Remove unnecessary configuration duplication
* [ ] Document any final configuration changes

---

## Priority 6 — Backups

* [ ] Define backup requirements
* [ ] Identify critical configuration/data
* [ ] Design backup destinations
* [ ] Configure automated backups
* [ ] Back up critical service configuration
* [ ] Back up Proxmox configuration
* [ ] Back up Pterodactyl configuration
* [ ] Back up media-stack configuration
* [ ] Verify backup integrity
* [ ] Perform a test restore

---

## Priority 7 — Stability

* [ ] Run the completed homelab without major architectural changes
* [ ] Monitor for recurring failures
* [ ] Fix reliability issues as they appear
* [ ] Avoid unnecessary infrastructure changes
* [ ] Confirm services remain operational over an extended period
* [ ] Confirm backups and monitoring continue working

---

## Priority 8 — Final Architecture

* [ ] Confirm final infrastructure topology
* [ ] Rebuild the architecture diagram
* [ ] Update README architecture section
* [ ] Update relevant documentation
* [ ] Perform final documentation review
* [ ] Mark the homelab baseline as stable
