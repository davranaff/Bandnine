# Production Deployment (Backend + Frontend + Landing)

## 1) DNS records
Create these DNS records and point them to your server IP:

- `A bandnine.online -> <SERVER_IP>`
- `A ielts.bandnine.online -> <SERVER_IP>`
- `A api.bandnine.online -> <SERVER_IP>`

## 2) Open firewall ports
Allow inbound ports:

- `80/tcp` (for host nginx + certbot challenge)
- `443/tcp` (public HTTPS on domains)
- Optional direct service ports from `.env.prod` (`18000`, `30000`, `31000`, etc.)

## 3) Prepare env
From project root:

```bash
cp .env.prod.example .env.prod
```

Then edit `.env.prod` and set real secrets:

- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- SMTP credentials
- `OPENAI_API_KEY`

Also set build-time URLs:

- `PROD_FRONTEND_API_ORIGIN=https://api.bandnine.online`
- `PROD_LANDING_PLATFORM_URL=https://ielts.bandnine.online`

## 4) First deploy

```bash
./scripts/prod/deploy.sh
```

What this does:

- validates ports (must be `1..65535`)
- builds and starts all production containers
- applies Alembic migrations
- prints running services

## 5) Update deploy (pull + rebuild + migrate)

```bash
./scripts/prod/update.sh
```

Default branch is `main`. To use another branch:

```bash
BRANCH=develop ./scripts/prod/update.sh
```

## 6) Domains routing
Recommended: host nginx on `:443` with `scripts/prod/setup-host-nginx.sh`:

- `https://bandnine.online` -> landing
- `https://ielts.bandnine.online` -> frontend
- `https://api.bandnine.online` -> backend API

Run:

```bash
sudo ./scripts/prod/setup-host-nginx.sh --with-certbot --certbot-email you@example.com
```

## Notes about ports
Requested port style "add one zero" is kept where valid (for example `3000 -> 30000`).
`8000 -> 80000` is not possible because TCP max port is `65535`, so API defaults to `18000`.
You can change all ports in `.env.prod`.
