# home-setup

# On the qnap host
cd /opt/triantium.ddns.net/miniflux
docker compose exec postgres-internal pg_dump -U gitea gitea > /tmp/gitea.sql
# Then run the playbook (creates the central user/db)
ansible-playbook playbooks/production.yaml --tags miniflux
# Restore into central postgres
docker compose run --rm --network postgres-net \
-e PGPASSWORD=<central_postgres_admin_pw> \
postgres:18 psql -h postgres -U postgres -d miniflux < /tmp/miniflux.sql
