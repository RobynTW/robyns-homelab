# Homelab TODO

## Priority 1 — Monitoring Expansion

* [ ] Add any remaining VM108/Pterodactyl resource coverage to Beszel
* [ ] Add/verify Wings monitoring coverage as needed
* [ ] Add storage/NFS health monitoring
* [ ] Add Docker/container monitoring where useful
* [ ] Expand Uptime Kuma coverage where useful
* [ ] Configure useful resource/availability alerts
* [ ] Verify alerts actually trigger correctly

## Priority 2 — Firewall Hardening

* [ ] Document required network flows before applying firewall rules
* [ ] Harden VM108 with nftables
* [ ] Account for Docker networking
* [ ] Allow required NFS, Panel, Wings, and NetBird traffic
* [ ] Preserve Minecraft DNAT traffic through `wt0`
* [ ] Restrict unnecessary inbound traffic
* [ ] Test LAN and NetBird access after firewall changes

## Priority 3 — Remaining Service Configuration & Cleanup

* [ ] Review all deployed services for incomplete configuration
* [ ] Review Jellyfin, Pterodactyl, NetBird, Nginx, Certbot, and DDNS
* [ ] Review systemd services/timers and Docker Compose configurations
* [ ] Verify storage ownership/permissions
* [ ] Review documented hostnames, IPs, and listening ports
* [ ] Remove temporary troubleshooting configuration
* [ ] Perform a general consistency pass

## Priority 4 — Backups

* [ ] Define backup requirements
* [ ] Identify critical configuration/data
* [ ] Configure automated backups
* [ ] Back up Proxmox, Pterodactyl, media-stack, and Homepage configuration
* [ ] Verify backup integrity
* [ ] Perform a test restore

## Priority 5 — Stability

* [ ] Run without major architectural changes
* [ ] Monitor for recurring failures
* [ ] Fix reliability issues as they appear
* [ ] Confirm services and backups remain operational over an extended period

## Priority 6 — Final Architecture

* [ ] Confirm final topology
* [ ] Rebuild architecture diagram
* [ ] Update README and relevant documentation
* [ ] Mark the homelab baseline as stable

## Completed — Homepage

* [x] Deploy Homepage on CT107
* [x] Configure service groups
* [x] Add Proxmox resource widgets
* [x] Add Beszel and Uptime Kuma integration
* [x] Add direct GitHub repository widget
* [x] Remove redundant Developer/GitHub bookmark
* [x] Add custom background
* [x] Add glass-style service cards
* [x] Tune service group layout
* [x] Make GitHub icon monochrome/theme styled
* [x] Move GitHub widget to the right side of the top widget bar
* [x] Document Homepage
* [x] Update AI continuity documentation
