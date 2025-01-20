#!/bin/bash

# Variables
ANSIBLE_PROJECT_NAME="ansible"
DOCKER_COMPOSE_DIR="./docker-compose-files"
ANSIBLE_INVENTORY_DIR="$ANSIBLE_PROJECT_NAME/inventories"
ANSIBLE_ROLES_DIR="$ANSIBLE_PROJECT_NAME/roles"
ANSIBLE_PLAYBOOKS_DIR="$ANSIBLE_PROJECT_NAME/playbooks"

# Create the base Ansible structure
echo "Creating Ansible project directory structure..."
mkdir -p "$ANSIBLE_ROLES_DIR"
mkdir -p "$ANSIBLE_PLAYBOOKS_DIR"
mkdir -p "${ANSIBLE_INVENTORY_DIR}/production/group_vars"
mkdir -p "${ANSIBLE_INVENTORY_DIR}/development/group_vars"

# Create ansible.cfg
echo "Creating ansible.cfg..."
cat > "$ANSIBLE_PROJECT_NAME/ansible.cfg" <<EOL
[defaults]
inventory = inventories/production
roles_path = roles
EOL

# Create inventory files
echo "Creating inventory files..."
cat > "${ANSIBLE_INVENTORY_DIR}/production/hosts" <<EOL
[servers]
example-host ansible_host=192.168.1.10 ansible_user=root
EOL

cat > "${ANSIBLE_INVENTORY_DIR}/development/hosts" <<EOL
[servers]
localhost ansible_connection=local
EOL

# Create the main playbook
echo "Creating main playbook..."
cat > "$ANSIBLE_PLAYBOOKS_DIR/main.yml" <<EOL
- hosts: all
  become: yes
  roles:
EOL

# Install Docker role (common setup for all services)
mkdir -p "$ANSIBLE_ROLES_DIR/docker-setup/tasks"
cat > "$ANSIBLE_ROLES_DIR/docker-setup/tasks/main.yml" <<EOL
- name: Install Docker
  ansible.builtin.package:
    name: docker.io
    state: present

EOL

# Add the Docker setup role to the main playbook
sed -i 's/roles:/roles:\n    - role: docker-setup/' "$ANSIBLE_PLAYBOOKS_DIR/main.yml"

# Generate roles for each Docker Compose service
echo "Generating roles for Docker Compose files..."
for COMPOSE_FOLDER in "$DOCKER_COMPOSE_DIR"/*/; do
    # Extract the service name from the compose file name
    COMPOSE_FILE="${COMPOSE_FOLDER}docker-compose.yml"

    SERVICE_NAME=$(basename "${COMPOSE_FOLDER}")
    ROLE_DIR="$ANSIBLE_ROLES_DIR/docker-compose-$SERVICE_NAME"

    # Create the role structure
    mkdir -p "$ROLE_DIR/tasks"
    mkdir -p "$ROLE_DIR/files"
    mkdir -p "$ROLE_DIR/defaults"

    # Copy the Docker Compose file into the role
    cp "$COMPOSE_FILE" "$ROLE_DIR/files/docker-compose.yml"

    if [ -f "${COMPOSE_FOLDER}.env" ] ; then
      cp "${COMPOSE_FOLDER}.env" "$ROLE_DIR/files/.env"
    fi

    # Create the main tasks file for the role
    cat > "$ROLE_DIR/tasks/main.yml" <<EOL
- name: Create a directory for the $SERVICE_NAME service
  ansible.builtin.file:
    path: /opt/$URI/$SERVICE_NAME
    state: directory

- name: Copy docker-compose.yml to target host
  ansible.builtin.copy:
    src: docker-compose.yml
    dest: /opt/$URI/$SERVICE_NAME/docker-compose.yml
  register: docker_compose_yaml

- name: Start the $SERVICE_NAME service with Docker Compose
  ansible.builtin.command:
    cmd: docker compose up -d
    chdir: /opt/$URI/$SERVICE_NAME

- name: Pull on change
  when: docker_compose_yaml.changed
  command:
    chdir: /opt/monitoring-stack
    cmd: docker compose pull

- name: Restart on change
  when: docker_compose_yaml.changed
  command:
    chdir: /opt/monitoring-stack
    cmd: docker compose restart
EOL

    # Add service variables to defaults (optional)
    cat > "$ROLE_DIR/defaults/main.yml" <<EOL
service_name: $SERVICE_NAME
uri: $SERVICE_NAME.triantium.de
EOL

    # Add the role to the main playbook
    sed -i "s/roles:/roles:\n    - role: docker-compose-$SERVICE_NAME/" "$ANSIBLE_PLAYBOOKS_DIR/main.yml"
done

echo "Ansible project structure created successfully in $ANSIBLE_PROJECT_NAME!"
