#!/usr/bin/env python3
# miniswhid
# Copyright (c) 2025 Diego Jorquera
# SPDX-License-Identifier: MIT

"""
Command-line interface for miniswhid.

Provides a simple CLI for computing Software Hash Identifiers (SWHIDs)
for files and directories.
"""

import os
import sys

from .miniswhid import compute_content_swhid, compute_directory_swhid


def main() -> None:
    """
    Command-line interface for computing SWHIDs.

    Usage: miniswhid <path>

    Computes and prints the SWHID for a file or directory.
    """
    if len(sys.argv) != 2:
        usage()
        exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print("Path doesn't exist")
        exit(1)

    if os.path.isdir(path):
        print(compute_directory_swhid(path))
    else:
        print(compute_content_swhid(path))


def usage() -> None:
    print("miniswhid - No-frills Software Hash Identifier (SWHID) computation")
    print()
    print("Usage: miniswhid <path>")
    print()
    print("Computes and prints the SWHID for a file or directory.")
    print()
    print("Arguments:")
    print("  path    Path to a file or directory to compute the SWHID for")
    print()
    print("Examples:")
    print("  miniswhid README.md              # Compute SWHID for a file")
    print("  miniswhid /path/to/directory     # Compute SWHID for a directory")
    print()
    print("Output formats:")
    print("  swh:1:cnt:<hash>  # Content (file) SWHID")
    print("  swh:1:dir:<hash>  # Directory SWHID")


if __name__ == "__main__":
    main()
