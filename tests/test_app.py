import base64
import io
import re
import tempfile
import unittest
from pathlib import Path

import app
import qrcode
from qrcode.image.svg import SvgPathImage


class DropTest(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.TemporaryDirectory()
        app.DATA_DIR = Path(self.data.name)
        self.client = app.app.test_client()

    def tearDown(self):
        self.data.cleanup()

    def test_upload_and_default_download_is_one_time(self):
        response = self.client.post(
            "/upload",
            data={"file": (io.BytesIO(b"hello"), "hello.txt"), "expiration": "download"},
            content_type="multipart/form-data",
            headers={"Accept": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        slug = response.get_json()["url"].rsplit("/", 1)[-1]
        downloaded = self.client.get(f"/d/{slug}")
        self.assertEqual(downloaded.status_code, 200)
        self.assertEqual(downloaded.data, b"hello")
        self.assertEqual(self.client.get(f"/d/{slug}").status_code, 404)

    def test_invalid_expiration_is_rejected(self):
        response = self.client.post(
            "/upload",
            data={"file": (io.BytesIO(b"hello"), "hello.txt"), "expiration": "never"},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_home_page_uses_static_stylesheet(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"/static/style.css", response.data)

    def test_browser_upload_shows_qr_code_for_download_link(self):
        response = self.client.post(
            "/upload",
            data={"file": (io.BytesIO(b"hello"), "hello.txt"), "expiration": "forever"},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        link_match = re.search(r'<a href="([^"]+)">', html)
        qr_match = re.search(
            r'<img class="qr-code" src="data:image/svg\+xml;base64,([^"]+)" '
            r'alt="QR code for download link">',
            html,
        )
        self.assertIsNotNone(link_match)
        self.assertIsNotNone(qr_match)

        expected_code = qrcode.QRCode(box_size=8, border=4)
        expected_code.add_data(link_match.group(1))
        expected_code.make(fit=True)
        expected_image = expected_code.make_image(image_factory=SvgPathImage)
        expected_svg = io.BytesIO()
        expected_image.save(expected_svg)
        self.assertEqual(base64.b64decode(qr_match.group(1)), expected_svg.getvalue())

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_forever_file_can_be_downloaded_twice(self):
        response = self.client.post(
            "/upload",
            data={"file": (io.BytesIO(b"hello"), "hello.txt"), "expiration": "forever"},
            content_type="multipart/form-data",
            headers={"Accept": "application/json"},
        )
        slug = response.get_json()["url"].rsplit("/", 1)[-1]
        self.assertEqual(self.client.get(f"/d/{slug}").status_code, 200)
        self.assertEqual(self.client.get(f"/d/{slug}").status_code, 200)
