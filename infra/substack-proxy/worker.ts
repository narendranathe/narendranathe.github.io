// Substack RSS proxy — Cloudflare Worker.
//
// Why this exists:
// Substack/Cloudflare returns HTTP 403 to GitHub-hosted runner egress IPs,
// which silently breaks the every-4h `substack-snapshot` workflow. Confirmed
// IP-based block (same User-Agent from a residential IP returns 200), so a
// stateless edge proxy in front of the feed is the durable fix.
//
// Behavior:
// - Any path / method passes through; we always GET the upstream feed.
// - Sends a real Chrome User-Agent + standard Accept / Accept-Language
//   headers so Cloudflare's edge heuristics see a normal browser request.
// - On 2xx upstream: stream the raw RSS XML back with a 15-minute public
//   cache so repeated callers (workflow re-runs, debugging) hit cache.
// - On non-2xx upstream: pass the status through with a small JSON error
//   body so the calling workflow surfaces a real failure, not a fake 200.

const UPSTREAM = "https://narendranathe.substack.com/feed";

const BROWSER_HEADERS: HeadersInit = {
  "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
  "Accept":
    "text/html,application/xhtml+xml,application/xml;q=0.9," +
    "image/avif,image/webp,*/*;q=0.8",
  "Accept-Language": "en-US,en;q=0.9",
};

export default {
  async fetch(_request: Request): Promise<Response> {
    let upstream: Response;
    try {
      upstream = await fetch(UPSTREAM, {
        method: "GET",
        headers: BROWSER_HEADERS,
        redirect: "follow",
      });
    } catch (err) {
      return Response.json(
        { error: "upstream_fetch_failed", detail: String(err) },
        { status: 502 },
      );
    }

    if (!upstream.ok) {
      return Response.json(
        { error: "upstream_non_200", status: upstream.status },
        { status: upstream.status },
      );
    }

    const body = await upstream.text();
    return new Response(body, {
      status: 200,
      headers: {
        "Content-Type": "application/rss+xml; charset=utf-8",
        "Cache-Control": "public, max-age=900",
      },
    });
  },
};
