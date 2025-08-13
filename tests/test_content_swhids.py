# miniswhid
# Copyright (c) 2025 Diego Jorquera
# SPDX-License-Identifier: MIT

"""
Test content SWHID computation.

All expected SWHIDs are generated using `swh identify` from the official
Software Heritage toolchain to ensure correctness.
"""

import tempfile
import unittest

from miniswhid import compute_content_swhid


class TestContentSWHIDs(unittest.TestCase):
    """Test content (file) SWHID computation"""

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w") as tmp:
            tmp.flush()

            swhid = compute_content_swhid(tmp.name)
            expected = "swh:1:cnt:e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
            self.assertEqual(swhid, expected)

    def test_text_file(self):
        with tempfile.NamedTemporaryFile(mode="w") as tmp:
            tmp.write("Hello World\nHello World\nHello World\n")
            tmp.flush()

            swhid = compute_content_swhid(tmp.name)
            expected = "swh:1:cnt:1b032f8cbb97e41ff294b203cfce439b66895609"
            self.assertEqual(swhid, expected)

    def test_binary_file(self):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(bytes(range(256)))
            tmp.flush()

            swhid = compute_content_swhid(tmp.name)
            expected = "swh:1:cnt:c86626638e0bc8cf47ca49bb1525b40e9737ee64"
            self.assertEqual(swhid, expected)

    def test_large_file(self):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(b"x" * (100 * 1024))
            tmp.flush()

            swhid = compute_content_swhid(tmp.name)
            expected = "swh:1:cnt:710e790fe27838de793236b533ecc9aa453036a1"
            self.assertEqual(swhid, expected)
