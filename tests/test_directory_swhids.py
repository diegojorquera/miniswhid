# miniswhid
# Copyright (c) 2025 Diego Jorquera
# SPDX-License-Identifier: MIT

"""
Test directory SWHID computation.

All expected SWHIDs are generated using `swh identify` from the official
Software Heritage toolchain to ensure correctness.
"""

import os
import tempfile
import unittest

from miniswhid import compute_directory_swhid


class TestDirectorySWHIDs(unittest.TestCase):
    """Test directory SWHID computation"""

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_dir = os.path.join(temp_dir, "empty")
            os.makedirs(empty_dir)

            swhid = compute_directory_swhid(empty_dir)
            expected = "swh:1:dir:4b825dc642cb6eb9a060e54bf8d69288fbee4904"
            self.assertEqual(swhid, expected)

    def test_complex_directory_structures(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested structure
            nested_dir = os.path.join(temp_dir, "nested")
            os.makedirs(os.path.join(nested_dir, "sub1", "deep"))
            os.makedirs(os.path.join(nested_dir, "sub2"))

            # Add files
            with open(os.path.join(nested_dir, "sub1", "deep", "file.txt"), "w") as f:
                f.write("deep file\n")
            with open(os.path.join(nested_dir, "sub2", "data.txt"), "w") as f:
                f.write("sub2 content\n")
            with open(os.path.join(nested_dir, "README.md"), "w") as f:
                f.write("root file\n")

            swhid = compute_directory_swhid(nested_dir)
            expected = "swh:1:dir:b678b5af0ad6d6c0f2e425c8ae0c9c11676376c5"
            self.assertEqual(swhid, expected)

    def test_unicode_filenames(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            unicode_dir = os.path.join(temp_dir, "unicode_test")
            os.makedirs(unicode_dir)

            # Create files with unicode filenames (Chinese characters)
            with open(
                os.path.join(unicode_dir, "测试文件名.txt"), "w", encoding="utf-8"
            ) as f:
                f.write("Unicode filename content\n")

            with open(os.path.join(unicode_dir, "regular.txt"), "w") as f:
                f.write("Regular filename\n")

            swhid = compute_directory_swhid(unicode_dir)
            expected = "swh:1:dir:932606ba9d7ac313de532a19b787bb0186a72c1b"
            self.assertEqual(swhid, expected)

    def test_unicode_directory_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "unicode_dirs")
            os.makedirs(test_dir)

            # Create subdirectories with unicode names (Chinese and Russian characters)
            chinese_dir = os.path.join(test_dir, "测试目录")
            russian_dir = os.path.join(test_dir, "русская_папка")
            os.makedirs(chinese_dir)
            os.makedirs(russian_dir)

            # Add content to each directory
            with open(
                os.path.join(chinese_dir, "content.txt"), "w", encoding="utf-8"
            ) as f:
                f.write("file in chinese dir\n")
            with open(
                os.path.join(russian_dir, "файл.txt"), "w", encoding="utf-8"
            ) as f:
                f.write("file in russian dir\n")

            # Add a regular file at root level
            with open(os.path.join(test_dir, "regular_file.txt"), "w") as f:
                f.write("regular dir file\n")

            swhid = compute_directory_swhid(test_dir)
            expected = "swh:1:dir:c07cdcd8891ac98bfe71eec82fed07b61f23d2fe"
            self.assertEqual(swhid, expected)

    def test_directory_with_file_symlinks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "file_symlinks")
            os.makedirs(test_dir)

            # Create files and symlinks pointing to them
            with open(os.path.join(test_dir, "file1.txt"), "w") as f:
                f.write("content1\n")
            with open(os.path.join(test_dir, "file2.txt"), "w") as f:
                f.write("content2\n")

            os.symlink("file1.txt", os.path.join(test_dir, "link_to_file1"))
            os.symlink("file2.txt", os.path.join(test_dir, "link_to_file2"))

            swhid = compute_directory_swhid(test_dir)
            expected = "swh:1:dir:9af2d8ac62afecf35c122d4eeb2bf1d178ca76f8"
            self.assertEqual(swhid, expected)

    def test_directory_with_directory_symlinks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "dir_symlinks")
            os.makedirs(test_dir)

            # Create subdirectories with content
            subdir1 = os.path.join(test_dir, "subdir1")
            subdir2 = os.path.join(test_dir, "subdir2")
            os.makedirs(subdir1)
            os.makedirs(subdir2)

            with open(os.path.join(subdir1, "file.txt"), "w") as f:
                f.write("sub1 content\n")
            with open(os.path.join(subdir2, "file.txt"), "w") as f:
                f.write("sub2 content\n")

            # Create symlinks to subdirectories
            os.symlink("subdir1", os.path.join(test_dir, "link_to_subdir1"))
            os.symlink("subdir2", os.path.join(test_dir, "link_to_subdir2"))

            swhid = compute_directory_swhid(test_dir)
            expected = "swh:1:dir:a3595e28c573e3220ae48a6f6eadcebfe0bf2fad"
            self.assertEqual(swhid, expected)

    def test_directory_with_broken_symlinks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "broken_symlinks")
            os.makedirs(test_dir)

            # Create a real file for contrast
            with open(os.path.join(test_dir, "real_file.txt"), "w") as f:
                f.write("real file\n")

            # Create broken symlinks
            os.symlink("nonexistent_file", os.path.join(test_dir, "broken_link"))
            os.symlink("missing_dir", os.path.join(test_dir, "broken_dir_link"))

            swhid = compute_directory_swhid(test_dir)
            expected = "swh:1:dir:288235f3c8653edbf4bc0c7db2cb34ee0e746136"
            self.assertEqual(swhid, expected)

    def test_directory_with_mixed_content_types(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "mixed_types")
            os.makedirs(test_dir)

            # Regular file and executable
            with open(os.path.join(test_dir, "regular.txt"), "w") as f:
                f.write("regular file\n")

            script_path = os.path.join(test_dir, "script.sh")
            with open(script_path, "w") as f:
                f.write("executable content\n")
            os.chmod(script_path, 0o755)

            # Subdirectory with content
            subdir = os.path.join(test_dir, "subdir")
            os.makedirs(subdir)
            with open(os.path.join(subdir, "nested.txt"), "w") as f:
                f.write("subdir file\n")

            # All types of symlinks (comprehensive symlink coverage)
            os.symlink(
                "regular.txt", os.path.join(test_dir, "link_to_file")
            )  # File symlink
            os.symlink(
                "subdir", os.path.join(test_dir, "link_to_dir")
            )  # Directory symlink
            os.symlink(
                "nonexistent", os.path.join(test_dir, "broken_link")
            )  # Broken symlink
            os.symlink(
                "/etc/passwd", os.path.join(test_dir, "abs_link")
            )  # Absolute symlink

            swhid = compute_directory_swhid(test_dir)
            expected = "swh:1:dir:61306a3816a5a0cafe0f948f6237e7c43c8f4181"
            self.assertEqual(swhid, expected)
