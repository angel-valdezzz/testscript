"""HTTP responses are values, including 4xx/5xx responses."""

import httpx

from testscript.model import Builtin, Namespace


class HttpAdapter:
    def __init__(self, timeout=10, base_url="", on_response=None):
        self.timeout, self.base_url, self.on_response = timeout, base_url, on_response
        self.client = None

    def request(self, method, url, body=None, headers=None, query=None):
        if self.client is None:
            self.client = httpx.Client(timeout=self.timeout, follow_redirects=True, trust_env=False)
        response = self.client.request(
            method,
            self.base_url.rstrip("/") + url if url.startswith("/") else url,
            json=body,
            headers=headers,
            params=query,
        )
        try:
            payload = response.json()
        except ValueError:
            payload = None
        result = {
            "status": response.status_code,
            "json": payload,
            "text": response.text,
            "headers": dict(response.headers),
            "url": str(response.url),
        }
        if self.on_response:
            self.on_response(method, str(response.url), response.status_code)
        return result

    def namespace(self):
        members = {}
        for method in ("get", "post", "put", "patch", "delete", "head", "options"):
            members[method] = Builtin(
                f"api.{method}",
                lambda url, body=None, headers=None, query=None, m=method: self.request(
                    m.upper(), url, body, headers, query
                ),
                pure=False,
            )
        return Namespace(members)

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
