# AGENTS.md

Ansible infrastructure-as-code for a personal home lab. There is no application
code; changes are YAML/Jinja roles and playbooks. Production targets Tailscale
hostnames: most Docker Compose services run on the QNAP NAS (`nas.fritz.box`,
group `qnap`); monitoring/nginx/homer/meshtastic/restic exporter run on `gloin`.
`README.md` is a useful overview, but its role/service tables are stale. Trust
`playbooks/deployments/` and `roles/docker-compose/` for what is actually deployed.

## Setup

- `ansible-galaxy role install -r requirements.yml` installs the pinned
  `geerlingguy.*` roles into `roles/` because `ansible.cfg` sets
  `roles_path = roles`. Do not edit those vendored roles.
- The `community.general` and `ansible.posix` collections are required
  (`passwordstore` lookups, `authorized_key`) but are not listed in
  `requirements.yml`; make sure they are installed.
- All host credentials and service secrets are `pass` lookups. Set
  `PASSWORD_STORE_DIR` and have the GPG key unlocked, or inventory parsing fails.
- Some lookups use `missing='create'`, and several playbooks run
  `pass git pull` / `pass git push`. Playbook runs can therefore create secrets
  and modify/push the password store.
- `.envrc` exports `RESTIC_*` values from `pass`; its Galaxy check looks at the
  old `playbooks/roles/` path, so direnv may reinstall roles on every entry.

## Commands

- CI/lint: `pre-commit run --all-files`. CI only runs pre-commit
  (`check-yaml`, whitespace/EOF fixes, gitleaks, editorconfig); `ansible-lint`
  and checkov hooks are commented out. Do not assume CI runs ansible-lint.
- `ansible.cfg` defaults to `inventories/development`, so production runs need
  an explicit inventory:

  ```bash
  ansible-playbook -i inventories/production/production.yaml playbooks/production.yaml
  ansible-playbook -i inventories/production/production.yaml playbooks/deployments/10_gitea.yaml --limit qnap
  ```

- Useful non-mutating checks:
  `ansible-inventory -i inventories/production/production.yaml --graph` and
  `ansible-playbook -i inventories/production/production.yaml --syntax-check playbooks/...`.
- There is no test suite or Molecule setup for this repo's roles. Real
  verification requires a playbook run against a host.

## Deployment model

- `playbooks/production.yaml` imports `deployments/NN_*.yaml` in numeric order.
  `00_setup.yaml` provisions common packages/Docker/Vector; `01_postgres.yaml`
  must run before services that use central Postgres.
- To add a service: create `roles/docker-compose/<name>/` following the existing
  pattern (`defaults/main.yml`, `files/docker-compose.yml` or
  `templates/docker-compose.yml.j2`, `templates/env.j2`, `tasks/main.yml`), add
  `playbooks/deployments/NN_<name>.yaml`, and import it in `production.yaml`.
- Compose stacks are written under `/opt/<domain>/<service>` (or a role-specific
  data dir). Invoke Docker as `{{ docker_cli }} compose ...`; QNAP uses a custom
  binary and sets `ansible_become: false` plus a custom Python interpreter.
  Never hardcode `/usr/bin/docker`.
- Services using central Postgres join the external `postgres-net` network,
  created by the postgres role. Database/user creation tasks tolerate duplicates.
- Follow the existing `passwordstore` defaults and `templates/env.j2` pattern;
  never put plaintext secrets in compose files. `shared_templates_dir` points to
  the shared `templates/` tree (notably `templates/autorestic/`).
- Backups use autorestic/restic to BorgBase. Service roles set
  `autorestic_location_name` and derive a stable randomized cron from
  `inventory_hostname` + `service_name`.

## Gotchas

- `docker compose restart` does not apply changed `.env` values; recreate with
  `{{ docker_cli }} compose up -d` (also noted in `TODO.md`). Some existing
  roles still use `restart` after template changes.
- The enabled `ansible_metrics` callback pushes to
  `http://gloin.taila24d4b.ts.net:9091` after every run. Failures are warnings;
  set `ANSIBLE_PUSHGATEWAY_URL` if the pushgateway is unreachable.
- YAML is 2-space indented, LF, final newline (`.editorconfig`). Pre-commit
  handles whitespace/EOF fixes.
- Do not casually "fix" inventory quirks: `display-02` currently references the
  `hosts/display-01` pass entry, some netcup lookup keys have leading spaces,
  and QNAP intentionally uses custom interpreter/become/Docker settings.
