import io
import tempfile
import unittest
from pathlib import Path

import app


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
