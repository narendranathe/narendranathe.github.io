# Substack RSS Proxy (Cloudflare Worker)

Stateless edge proxy that fetches `https://narendranathe.substack.com/feed`
and returns the raw RSS XML. Exists because Substack/Cloudflare returns
HTTP 403 to GitHub-hosted runner egress IPs, silently breaking the every-4h
`substack-snapshot` workflow. See [issue #98](https://github.com/narendranathe/narendranathe.github.io/issues/98).

The Worker:
- Sends a real Chrome User-Agent + standard `Accept` / `Accept-Language` headers
- Returns `Content-Type: application/rss+xml; charset=utf-8`
- Caches for 15 minutes (`Cache-Control: public, max-age=900`)
- Passes upstream non-200s through as real errors (no fake successes)

Free-tier safe: 100k requests/day on Cloudflare Workers free plan; this
endpoint is hit ~6 times/day by the cron, well under the limit.

## Deploy

One-time setup:

```bash
npm install -g wrangler
wrangler login        # opens browser, authenticates against your Cloudflare account
```

Deploy from this directory:

```bash
cd infra/substack-proxy
wrangler deploy
```

Wrangler will print the deployed URL, of the form:

```
https://substack-proxy.<account-subdomain>.workers.dev
```

## Wire into the snapshot workflow

The Python script (`scripts/snap-substack-feed.py`) reads an env var
`SUBSTACK_FEED_URL` and falls back to the hardcoded Substack URL when unset
(so local runs from a residential IP keep working unchanged).

The GitHub Actions workflow (`.github/workflows/substack-snapshot.yml`) reads
the same env var from a **repository Variable** named `SUBSTACK_FEED_URL`.

To wire it up after deploy:

1. Go to the repo on GitHub: **Settings → Secrets and variables → Actions → Variables tab → New repository variable**
2. Name: `SUBSTACK_FEED_URL`
3. Value: `https://substack-proxy.<account-subdomain>.workers.dev/feed`
4. Save. Next scheduled run (or a manual `workflow_dispatch`) will route through the Worker.

## Verify

Hit the deployed URL from your browser or curl. You should get RSS XML and a
`200 OK`. If you get a JSON error body with a non-200 status, the upstream
returned an error — the Worker surfaces it instead of silently swallowing it.

```bash
curl -i https://substack-proxy.<account-subdomain>.workers.dev/feed | head -20
```
