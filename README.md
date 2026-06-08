# home-setup

Ansible-based infrastructure-as-code for a personal home server environment. Deploys
and manages Docker-based self-hosted services across Raspberry Pis, a QNAP NAS, and
other Linux hosts.

## Prerequisites

- **Ansible** >= 2.14 (`pip install ansible`)
- **pass** (passwordstore.org) with a GPG key for secret management
- **Tailscale** on all target hosts for secure connectivity
- **direnv** (optional, for auto-installing Galaxy roles)

## Getting Started

```bash
# 1. Clone the repository
git clone git@github.com:triantium/home-setup.git
cd home-setup

# 2. Install Ansible Galaxy role dependencies
ansible-galaxy role install --role-file requirements.yml

# 3. Set up the password store
#    The project uses `pass` to retrieve host credentials and service secrets.
#    Clone or create your password store and point PASSWORD_STORE_DIR to it:
export PASSWORD_STORE_DIR=/path/to/your/passwordstore

# 4. Verify connectivity to your hosts (all must be on the same Tailscale network)
ansible all -i inventories/production -m ping

# 5. Run a playbook
ansible-playbook playbooks/production.yaml
```

> **Note:** If you have `direnv` installed, entering the project directory will
> automatically install missing Galaxy roles (see `.envrc`).

## Project Structure

```
├── ansible.cfg                  # Ansible config: inventory, roles_path
├── inventories/                 # Host inventories
│   ├── development/             #   Dev hosts (berserker, gloin, heimdall, ...)
│   └── production/              #   Production hosts (pi, divera, octoprint, qnap)
├── playbooks/                   # Ansible playbooks
│   ├── production.yaml          #   Full production deployment
│   ├── development.yaml         #   Dev deployment (keycloak, vector)
│   ├── semaphore.yaml           #   Deploy Semaphore Ansible UI on QNAP
│   └── upgrade.yaml             #   Simple apt upgrade for pi/divera
├── roles/                       # Ansible roles
│   ├── common-setup/            #   Base server provisioning
│   ├── docker-setup/            #   Docker engine installation
│   ├── docker-compose-*/        #   Service-specific Docker Compose deployments
│   ├── docker-volumes-backup/   #   restic/autorestic backup of Docker volumes
│   ├── divera/                  #   Divera 247 emergency alert monitor
│   └── octoprint/               #   OctoPrint 3D printer management
├── templates/autorestic/        # Backup config templates
├── renovate.json                # Automated Docker image updates
└── .pre-commit-config.yaml      # Linting & secrets scanning hooks
```

## Inventories

| Group     | Hosts                                   | Description                    |
|-----------|-----------------------------------------|--------------------------------|
| `pi`      | `heimdall`, `gloin`                     | Raspberry Pi 4/5 nodes         |
| `divera`  | `display-02`                            | Divera 247 display machine     |
| `octoprint` | `octopi`                              | OctoPrint 3D printer controller |
| `qnap`    | `nas`                                   | QNAP NAS (Container Station)   |

Host credentials and become passwords are stored in `pass` and looked up via the
`community.general.passwordstore` lookup plugin.

## Roles

### Infrastructure

| Role | Description |
|------|-------------|
| **common-setup** | Base provisioning: apt upgrades, installs tools (vim, git, restic, zsh, unattended-upgrades, node-exporter), creates `wheel`/`docker` groups, configures passwordless sudo, creates `triantium` and `semaphore` users, deploys SSH authorized keys. |
| **docker-setup** | Installs Docker engine (`docker.io`), loads required kernel modules (`overlay`, `br_netfilter`), enables and starts the Docker systemd service. |
| **geerlingguy.pip** | Community role — installs pip (Python package manager). |
| **geerlingguy.docker** | Community role — installs Docker CE. |

### Docker Compose Services

Each `docker-compose-*` role deploys a Docker Compose stack under `/opt/<domain>/<service>/`
(or `/opt/<service>/` for standalone services). All include a `docker-compose.yml` and
`.env` template with secrets sourced from the password store.

| Role | Service | Description |
|------|---------|-------------|
| **docker-compose-postgres** | PostgreSQL + pgAdmin | Central database server on shared `postgres-net` network. Other services connect to this for their database backend. Includes autorestic backups. |
| **docker-compose-traefik** | Traefik + whoami | Reverse proxy with Let's Encrypt ACME TLS certificates. |
| **docker-compose-gitea** | Gitea | Git service with PostgreSQL backend on central Postgres. Includes DB initialization and autorestic backups. |
| **docker-compose-keycloak** | Keycloak | Identity and access management with central PostgreSQL, SSL certificate mounts, health/metrics endpoints. |
| **docker-compose-home-assistant** | Home Assistant | Home automation platform using host networking for Bluetooth/Zigbee. |
| **docker-compose-pi-hole** | Pi-hole + Unbound | DNS ad-blocker with recursive DNS resolver and Prometheus exporter. Configured via API (session auth, gravity updates). |
| **docker-compose-paperless-ngx** | Paperless-ngx | Document management with Redis, Tika/Gotenberg document processing, internal PostgreSQL, Prometheus exporter, autorestic backups. |
| **docker-compose-jellyfin** | Jellyfin | Media server. |
| **docker-compose-navidrome** | Navidrome | Music streaming server with AI/ListenBrainz plugin downloads and Last.fm integration. |
| **docker-compose-minio** | MinIO | S3-compatible object storage. |
| **docker-compose-miniflux** | Miniflux | RSS reader with central PostgreSQL, autorestic backups. |
| **docker-compose-influxdb** | InfluxDB + Chronograf | Time-series monitoring stack (InfluxDB 2.x). |
| **docker-compose-mosquitto** | Mosquitto | MQTT broker with Prometheus exporter. |
| **docker-compose-moodle** | Moodle | LMS (Bitnami image) with MariaDB. |
| **docker-compose-minecraft** | Minecraft | Paper server (v1.21.1, hard difficulty). |
| **docker-compose-node-exporter** | Node Exporter | Prometheus system metrics collector. |
| **docker-compose-vector** | Vector | Log aggregator for Docker container logs. |
| **docker-compose-semaphore** | Semaphore | Ansible web UI with custom Docker image including pass/gnupg for password store integration. Includes GPG key generation, SSH key setup, Tailscale sidecar, and API-based project configuration. |

### Specialty Roles

| Role | Description |
|------|-------------|
| **divera** | Deploys Divera 247 emergency alert monitor on dedicated display machines. Creates `monitor` user with auto-login, installs dependencies (libfuse2, dbus, VLC, xdotool), downloads the Divera AppImage, sets up DBus notification services. |
| **octoprint** | Deploys OctoPrint + Spoolman for 3D printer management with autorestic backups. |
| **docker-volumes-backup** | Deploys an autorestic container that backs up all Docker volumes to a restic/BorgBase backend. Configured via `templates/autorestic/`. |

## Playbooks

| Playbook | Target | Roles |
|----------|--------|-------|
| `production.yaml` | pi, divera, qnap, heimdall | Full production deployment: common-setup, pip, docker plus all services. |
| `development.yaml` | gloin | Development deployment (keycloak, vector). |
| `semaphore.yaml` | qnap | Deploys the Semaphore Ansible UI. |
| `upgrade.yaml` | pi, divera | Simple `apt upgrade` run. |

## Backup Strategy

Docker volume backups are handled by **autorestic** (a wrapper around restic).
The `docker-volumes-backup` role deploys a container that periodically backs up
`/var/lib/docker/volumes` to a restic remote repository. Service-specific roles
(e.g., gitea, paperless, postgres, miniflux) also include additional backup
configurations for their data directories.

Backup configuration is templated from `templates/autorestic/config.yml.j2`.

## Secrets Management

All secrets (host passwords, database credentials, API tokens, admin passwords)
are stored in a **pass** password store and referenced via the
`community.general.passwordstore` Ansible lookup plugin:

```yaml
ansible_become_password: "{{ lookup('community.general.passwordstore', 'hosts/heimdall/login') }}"
```

The `docker-compose-semaphore` role extends this by including `pass` and `gnupg`
inside the Semaphore container, allowing playbook runs from the web UI to
seamlessly resolve password store lookups.

## Development

### Linting & Pre-commit

This project uses [pre-commit](https://pre-commit.com/) hooks for code quality:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Hooks configured: YAML linting, trailing whitespace fixes, end-of-file fixing,
Gitleaks secrets scanning, EditorConfig validation.

### Automated Dependency Updates

Docker images and dependencies are updated automatically via
[Renovate](https://docs.renovatebot.com/). Configuration is in `renovate.json`.
Postgres major version updates require manual review.
