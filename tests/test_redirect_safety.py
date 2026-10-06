"""Redirect consent tests use an in-memory HTTPX transport only."""
import httpx
import pytest

from vibetest.core.consent import ConsentDenied, ConsentGate
from vibetest.core.http_util import gated_get, gated_stream


def test_gated_get_refuses_cross_host_redirect_before_following():
    calls = []

    def handler(request):
        calls.append(str(request.url))
        return httpx.Response(302, headers={"location": "https://outside.test/secret"}, request=request)

    with httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True) as client:
        with pytest.raises(ConsentDenied):
            gated_get(client, "https://owned.test/start", ConsentGate(["owned.test"]))
    assert calls == ["https://owned.test/start"]


def test_gated_get_allows_redirect_to_allowlisted_subdomain():
    calls = []

    def handler(request):
        calls.append(str(request.url))
        if request.url.path == "/start":
            return httpx.Response(302, headers={"location": "https://app.owned.test/final"}, request=request)
        return httpx.Response(200, text="ok", request=request)

    with httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True) as client:
        response = gated_get(client, "https://owned.test/start", ConsentGate(["owned.test"]))
    assert response.status_code == 200
    assert calls == ["https://owned.test/start", "https://app.owned.test/final"]


def test_gated_stream_refuses_cross_host_redirect_before_following():
    calls = []

    def handler(request):
        calls.append(str(request.url))
        return httpx.Response(302, headers={"location": "https://outside.test/file.js"}, request=request)

    with httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True) as client:
        with pytest.raises(ConsentDenied):
            with gated_stream(client, "GET", "https://owned.test/app.js", ConsentGate(["owned.test"])):
                pass
    assert calls == ["https://owned.test/app.js"]
