# Copyright 2018-2026 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors (odfdo project): jerome.dumonteil@gmail.com
# The odfdo project is a derivative work of the lpod-python project:
# https://github.com/lpod/lpod-python
"""Security limits and validation for ODF document processing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zipfile import ZipFile


class SecurityError(Exception):
    """Raised when a document exceeds security thresholds (Zip bomb, XML bomb, etc.)."""

    pass


@dataclass
class SecurityConfig:
    """Security limits configuration.

    This class holds security-related limits for ODF document processing.
    Modify attributes at runtime to customize security thresholds.

    Example:
        >>> from odfdo.security import security
        >>> security.max_uncompressed_size = 1024 * 1024 * 1024  # 1GB
        >>> security.reset_to_defaults()  # Reset to defaults
    """

    max_uncompressed_size: int = 500 * 1024 * 1024  # 500MB
    max_compression_ratio: int = 200
    max_file_count: int = 10000
    max_spaces_attribute: int = 10000
    max_xml_depth: int = 1000  # Prevents stack overflow on deeply nested tags

    def reset_to_defaults(self) -> None:
        """Reset all security limits to their default values."""
        self.max_uncompressed_size = 500 * 1024 * 1024
        self.max_compression_ratio = 200
        self.max_file_count = 10000
        self.max_spaces_attribute = 10000
        self.max_xml_depth = 1000


def validate_zip_safety(zip_file: ZipFile) -> None:
    """Validate ZIP file safety against zip bombs.

    Checks total uncompressed size, compression ratio, and file count
    against the global `security` singleton configuration.
    Raises SecurityError if limits are exceeded.

    Args:
        zip_file: An opened ZipFile object.

    Raises:
        SecurityError: If the ZIP exceeds security thresholds.
    """
    total_uncompressed_size = 0
    file_count = 0

    for info in zip_file.infolist():
        file_count += 1  # noqa: SIM113
        if file_count > security.max_file_count:
            raise SecurityError(
                f"odfdo detected a breach of security. "
                f"Too many files in archive ({file_count} exceeds limit {security.max_file_count})."
            )
        # Check individual file size
        total_uncompressed_size += info.file_size

        # Check compression ratio for non-empty files
        if (
            info.compress_size > 0
            and info.file_size > security.max_compression_ratio * info.compress_size
        ):
            ratio = info.file_size / info.compress_size
            raise SecurityError(
                f"odfdo detected a breach of security. "
                f"High compression ratio ({ratio:.1f}:1) detected in {info.filename}. "
                f"Maximum allowed is {security.max_compression_ratio}:1."
            )

    if total_uncompressed_size > security.max_uncompressed_size:
        raise SecurityError(
            f"odfdo detected a breach of security. "
            f"Total uncompressed size ({total_uncompressed_size} bytes) exceeds limit "
            f"({security.max_uncompressed_size} bytes)."
        )


# Global singleton instance - import this to access and modify security settings
security = SecurityConfig()
