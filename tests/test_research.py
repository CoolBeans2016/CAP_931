import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from cap_931.research import fetch_page_text, validate_url, extract_clean_text



class ValidateUrlTests(unittest.TestCase):
    def test_rejects_unsupported_scheme(self) -> None:
        with self.assertRaises(ValueError):
            validate_url("ftp://example.com")

    def test_rejects_loopback_ip(self) -> None:
        with self.assertRaises(ValueError):
            validate_url("http://127.0.0.1")
    def test_rejects_private_ip(self) -> None:
        with self.assertRaises(ValueError):
            validate_url("http://192.168.1.10")
    def test_rejects_empty_url(self) -> None:
        with self.assertRaises(ValueError):
            validate_url("")

    def test_accepts_public_ip_url(self) -> None:
        self.assertEqual(
            validate_url("https://8.8.8.8"),
            "https://8.8.8.8",
        )

    @patch("cap_931.research.socket.getaddrinfo")
    def test_rejects_hostname_resolving_to_private_ip(self, mock_getaddrinfo) -> None:
        mock_getaddrinfo.return_value = [
            (None, None, None, None, ("192.168.1.10", 0))
        ]

        with self.assertRaises(ValueError):
            validate_url("https://example.com")
    @patch("cap_931.research.socket.getaddrinfo")
    def test_accepts_public_hostname(self, mock_getaddrinfo) -> None:
        mock_getaddrinfo.return_value = [
            (None, None, None, None, ("93.184.216.34", 0))
        ]

        self.assertEqual(
            validate_url("https://example.com"),
            "https://example.com",
        )
        mock_getaddrinfo.assert_called_once()

    @patch("cap_931.research.requests.get")
    def test_rejects_redirect_to_private_ip(self, mock_get) -> None:
        response = MagicMock()
        response.__enter__.return_value.status_code = 302
        response.__enter__.return_value.headers = {
            "Location": "http://127.0.0.1"
        }
        mock_get.return_value = response

        with self.assertRaises(ValueError):
            fetch_page_text("https://8.8.8.8")

        mock_get.assert_called_once()

    def test_extracts_readable_text_without_scripts_or_styles(self) -> None:
        html = (
            "<html><head><style>hidden style</style>"
            "<script>hidden script</script></head>"
            "<body><p>Public company text</p></body></html>"
        )

        text = extract_clean_text(html)

        self.assertIn("Public company text", text)
        self.assertNotIn("hidden style", text)
        self.assertNotIn("hidden script", text)

    def test_empty_html_returns_empty_text(self) -> None:
        self.assertEqual(extract_clean_text(""), "") 

    @patch("cap_931.research.requests.get")
    def test_fetch_rejects_empty_page(self, mock_get) -> None:
        response = MagicMock()
        entered_response = response.__enter__.return_value
        entered_response.status_code = 200
        entered_response.encoding = "utf-8"
        entered_response.iter_content.return_value = [b""]
        mock_get.return_value = response

        with self.assertRaisesRegex(RuntimeError, "No readable text"):
            fetch_page_text("https://8.8.8.8")

        mock_get.assert_called_once()

    @patch("cap_931.research.requests.get")
    def test_fetch_rejects_oversized_page(self, mock_get) -> None:
        response = MagicMock()
        entered_response = response.__enter__.return_value
        entered_response.status_code = 200
        entered_response.encoding = "utf-8"
        entered_response.iter_content.return_value = [b"x" * 1_000_001]
        mock_get.return_value = response

        with self.assertRaisesRegex(RuntimeError, "too large"):
            fetch_page_text("https://8.8.8.8")

        mock_get.assert_called_once()

    @patch("cap_931.research.requests.get")
    def test_fetch_returns_title_and_readable_text(self, mock_get) -> None:
        response = MagicMock()
        entered_response = response.__enter__.return_value
        entered_response.status_code = 200
        entered_response.encoding = "utf-8"
        entered_response.iter_content.return_value = [
            b"<title>Example company</title><p>Readable page text</p>"
        ]
        mock_get.return_value = response

        page = fetch_page_text("https://8.8.8.8")

        self.assertEqual(page["url"], "https://8.8.8.8")
        self.assertEqual(page["title"], "Example company")
        self.assertIn("Readable page text", page["text"])
        mock_get.assert_called_once()