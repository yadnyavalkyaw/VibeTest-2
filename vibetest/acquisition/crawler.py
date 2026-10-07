"""Crawler. Katana discovery (soft dependency) + httpx fetching + JS bundle extraction.

Flow: consent-gated Katana discovery → fetch entry page + discovered pages (capped)
→ render JS-built pages in a headless browser when Playwright is installed
(see render.py) → download the app's own JS bundles → Artifact. If Katana or
Playwright are missing, the scan degrades gracefully and still produces an Artifact.
"""
from __future__ import annotations

import logging
import re
from urllib.parse import urljoin, urlsplit

import httpx

from ..core.context import ScanContext
from ..core.http_util import gated_get
from ..schemas.artifacts import Artifact, Endpoint, PageSnapshot
from . import fingerprint, katana, render
from .js_bundle import extract_bundles

logger = logging.getLogger(__name__)


def select_urls(entry_url: str, discovered: list[katana.DiscoveredURL], max_pages: int) -> list[str]:
    """Entry page first, then discovered URLs (deduped, capped). Pure — unit-tested."""
    urls = [entry_url]
    seen = {entry_url}
    for d in discovered:
        if len(urls) >= max_pages:
            break
        if d.url in seen:
            continue
        seen.add(d.url)
        urls.append(d.url)
    return urls


def _apply_rendering(pages: list[PageSnapshot], ctx: ScanContext) -> list[str]:
    """Render SPA-looking pages when Playwright is installed.

    Replaces raw shell HTML with the rendered DOM and returns the script URLs
    the browser observed (they feed bundle extraction). Pure side-effect-free
    when rendering is disabled or unavailable.
    """
    if not ctx.settings.render_spa:
        return []
    candidates = [p.url for p in pages if render.looks_like_spa(p)][: ctx.settings.max_render_pages]
    if not candidates:
        return []
    rendered = render.render_pages(candidates, gate=ctx.gate, settings=ctx.settings)
    extra_scripts: list[str] = []
    for page in pages:
        rendered_page = rendered.get(page.url)
        if rendered_page is None:
            continue
        page.html = rendered_page.html
        extra_scripts.extend(rendered_page.script_urls)
    return extra_scripts


_API_ROUTE_RE = re.compile(
    r"""["'`](/(?:api|rest/v1|v1|graphql)/[a-zA-Z0-9_\-\/]+)["'`]""",
    re.IGNORECASE,
)


def _extract_links(html: str, base_url: str) -> list[str]:
    """Extract same-origin links from HTML when Katana is unavailable."""
    base_parts = urlsplit(base_url)
    base_host = (base_parts.hostname or "").lower()
    links: list[str] = []
    seen: set[str] = set()
    for match in re.finditer(r"""href=["']([^"'#\s]+)["']""", html, re.IGNORECASE):
        href = match.group(1).strip()
        if href.startswith(("javascript:", "mailto:", "tel:", "data:", "#")):
            continue
        full_url = urljoin(base_url, href)
        parsed = urlsplit(full_url)
        if parsed.scheme in ("http", "https") and (parsed.hostname or "").lower() == base_host:
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if not any(clean_url.lower().endswith(ext) for ext in (
                ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".css", ".js", ".woff", ".woff2", ".ttf", ".webp", ".mp4", ".zip", ".pdf"
            )):
                if clean_url not in seen:
                    seen.add(clean_url)
                    links.append(clean_url)
    return links


def _extract_api_routes(content: str, base_url: str) -> list[str]:
    """Extract relative API routes referenced in JS bundles or HTML."""
    routes: list[str] = []
    seen: set[str] = set()
    base_prefix = base_url.rstrip("/")
    for match in _API_ROUTE_RE.finditer(content):
        path = match.group(1)
        full_url = f"{base_prefix}{path}"
        if full_url not in seen:
            seen.add(full_url)
            routes.append(full_url)
    return routes


def fetch(url: str, ctx: ScanContext) -> Artifact:
    """Discover URLs (Katana or link spidering), fetch each page, then download the app's JS bundles."""
    discovered = katana.discover(url, ctx)
    errors: list[str] = []
    pages: list[PageSnapshot] = []

    max_pages = max(1, ctx.settings.max_pages)
    with httpx.Client(
        follow_redirects=False,
        timeout=ctx.settings.request_timeout,
        headers={"User-Agent": ctx.settings.user_agent},
    ) as client:
        url_queue = select_urls(url, discovered, max_pages)
        seen_urls = set(url_queue)

        while url_queue and len(pages) < max_pages:
            page_url = url_queue.pop(0)
            if not ctx.gate.is_allowed(page_url):  # belt-and-suspenders re-check
                continue
            try:
                resp = gated_get(client, page_url, ctx.gate)
            except httpx.HTTPError as exc:
                errors.append(f"fetch failed for {page_url}: {exc}")
                continue
            page = PageSnapshot(
                url=str(resp.url),
                status_code=resp.status_code,
                headers={k.lower(): v for k, v in resp.headers.items()},
                html=resp.text,
            )
            pages.append(page)

            # If Katana was not installed or discovered nothing, spider same-origin links
            if not discovered and len(pages) < max_pages:
                for link in _extract_links(page.html, str(resp.url)):
                    if link not in seen_urls and ctx.gate.is_allowed(link):
                        seen_urls.add(link)
                        url_queue.append(link)

        # Render JS-built pages (when Playwright is installed), then download the
        # app's own bundles (allowlisted hosts only — see js_bundle.py docstring).
        extra_scripts = _apply_rendering(pages, ctx)
        bundles = extract_bundles(pages, ctx, client=client, extra_urls=extra_scripts)

    # Endpoints = Katana discovered + internal API routes extracted from HTML and bundles
    endpoints = [Endpoint(url=d.url, method=d.method) for d in discovered]
    existing_endpoint_urls = {e.url for e in endpoints}

    for bundle in bundles:
        for route in _extract_api_routes(bundle.content, url):
            if route not in existing_endpoint_urls:
                existing_endpoint_urls.add(route)
                endpoints.append(Endpoint(url=route, method="GET"))

    for p in pages:
        for route in _extract_api_routes(p.html, url):
            if route not in existing_endpoint_urls:
                existing_endpoint_urls.add(route)
                endpoints.append(Endpoint(url=route, method="GET"))

    return Artifact(
        target_url=url,
        pages=pages,
        js_bundles=bundles,
        endpoints=endpoints,
        tech=fingerprint.detect(pages, bundles),
        errors=errors,
    )
