# miniswhid
# Copyright (c) 2025 Diego Jorquera
# SPDX-License-Identifier: MIT

"""
miniswhid - No-frills Software Hash Identifier (SWHID) computation

This module provides functions to compute Software Hash Identifiers (SWHIDs)
for files and directories. SWHIDs are cryptographic identifiers that uniquely
identify software artifacts and are compatible with Git's object model.

The implementation follows the official [SWHID specification](https://swhid.org).
"""

import concurrent.futures
import hashlib
import io
import os


def compute_directory_swhid(dir_path: str) -> str:
    """
    Compute the SWHID for a directory.

    Args:
        dir_path: Path to the directory

    Returns:
        Directory SWHID string in format "swh:1:dir:<hash>"

    Example:
        >>> compute_directory_swhid("/path/to/directory")
        'swh:1:dir:a1b2c3d4e5f6...'
    """
    hash = _compute_directory_hash(dir_path)
    return f"swh:1:dir:{bytes.hex(hash)}"


def compute_content_swhid(file_path: str) -> str:
    """
    Compute the content SWHID for a file.

    Args:
        file_path: Path to the file

    Returns:
        Content SWHID string in format "swh:1:cnt:<hash>"

    Example:
        >>> compute_content_swhid("README.md")
        'swh:1:cnt:95d09f2b10159347eece71399a7e2e907ea3df4f'
    """
    hash = _compute_file_content_hash(file_path)
    return f"swh:1:cnt:{bytes.hex(hash)}"


def _compute_file_content_hash(file_path: str) -> bytes:
    file_size = os.path.getsize(file_path)
    prefix = b"blob " + str(file_size).encode("ASCII") + b"\0"

    with open(file_path, "rb") as f:
        return _compute_buffered_io_hash(f, prefix)


def _compute_symlink_content_hash(symlink_path: str) -> bytes:
    link_bytes = os.fsencode(os.readlink(symlink_path))
    prefix = b"blob " + str(len(link_bytes)).encode("ASCII") + b"\0"

    return _compute_buffered_io_hash(io.BytesIO(link_bytes), prefix)


def _compute_directory_hash(dir_path: str) -> bytes:
    class Entry:
        def __init__(self, root: str, name: str):
            self.name = name
            self.path = os.path.join(root, name)
            self.is_symlink = os.path.islink(self.path)

    class DirectoryEntry(Entry):
        def __init__(self, root: str, name: str):
            super().__init__(root, name)
            self.sorting_key = os.fsencode(name) + b"/"

    class FileEntry(Entry):
        def __init__(self, root: str, name: str):
            super().__init__(root, name)
            self.is_executable = os.access(self.path, os.X_OK)
            self.sorting_key = os.fsencode(name)

    def handle_walk_error(error: Exception) -> None:
        """Handle os.walk errors by re-raising the original OS exception.

        This provides better error messages than the KeyError that would
        otherwise occur when dir_path is not found in dir_hashes.
        """
        raise error

    dir_hashes: dict[str, bytes] = {}

    for root, dirs, files in os.walk(
        dir_path, topdown=False, onerror=handle_walk_error
    ):
        file_entries = [FileEntry(root, file) for file in files]
        file_hashes = {}

        if file_entries:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_to_path = {
                    executor.submit(_compute_file_content_hash, entry.path): entry.path
                    for entry in file_entries
                    if not entry.is_symlink
                }

                for future in concurrent.futures.as_completed(future_to_path):
                    file_path = future_to_path[future]
                    file_hashes[file_path] = future.result()

        dir_entries = [DirectoryEntry(root, dir) for dir in dirs]
        entries = file_entries + dir_entries
        sorted_entries = sorted(entries, key=lambda e: e.sorting_key)

        with io.BytesIO() as root_seq_buffer:
            for entry in sorted_entries:
                match entry:
                    case Entry(is_symlink=True):
                        entry_hash = _compute_symlink_content_hash(entry.path)
                        entry_access_rights = b"120000"
                    case DirectoryEntry():
                        entry_hash = dir_hashes.pop(entry.path)
                        entry_access_rights = b"40000"
                    case FileEntry():
                        entry_hash = file_hashes[entry.path]
                        entry_access_rights = (
                            b"100755" if entry.is_executable else b"100644"
                        )

                entry_seq = (
                    entry_access_rights
                    + b" "
                    + os.fsencode(entry.name)
                    + b"\0"
                    + entry_hash
                )
                root_seq_buffer.write(entry_seq)

            prefix = (
                b"tree " + str(len(root_seq_buffer.getvalue())).encode("ASCII") + b"\0"
            )
            dir_hashes[root] = _compute_buffered_io_hash(root_seq_buffer, prefix)

    return dir_hashes[dir_path]


def _compute_buffered_io_hash(buffer: io.BufferedIOBase, prefix: bytes) -> bytes:
    sha1 = hashlib.sha1(prefix)

    buffer.seek(0)
    for chunk in iter(lambda: buffer.read(65536), b""):
        sha1.update(chunk)

    return sha1.digest()
