"""Shared HTTP response helpers for acquisition and detectors.

One implementation of the two patterns every probe-based check needs:
bounded reads (never download more than N bytes of somebody's file) and
SPA-fallback detection (Vercel/Netlify answer 200 + the app shell for
*every* unknown path — a bare status-code check would flag everything).
"""
from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator
from urllib.parse import urljoin

import httpx


_REDIRECT_STATUSES = {301, 302, 303, 307, 308}


@contextmanager
def gated_stream(client: httpx.Client, method: str, url: str, gate, *, max_redirects: int = 5, **kwargs) -> Iterator[httpx.Response]:
    """Stream a response while checking consent before every redirect hop."""
    current = url
    for _ in range(max_redirects + 1):
        gate.check(current)
        with client.stream(method, current, follow_redirects=False, **kwargs) as response:
            location = response.headers.get("location")
            if response.status_code not in _REDIRECT_STATUSES or not location:
                yield response
                return
            destination = urljoin(str(response.url), location)
            # Refuse before a request can be sent to the redirect destination.
            gate.check(destination)
            current = destination
    raise httpx.TooManyRedirects(f"more than {max_redirects} redirects from {url}")


def gated_get(client: httpx.Client, url: str, gate, *, max_redirects: int = 5, **kwargs) -> httpx.Response:
    """GET a page and check consent before following each redirect."""
    current = url
    for _ in range(max_redirects + 1):
        gate.check(current)
        response = client.get(current, follow_redirects=False, **kwargs)
        location = response.headers.get("location")
        if response.status_code not in _REDIRECT_STATUSES or not location:
            return response
        destination = urljoin(str(response.url), location)
        response.close()
        gate.check(destination)
        current = destination
    raise httpx.TooManyRedirects(f"more than {max_redirects} redirects from {url}")


def read_bounded(resp, limit: int) -> bytes:
    """Read at most `limit` bytes from a streaming httpx response."""
    chunks: list[bytes] = []
    size = 0
    for chunk in resp.iter_bytes():
        chunks.append(chunk)
        size += len(chunk)
        if size >= limit:
            break
    return b"".join(chunks)[:limit]


def looks_like_html(content_type: str, raw: bytes) -> bool:
    """True when a response is an HTML page (e.g. an SPA fallback shell)."""
    if "text/html" in content_type.lower():
        return True
    sniff = raw[:200].lstrip().lower()
    return sniff.startswith(b"<!doctype") or sniff.startswith(b"<html")
