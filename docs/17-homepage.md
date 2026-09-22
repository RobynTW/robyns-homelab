# Homepage Dashboard

Homepage is the current central dashboard for the homelab. It replaced the previous plan to deploy Homarr on VMID 107.

## Deployment

```text
VMID:       107
Type:       LXC
Hostname:   homepage
Host:       pve-1
IP:         192.168.20.92
OS:         Debian 13
Runtime:    Docker
Homepage:   2.4.0
```

Primary directory: `/opt/homepage`

Compose file: `/opt/homepage/docker-compose.yml`

Homepage listens on `192.168.20.92:3000`.

## Reverse Proxy

```text
homepage.robynshomelab.dev
  ↓
CT106 Nginx
192.168.20.94
  ↓
CT107 Homepage
192.168.20.92:3000
```

Pi-hole split DNS points `homepage.robynshomelab.dev` to `192.168.20.94`.

No router port forwarding is used.

## Docker Compose

File: `/opt/homepage/docker-compose.yml`

Important mounts:

```text
/opt/homepage/config:/app/config
/opt/homepage/images:/app/public/images
/var/run/docker.sock:/var/run/docker.sock:ro
/mnt/homelab-data:/mnt/homelab-data:ro
```

The image mount was added so Homepage can load the local background image.

Changing Homepage YAML/CSS/JS normally does not require a Docker restart. Changing the Compose file itself, such as adding a volume mount, does require recreating the container.

## Background

Local image:

`/opt/homepage/images/homepage-background.jpg`

Settings file:

`/opt/homepage/config/settings.yaml`

Relevant configuration:

```yaml
background:
  image: /images/homepage-background.jpg
  blur: sm
  saturate: 80
  brightness: 50
  opacity: 70

iconStyle: theme
```

The `iconStyle: theme` setting makes prefixed icons such as GitHub monochrome/theme styled instead of multicolour.

## Top Information Widgets

File: `/opt/homepage/config/widgets.yaml`

Current resources:

```yaml
---
- resources:
    label: System
    cpu: true
    memory: true

- resources:
    label: Storage
    disk:
      - /
      - /mnt/homelab-data
```

The native resource labels still use Homepage's `Free` terminology for RAM/disk. This was intentionally left alone rather than adding more DOM/CSS manipulation.

### GitHub

The top bar also contains:

```yaml
- logo:
    icon: si-github
    href: https://github.com/RobynTW/robyns-homelab
    target: _blank
```

The old Developer/GitHub bookmark was removed because it duplicated this widget and consumed dashboard space.

Custom CSS moves the GitHub widget to the right side of the top information bar by targeting the actual Homepage DOM:

```text
#information-widgets
└── #widgets-wrap
    ├── resource widgets
    ├── .information-widget-logo
    └── #information-widgets-right
```

The final CSS hides the empty `#information-widgets-right` container and applies `margin-left: auto` to `.information-widget-logo`.

## Service Layout

File: `/opt/homepage/config/services.yaml`

Current groups:

```text
Infrastructure
Network
Media
Gaming
Monitoring
```

Desktop arrangement:

```text
Infrastructure  | Media | Gaming
Network         |       | Monitoring
```

Network is manually positioned beneath Infrastructure.

Gaming and Monitoring occupy the third column, with Monitoring offset beneath Gaming.

The exact Network vertical offset is user-tuned and should not be overwritten casually.

## Service Card Styling

File: `/opt/homepage/config/custom.css`

The current design includes:

- Three-column desktop layout.
- Responsive tablet/mobile layouts.
- Larger service-group headings.
- Semi-transparent dark glass cards.
- Light borders.
- Backdrop blur.
- Subtle shadows.
- Rounded corners.
- Desktop hover lift.
- Reduced-motion handling.
- Custom background presentation.
- GitHub right alignment.
- Bottom visual cap bar.

The cards were made less opaque to improve readability against the background.

The bottom cap is a cosmetic element. Its stacking was not further altered after attempts to keep the normal Homepage controls accessible.

## Custom JavaScript

File: `/opt/homepage/config/custom.js`

The script performs one delayed DOM pass and adds stable classes:

```text
Gaming     → service-group-gaming
Monitoring → service-group-monitoring
Network    → service-group-network
```

It intentionally contains no:

- MutationObserver
- recursion
- polling loop

An earlier broad MutationObserver implementation caused severe browser/PC lag and contributed to a browser crash. It was removed and must not be reintroduced for routine group styling.

## Proxmox Custom API Widgets

Native Glances service widgets were previously attempted for the Proxmox hosts but produced overlapping/error-prone presentation.

The final dashboard uses a small local Python API.

PVE-1:

`http://192.168.20.100:61209/stats`

PVE-2:

`http://192.168.20.101:61209/stats`

Each host runs:

`/usr/local/bin/homepage-stats.py`

and:

`/etc/systemd/system/homepage-stats.service`

Returned metrics:

- CPU
- RAM
- Swap
- Temperature
- Uptime
- Root filesystem usage
- PVE-2 storage usage

The systemd service is enabled and running on both Proxmox hosts.

## Monitoring Integration

### Beszel

Homepage links to:

`https://beszel.robynshomelab.dev`

Backend:

`http://192.168.20.96:8090`

Credentials are supplied through Homepage's environment configuration and are intentionally not documented.

### Uptime Kuma

Homepage links to the curated status page:

`https://status.robynshomelab.dev/status/homelab`

The internal Kuma backend is:

`http://192.168.20.95:3001`

Status-page slug:

`homelab`

## Files

```text
/opt/homepage/
├── docker-compose.yml
├── .env
├── config/
│   ├── settings.yaml
│   ├── widgets.yaml
│   ├── services.yaml
│   ├── bookmarks.yaml
│   ├── custom.js
│   └── custom.css
└── images/
    └── homepage-background.jpg
```

`.env` contains secrets and must not be committed.

## Desktop Editing Workflow

The Homepage configuration is edited from the Arch desktop using SSHFS:

```bash
mkdir -p ~/homelab/homepage
fusermount3 -u ~/homelab/homepage 2>/dev/null || true
sshfs root@192.168.20.92:/opt/homepage ~/homelab/homepage
cd ~/homelab/homepage
vscodium .
```

## Operational Rules

- Save YAML/CSS/JS changes and refresh the browser first.
- Do not restart Docker for ordinary Homepage configuration changes.
- Recreate the Compose service when changing the Compose file itself.
- Preserve the safe one-pass custom.js implementation.
- Preserve the manually tuned Network position.
- Keep the GitHub repository link in the top widget bar.
- Do not reintroduce the deleted Developer/GitHub bookmark unless the dashboard design changes.
- Never document Homepage credentials.
- Avoid broad DOM observers.

## Current Status

```text
Homepage deployment       DEPLOYED / VERIFIED
Background image          DEPLOYED / VERIFIED
Glass card styling        DEPLOYED / VERIFIED
Service group layout      DEPLOYED / VERIFIED
Proxmox custom widgets    DEPLOYED / VERIFIED
Beszel integration        DEPLOYED / VERIFIED
Uptime Kuma integration   DEPLOYED / VERIFIED
GitHub top widget         DEPLOYED / VERIFIED
GitHub monochrome styling DEPLOYED / VERIFIED
```

Homepage is considered operational and complete for the current dashboard phase.
