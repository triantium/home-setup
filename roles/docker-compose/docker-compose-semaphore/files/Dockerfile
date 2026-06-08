FROM semaphoreui/semaphore:v2.18.10

USER root
RUN apk add --no-cache pass gnupg bind-tools

COPY --chown=1001:1001 semaphore-init.sh /home/semaphore/semaphore-init.sh
RUN chmod +x /home/semaphore/semaphore-init.sh

ENV PASSWORD_STORE_DIR="/home/semaphore/.password-store"

USER 1001
CMD ["/home/semaphore/semaphore-init.sh"]
