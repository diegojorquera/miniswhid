# miniswhid
# Copyright (c) 2025 Diego Jorquera
# SPDX-License-Identifier: MIT

"""
miniswhid - No-frills Software Hash Identifier (SWHID) computation

This package provides functions to compute Software Hash Identifiers (SWHIDs)
for files and directories. SWHIDs are cryptographic identifiers that uniquely
identify software artifacts and are compatible with Git's object model.
"""

from .miniswhid import (
    compute_content_swhid,
    compute_directory_swhid,
)

__version__ = "0.1.0"
__author__ = "Diego Jorquera"

__all__ = [
    "compute_content_swhid",
    "compute_directory_swhid",
]
