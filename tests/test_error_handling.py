# miniswhid
# Copyright (c) 2025 Diego Jorquera
# SPDX-License-Identifier: MIT

"""
Test error handling for miniswhid API methods.

These tests verify that the API methods handle invalid parameters correctly
and raise appropriate exceptions with helpful error messages.
"""

import os
import tempfile
import unittest

from miniswhid import compute_content_swhid, compute_directory_swhid


class TestErrorHandling(unittest.TestCase):
    """Test error handling for invalid parameters to API methods"""

    def test_content_swhid_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            compute_content_swhid("/nonexistent/file/path")

    def test_content_swhid_empty_path(self):
        with self.assertRaises(FileNotFoundError):
            compute_content_swhid("")

    def test_content_swhid_directory_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(IsADirectoryError):
                compute_content_swhid(temp_dir)

    def test_content_swhid_permission_denied(self):
        # Create a file, remove read permissions, then test
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(b"test content")
            tmp.flush()

            # Remove read permissions
            os.chmod(tmp.name, 0o000)

            try:
                # This should raise PermissionError
                with self.assertRaises(PermissionError):
                    compute_content_swhid(tmp.name)
            finally:
                # Restore permissions so automatic cleanup can work
                os.chmod(tmp.name, 0o644)

    def test_directory_swhid_nonexistent_directory(self):
        with self.assertRaises(FileNotFoundError):
            compute_directory_swhid("/nonexistent/directory/path")

    def test_directory_swhid_empty_path(self):
        with self.assertRaises(FileNotFoundError):
            compute_directory_swhid("")

    def test_directory_swhid_file_path(self):
        with tempfile.NamedTemporaryFile() as tmp:
            with self.assertRaises(NotADirectoryError):
                compute_directory_swhid(tmp.name)

    def test_directory_swhid_permission_denied(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory
            test_dir = os.path.join(temp_dir, "test_dir")
            os.makedirs(test_dir)

            # Add a file to make it non-empty
            with open(os.path.join(test_dir, "file.txt"), "w") as f:
                f.write("content")

            try:
                # Remove read/execute permissions
                os.chmod(test_dir, 0o000)

                # This should raise PermissionError
                with self.assertRaises(PermissionError):
                    compute_directory_swhid(test_dir)
            finally:
                # Restore permissions so cleanup can work
                os.chmod(test_dir, 0o755)

    def test_content_swhid_none_parameter(self):
        with self.assertRaises(TypeError):
            compute_content_swhid(None)  # type: ignore

    def test_directory_swhid_none_parameter(self):
        with self.assertRaises(TypeError):
            compute_directory_swhid(None)  # type: ignore

    def test_directory_swhid_concurrent_file_access_errors(self):
        """Test ThreadPoolExecutor error handling during parallel file processing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "concurrent_test")
            os.makedirs(test_dir)

            # Create a file with no read permissions from the start
            problematic_file = os.path.join(test_dir, "no_read_access.txt")
            with open(problematic_file, "w") as f:
                f.write("inaccessible content\n")

            # Remove read permissions before processing starts
            os.chmod(problematic_file, 0o000)

            # Create additional files to ensure ThreadPoolExecutor is used
            for i in range(5):
                file_path = os.path.join(test_dir, f"file_{i}.txt")
                with open(file_path, "w") as f:
                    f.write(f"content {i}\n")

            try:
                # This should propagate the PermissionError from future.result()
                with self.assertRaises(PermissionError):
                    compute_directory_swhid(test_dir)
            finally:
                # Restore permissions for cleanup
                try:
                    os.chmod(problematic_file, 0o644)
                except OSError:
                    pass

    def test_directory_swhid_file_access_in_threadpool(self):
        """Test that ThreadPoolExecutor properly propagates file access errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "threadpool_test")
            os.makedirs(test_dir)

            # Create enough files to trigger ThreadPoolExecutor (>1 file)
            for i in range(3):
                file_path = os.path.join(test_dir, f"file_{i}.txt")
                with open(file_path, "w") as f:
                    f.write(f"content {i}\n")

            # Create a symlink to verify symlinks are excluded from ThreadPoolExecutor
            os.symlink("file_0.txt", os.path.join(test_dir, "symlink_file"))

            # Create a subdirectory with a file that has permission issues
            subdir = os.path.join(test_dir, "subdir")
            os.makedirs(subdir)
            problem_file = os.path.join(subdir, "permission_problem.txt")
            with open(problem_file, "w") as f:
                f.write("problematic content\n")

            try:
                # Remove read permissions
                os.chmod(problem_file, 0o000)

                # This should propagate PermissionError from the worker thread
                with self.assertRaises(PermissionError):
                    compute_directory_swhid(test_dir)
            finally:
                # Restore permissions for cleanup
                try:
                    os.chmod(problem_file, 0o644)
                except OSError:
                    pass
