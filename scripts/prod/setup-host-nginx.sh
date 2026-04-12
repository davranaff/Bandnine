#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env.prod}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/docker-compose.prod.yml}"
NGINX_CONF_PATH="${NGINX_CONF_PATH:-/etc/nginx/conf.d/bandnine.conf}"

ROOT_DOMAIN="${ROOT_DOMAIN:-bandnine.online}"
FRONT_DOMAIN="${FRONT_DOMAIN:-ilets.bandnine.online}"
API_DOMAIN="${API_DOMAIN:-api.bandnine.online}"

SYNC_ENV=1
WITH_CERTBOT=0
CERTBOT_EMAIL="${CERTBOT_EMAIL:-}"

usage() {
  cat <<USAGE
Usage: $(basename "$0") [options]

Options:
  --env-file <path>         Path to .env.prod (default: $ROOT_DIR/.env.prod)
  --compose-file <path>     Path to docker-compose.prod.yml
  --nginx-conf <path>       Nginx conf path (default: /etc/nginx/conf.d/bandnine.conf)

  --root-domain <domain>    Landing domain (default: bandnine.online)
  --front-domain <domain>   Frontend domain (default: ilets.bandnine.online)
  --api-domain <domain>     API domain (default: api.bandnine.online)

  --no-env-sync             Do not rewrite .env.prod and rebuild docker services
  --with-certbot            Run certbot after nginx reload
  --certbot-email <email>   Email for certbot (required with --with-certbot)

  -h, --help                Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    --compose-file)
      COMPOSE_FILE="$2"
      shift 2
      ;;
    --nginx-conf)
      NGINX_CONF_PATH="$2"
      shift 2
      ;;
    --root-domain)
      ROOT_DOMAIN="$2"
      shift 2
      ;;
    --front-domain)
      FRONT_DOMAIN="$2"
      shift 2
      ;;
    --api-domain)
      API_DOMAIN="$2"
      shift 2
      ;;
    --no-env-sync)
      SYNC_ENV=0
      shift
      ;;
    --with-certbot)
      WITH_CERTBOT=1
      shift
      ;;
    --certbot-email)
      CERTBOT_EMAIL="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown option '$1'" >&2
      usage
      exit 1
      ;;
  esac
done

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: required command not found: $cmd" >&2
    exit 1
  fi
}

validate_port() {
  local name="$1"
  local value="$2"

  if ! [[ "$value" =~ ^[0-9]+$ ]]; then
    echo "Error: $name must be a number, got '$value'" >&2
    exit 1
  fi

  if (( value < 1 || value > 65535 )); then
    echo "Error: $name must be in range 1..65535, got '$value'" >&2
    exit 1
  fi
}

upsert_env_key() {
  local file="$1"
  local key="$2"
  local value="$3"
  local tmp

  tmp="$(mktemp)"
  awk -v key="$key" -v value="$value" '
    BEGIN { updated = 0 }
    $0 ~ "^" key "=" {
      print key "=" value
      updated = 1
      next
    }
    { print }
    END {
      if (updated == 0) {
        print key "=" value
      }
    }
  ' "$file" > "$tmp"

  mv "$tmp" "$file"
}

compose() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Error: run as root (for /etc/nginx and nginx reload), e.g. sudo $0" >&2
  exit 1
fi

require_cmd nginx
require_cmd docker

if (( WITH_CERTBOT == 1 )); then
  require_cmd certbot
  if [[ -z "$CERTBOT_EMAIL" ]]; then
    echo "Error: --certbot-email is required with --with-certbot" >&2
    exit 1
  fi
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: env file not found: $ENV_FILE" >&2
  exit 1
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Error: compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "$ENV_FILE"
set +a

API_PORT="${API_PORT:-18000}"
FRONTEND_PORT="${FRONTEND_PORT:-30000}"
LANDING_PORT="${LANDING_PORT:-31000}"

validate_port "API_PORT" "$API_PORT"
validate_port "FRONTEND_PORT" "$FRONTEND_PORT"
validate_port "LANDING_PORT" "$LANDING_PORT"

if (( SYNC_ENV == 1 )); then
  echo "[nginx-setup] Syncing .env.prod for host nginx TLS on :443..."
  upsert_env_key "$ENV_FILE" "PROD_FRONTEND_API_ORIGIN" "https://${API_DOMAIN}"
  upsert_env_key "$ENV_FILE" "FRONTEND_BASE_URL" "https://${FRONT_DOMAIN}"
  upsert_env_key "$ENV_FILE" "CORS_ALLOW_ORIGINS" "https://${FRONT_DOMAIN},https://${ROOT_DOMAIN}"

  echo "[nginx-setup] Rebuilding app services with updated env..."
  compose config -q
  compose up -d --build --remove-orphans api worker frontend landing
  compose stop caddy >/dev/null 2>&1 || true
fi

if [[ -f "$NGINX_CONF_PATH" ]]; then
  cp "$NGINX_CONF_PATH" "${NGINX_CONF_PATH}.bak.$(date +%Y%m%d%H%M%S)"
fi

cat > "$NGINX_CONF_PATH" <<EOF_CONF
map \$http_upgrade \$bandnine_connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    listen [::]:80;
    server_name ${ROOT_DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:${LANDING_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name ${FRONT_DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:${FRONTEND_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name ${API_DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:${API_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \$bandnine_connection_upgrade;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF_CONF

echo "[nginx-setup] Testing nginx config..."
nginx -t

echo "[nginx-setup] Reloading nginx..."
if command -v systemctl >/dev/null 2>&1; then
  systemctl reload nginx
else
  nginx -s reload
fi

if (( WITH_CERTBOT == 1 )); then
  echo "[nginx-setup] Requesting SSL certificates via certbot..."
  certbot --nginx \
    --non-interactive \
    --agree-tos \
    --email "$CERTBOT_EMAIL" \
    --redirect \
    -d "$ROOT_DOMAIN" \
    -d "$FRONT_DOMAIN" \
    -d "$API_DOMAIN"
fi

echo "[nginx-setup] Done."
echo "  landing:  https://${ROOT_DOMAIN}"
echo "  frontend: https://${FRONT_DOMAIN}"
echo "  api:      https://${API_DOMAIN}/health"
