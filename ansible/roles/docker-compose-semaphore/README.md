# Semaphore Passwordstore Integration

Semaphore runs Ansible playbooks that use `community.general.passwordstore` lookups
to retrieve secrets from a `pass` password store. By default the upstream
`semaphoreui/semaphore` image does not include `pass` or `gpg`, so those lookups
would fail inside the container.

## Approach

A custom Docker image (`semaphore-custom:latest`) is built on the target host
that extends the upstream image with `pass` and `gnupg` installed. At container
start, an init script imports a dedicated GPG key and marks it as ultimately
trusted, enabling pass to decrypt the store without interaction.

The password store is cloned from its git remote onto the target host, and the
semaphore GPG private key is copied from the control node. Both are mounted
read-only into the container.

## GPG key

A dedicated GPG key (`semaphore@semaphore.<domain>`) is generated on the control
node if it does not already exist. The key uses RSA 4096 with no passphrase
(required for unattended decryption in the container). The public key is added
as a recipient to the password store via `pass init`, which re-encrypts all
stored passwords so they can be decrypted by any of the existing keys plus the
new semaphore key.

After the key is added, `pass git push` pushes the updated store to its git
remote so the change is persisted.

## Sync to target

The password store is cloned directly from its git remote onto the target host
using the `ansible.builtin.git` module. This replaces the previous approach of
archiving and transferring the store on every playbook run.

The target host must have SSH access to the password store git remote (the URL
is obtained from the control node's `~/.password-store` git config). Ensure the
target's SSH key is authorized on the git server, or use a deploy key. On
subsequent runs, the repo is updated via `git fetch` with `force: yes` to match
the remote.

## Container setup

| Volume | Mount point | Purpose |
|--------|-------------|---------|
| `/opt/<domain>/semaphore/.password-store` | `/home/semaphore/.password-store:ro` | Encrypted password files |
| `/opt/<domain>/semaphore/gpg/semaphore-private.key` | `/etc/semaphore/gpg/semaphore-private.key:ro` | GPG private key for decryption |

The `PASSWORD_STORE_DIR` environment variable is set so `pass` knows where to
look.

## Security notes

- The GPG private key has no passphrase. Anyone with access to the target host
  filesystem or the running container can decrypt the password store. This is an
  accepted trade-off for automated operation inside a trusted network.
- The password store is mounted read-only inside the container. Semaphore can
  read passwords but cannot modify the store.
- The GPG key is generated on the control node and transferred to the target.
  Consider generating it on the target instead if stricter key hygiene is
  desired.
