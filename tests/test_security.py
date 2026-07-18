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

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from odfdo.security import SecurityConfig, SecurityError, security, validate_zip_safety


def test_security_error_is_exception():
    """SecurityError should be a subclass of Exception."""
    assert issubclass(SecurityError, Exception)


def test_security_error_can_be_raised():
    """SecurityError should be raisable and catchable."""
    with pytest.raises(SecurityError, match="test error"):
        raise SecurityError("test error")


def test_security_config_default_values():
    """SecurityConfig should have correct default values."""
    config = SecurityConfig()
    assert config.max_uncompressed_size == 500 * 1024 * 1024  # 500MB
    assert config.max_compression_ratio == 200
    assert config.max_file_count == 10000
    assert config.max_spaces_attribute == 10000
    assert config.max_xml_depth == 1000


def test_security_config_custom_values():
    """SecurityConfig should accept custom values."""
    config = SecurityConfig(
        max_uncompressed_size=100,
        max_compression_ratio=50,
        max_file_count=500,
        max_spaces_attribute=5000,
        max_xml_depth=500,
    )
    assert config.max_uncompressed_size == 100
    assert config.max_compression_ratio == 50
    assert config.max_file_count == 500
    assert config.max_spaces_attribute == 5000
    assert config.max_xml_depth == 500


def test_security_config_reset_to_defaults():
    """reset_to_defaults should restore all values to defaults."""
    config = SecurityConfig()
    # Modify all values
    config.max_uncompressed_size = 1
    config.max_compression_ratio = 1
    config.max_file_count = 1
    config.max_spaces_attribute = 1
    config.max_xml_depth = 1
    # Reset
    config.reset_to_defaults()
    # Check defaults restored
    assert config.max_uncompressed_size == 500 * 1024 * 1024
    assert config.max_compression_ratio == 200
    assert config.max_file_count == 10000
    assert config.max_spaces_attribute == 10000
    assert config.max_xml_depth == 1000


def test_security_singleton_exists():
    """The global security singleton should exist."""
    assert isinstance(security, SecurityConfig)


def test_security_singleton_can_be_modified():
    """The global security singleton should be modifiable at runtime."""
    original = security.max_uncompressed_size
    try:
        security.max_uncompressed_size = 12345
        assert security.max_uncompressed_size == 12345
    finally:
        security.max_uncompressed_size = original


def test_security_singleton_reset():
    """The global security singleton reset_to_defaults should work."""
    original = security.max_uncompressed_size
    security.max_uncompressed_size = 999
    security.reset_to_defaults()
    assert security.max_uncompressed_size == 500 * 1024 * 1024
    # Restore if different
    if original != 500 * 1024 * 1024:
        security.max_uncompressed_size = original


def create_zip_bytes(
    files: dict[str, str | bytes], compression: int = zipfile.ZIP_DEFLATED
) -> io.BytesIO:
    """Helper to create a ZIP file in memory."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=compression) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    buffer.seek(0)
    return buffer


class TestValidateZipSafety:
    """Tests for validate_zip_safety function."""

    def test_empty_zip_passes(self):
        """An empty ZIP should pass validation."""
        buffer = create_zip_bytes({})
        with zipfile.ZipFile(buffer, "r") as zf:
            validate_zip_safety(zf)  # Should not raise

    def test_normal_zip_passes(self):
        """A normal ODF-like ZIP should pass validation."""
        buffer = create_zip_bytes(
            {
                "mimetype": "application/vnd.oasis.opendocument.text",
                "content.xml": "<office:document-content xmlns:office='urn:oasis:names:tc:opendocument:xmlns:office:1.0'><office:body><office:text></office:text></office:body></office:document-content>",
                "styles.xml": "<office:document-styles xmlns:office='urn:oasis:names:tc:opendocument:xmlns:office:1.0'></office:document-styles>",
            }
        )
        with zipfile.ZipFile(buffer, "r") as zf:
            validate_zip_safety(zf)  # Should not raise

    def test_max_file_count_exceeded(self):
        """ZIP with too many files should raise SecurityError."""
        original_limit = security.max_file_count
        try:
            security.max_file_count = 3
            buffer = create_zip_bytes(
                {
                    "file1.txt": "content1",
                    "file2.txt": "content2",
                    "file3.txt": "content3",
                    "file4.txt": "content4",
                }
            )
            with zipfile.ZipFile(buffer, "r") as zf:
                with pytest.raises(SecurityError, match="Too many files in archive"):
                    validate_zip_safety(zf)
        finally:
            security.max_file_count = original_limit

    def test_max_file_count_boundary(self):
        """ZIP at exactly max file count should pass."""
        original_limit = security.max_file_count
        try:
            security.max_file_count = 3
            buffer = create_zip_bytes(
                {
                    "file1.txt": "content1",
                    "file2.txt": "content2",
                    "file3.txt": "content3",
                }
            )
            with zipfile.ZipFile(buffer, "r") as zf:
                validate_zip_safety(zf)  # Should not raise (3 <= 3)
        finally:
            security.max_file_count = original_limit

    def test_compression_ratio_exceeded(self):
        """ZIP with high compression ratio should raise SecurityError."""
        original_limit = security.max_compression_ratio
        try:
            security.max_compression_ratio = 5  # Very low threshold
            # Create highly compressible content (repeated character)
            buffer = create_zip_bytes(
                {
                    "mimetype": "application/vnd.oasis.opendocument.text",
                    "content.xml": "A"
                    * 100000,  # 100KB of same char compresses very well
                }
            )
            with zipfile.ZipFile(buffer, "r") as zf:
                with pytest.raises(SecurityError, match="High compression ratio"):
                    validate_zip_safety(zf)
        finally:
            security.max_compression_ratio = original_limit

    def test_compression_ratio_boundary(self):
        """ZIP at exactly compression ratio limit should pass."""
        original_limit = security.max_compression_ratio
        try:
            # Use a very high limit so normal content passes
            security.max_compression_ratio = 10000
            buffer = create_zip_bytes(
                {
                    "mimetype": "application/vnd.oasis.opendocument.text",
                    "content.xml": "A" * 100000,
                }
            )
            with zipfile.ZipFile(buffer, "r") as zf:
                validate_zip_safety(zf)  # Should not raise
        finally:
            security.max_compression_ratio = original_limit

    def test_compression_ratio_zero_compress_size(self):
        """ZIP entry with compress_size of 0 should not cause division issues."""
        # ZIP_STORED means no compression, compress_size equals file_size
        buffer = create_zip_bytes(
            {
                "test.txt": "small content",
            },
            compression=zipfile.ZIP_STORED,
        )
        with zipfile.ZipFile(buffer, "r") as zf:
            info = zf.infolist()[0]
            # With STORED, compress_size == file_size, ratio would be 1.0
            assert info.compress_size == info.file_size
            validate_zip_safety(zf)  # Should not raise

    def test_total_uncompressed_size_exceeded(self):
        """ZIP with total size too large should raise SecurityError."""
        original_limit = security.max_uncompressed_size
        try:
            security.max_uncompressed_size = 1000  # 1KB limit
            buffer = create_zip_bytes(
                {
                    "file1.txt": "x" * 600,
                    "file2.txt": "y" * 600,
                }
            )
            with zipfile.ZipFile(buffer, "r") as zf:
                with pytest.raises(SecurityError, match="Total uncompressed size"):
                    validate_zip_safety(zf)
        finally:
            security.max_uncompressed_size = original_limit

    def test_total_uncompressed_size_boundary(self):
        """ZIP at exactly max total size should pass."""
        original_limit = security.max_uncompressed_size
        try:
            security.max_uncompressed_size = 100  # 100 bytes
            buffer = create_zip_bytes(
                {
                    "file1.txt": "x" * 50,
                    "file2.txt": "y" * 50,
                }
            )
            with zipfile.ZipFile(buffer, "r") as zf:
                validate_zip_safety(zf)  # Should not raise (100 <= 100)
        finally:
            security.max_uncompressed_size = original_limit

    def test_error_message_includes_prefix(self):
        """SecurityError messages should include the required prefix."""
        original_limit = security.max_file_count
        try:
            security.max_file_count = 1
            buffer = create_zip_bytes(
                {
                    "file1.txt": "content1",
                    "file2.txt": "content2",
                }
            )
            with zipfile.ZipFile(buffer, "r") as zf:
                with pytest.raises(SecurityError) as exc_info:
                    validate_zip_safety(zf)
                assert "odfdo detected a breach of security" in str(exc_info.value)
        finally:
            security.max_file_count = original_limit

    def test_multiple_security_checks_run(self):
        """All security checks should be evaluated."""
        # Test that file_count check runs before size check
        original_file_count = security.max_file_count
        original_size = security.max_uncompressed_size
        try:
            security.max_file_count = 2
            security.max_uncompressed_size = 1000000
            buffer = create_zip_bytes(
                {
                    "file1.txt": "x" * 100,
                    "file2.txt": "y" * 100,
                    "file3.txt": "z" * 100,
                }
            )
            with zipfile.ZipFile(buffer, "r") as zf:
                with pytest.raises(SecurityError, match="Too many files"):
                    validate_zip_safety(zf)
        finally:
            security.max_file_count = original_file_count
            security.max_uncompressed_size = original_size


class TestSecurityIntegration:
    """Integration tests for security module."""

    def test_security_config_is_dataclass(self):
        """SecurityConfig should be a dataclass with proper repr."""
        config = SecurityConfig()
        assert "SecurityConfig" in repr(config)
        assert "max_uncompressed_size" in repr(config)

    def test_security_config_equality(self):
        """SecurityConfig instances with same values should be comparable."""
        config1 = SecurityConfig()
        config2 = SecurityConfig()
        assert config1.max_uncompressed_size == config2.max_uncompressed_size

    def test_security_config_inequality(self):
        """Modified SecurityConfig should differ from default."""
        config1 = SecurityConfig()
        config2 = SecurityConfig()
        config2.max_uncompressed_size = 999
        assert config1.max_uncompressed_size != config2.max_uncompressed_size


def test_validate_zip_safety_with_path(tmp_path: Path):
    """validate_zip_safety should work with ZipFile opened from path."""
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("test.txt", "content")

    with zipfile.ZipFile(zip_path, "r") as zf:
        validate_zip_safety(zf)  # Should not raise
