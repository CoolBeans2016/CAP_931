from urllib.parse import urljoin
from urllib.parse import urlsplit
import ipaddress
import re
from html.parser import HTMLParser
import requests
import socket

def validate_url(url: str) -> str:
    if not url or not url.strip():
        raise ValueError("URL is required.")

    cleaned = url.strip()
    parsed = urlsplit(cleaned)

    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("Only http and https URLs are allowed.")

    if not parsed.netloc:
        raise ValueError("URL is missing a hostname.")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Unable to parse hostname.")

    lowered = hostname.lower()
    if lowered == "localhost" or lowered.endswith(".localhost"):
        raise ValueError("Localhost URLs are not allowed.")

    try:
        address = ipaddress.ip_address(hostname)
        addresses = {address}
    except ValueError:
        try:
            addresses = {
                ipaddress.ip_address(result[4][0])
                for result in socket.getaddrinfo(
                    hostname,
                    None,
                    type=socket.SOCK_STREAM,
                )
            }
        except socket.gaierror as exc:
            raise ValueError(f"Could not resolve hostname: {hostname}") from exc

    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("Private or non-public IP addresses are not allowed.")

    return cleaned


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.ignored_depth = 0

    def handle_starttag(
        self, tag: str, _attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag in {"script", "style"}:
            self.ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.ignored_depth:
            self.ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.ignored_depth:
            return

        text = " ".join(data.split())
        if text:
            self.parts.append(text)

    def get_text(self) -> str:
        return " ".join(self.parts)


def extract_clean_text(html: str) -> str:
    if not html:
        return ""

    parser = TextExtractor()
    parser.feed(html)
    parser.close()
    return " ".join(parser.get_text().split())


def fetch_page_text(url: str) -> dict:
    validated = validate_url(url)

    current_url = validated

    try:
        for _ in range(5):
            with requests.get(
                current_url,
                timeout=(5, 10),
                allow_redirects=False,
                stream=True,
            ) as response:
                if response.status_code in {301, 302, 303, 307, 308}:
                    location = response.headers.get("Location")
                    if not location:
                        raise RuntimeError("Redirect response did not include a Location header.")

                    current_url = validate_url(urljoin(current_url, location))
                    continue

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Request failed with status {response.status_code} for {current_url}"
                    )

                content = bytearray()
                for chunk in response.iter_content(chunk_size=64 * 1024):
                    if not chunk:
                        continue
                    if len(content) + len(chunk) > 1_000_000:
                        raise RuntimeError("Response is too large to process safely.")
                    content.extend(chunk)

                html = bytes(content).decode(
                    response.encoding or "utf-8",
                    errors="replace",
                )
                break
        else:
            raise RuntimeError("Too many redirects.")

    except requests.RequestException as exc:
        raise RuntimeError(f"Could not fetch page: {exc}") from exc

    text = extract_clean_text(html)

    if not text:
        raise RuntimeError("No readable text was extracted from the page.")

    title = ""
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if match:
        title = re.sub(r"<.*?>", "", match.group(1))
        title = " ".join(title.split())

    return {
        "url": current_url,
        "title": title or validated,
        "text": text[:5000],
    }


def collect_sources(
    prospect_url: str,
    competitor_urls: list[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    sources = []
    failures = []
    urls_to_fetch = [("prospect", prospect_url)]

    urls_to_fetch.extend(
        ("competitor", url.strip())
        for url in competitor_urls
        if url.strip()
    )

    for source_type, url in urls_to_fetch:
        try:
            page = fetch_page_text(url)
        except (ValueError, RuntimeError) as exc:
            failures.append({
                "url": url,
                "type": source_type,
                "error": str(exc),
            })
            continue

        sources.append({
            "id": f"S{len(sources) + 1}",
            "type": source_type,
            "url": page["url"],
            "title": page["title"],
            "text": page["text"],
        })

    return sources, failures