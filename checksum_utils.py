"""
Checksum Utilities - File integrity verification for OctopusFTP
"""

import hashlib
from pathlib import Path
from typing import Optional, Callable


class ChecksumCalculator:
    """Calculate file checksums using various hash algorithms"""

    ALGORITHMS = {
        'MD5': hashlib.md5,
        'SHA-1': hashlib.sha1,
        'SHA-256': hashlib.sha256,
        'SHA-512': hashlib.sha512
    }

    @staticmethod
    def calculate_file_hash(
        file_path: str,
        algorithm: str = 'SHA-256',
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> str:
        """
        Calculate hash of a file

        Args:
            file_path: Path to the file
            algorithm: Hash algorithm (MD5, SHA-1, SHA-256, SHA-512)
            progress_callback: Optional callback(bytes_processed, total_bytes)

        Returns:
            Hexadecimal hash string

        Raises:
            ValueError: If algorithm is not supported
            FileNotFoundError: If file doesn't exist
        """
        if algorithm not in ChecksumCalculator.ALGORITHMS:
            raise ValueError(
                f"Unsupported algorithm '{algorithm}'. "
                f"Supported: {', '.join(ChecksumCalculator.ALGORITHMS.keys())}"
            )

        hash_func = ChecksumCalculator.ALGORITHMS[algorithm]()
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = file_path_obj.stat().st_size
        bytes_processed = 0
        block_size = 8192  # 8KB blocks

        with open(file_path, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break

                hash_func.update(data)
                bytes_processed += len(data)

                if progress_callback:
                    progress_callback(bytes_processed, file_size)

        return hash_func.hexdigest()

    @staticmethod
    def verify_checksum(file_path: str, expected_hash: str, algorithm: str = 'SHA-256') -> bool:
        """
        Verify file checksum against expected hash

        Args:
            file_path: Path to the file
            expected_hash: Expected hash value (case-insensitive)
            algorithm: Hash algorithm to use

        Returns:
            True if checksums match, False otherwise
        """
        try:
            calculated_hash = ChecksumCalculator.calculate_file_hash(file_path, algorithm)
            return calculated_hash.lower() == expected_hash.lower()
        except Exception:
            return False

    @staticmethod
    def calculate_all_hashes(
        file_path: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> dict:
        """
        Calculate all supported hash algorithms for a file

        Args:
            file_path: Path to the file
            progress_callback: Optional callback(bytes_processed, total_bytes)

        Returns:
            Dictionary with algorithm names as keys and hash values as values
        """
        results = {}

        for algorithm in ChecksumCalculator.ALGORITHMS.keys():
            try:
                results[algorithm] = ChecksumCalculator.calculate_file_hash(
                    file_path, algorithm, progress_callback
                )
            except Exception as e:
                results[algorithm] = f"Error: {str(e)}"

        return results

    @staticmethod
    def format_hash(hash_value: str, uppercase: bool = False) -> str:
        """
        Format hash value with optional uppercase

        Args:
            hash_value: Hash string
            uppercase: Convert to uppercase if True

        Returns:
            Formatted hash string
        """
        return hash_value.upper() if uppercase else hash_value.lower()

    @staticmethod
    def get_algorithm_display_name(algorithm: str) -> str:
        """Get display-friendly algorithm name"""
        return algorithm.upper()


def calculate_sha256(file_path: str) -> str:
    """
    Quick helper to calculate SHA-256 (most common)

    Args:
        file_path: Path to the file

    Returns:
        SHA-256 hash as hexadecimal string
    """
    return ChecksumCalculator.calculate_file_hash(file_path, 'SHA-256')


def verify_sha256(file_path: str, expected_hash: str) -> bool:
    """
    Quick helper to verify SHA-256

    Args:
        file_path: Path to the file
        expected_hash: Expected SHA-256 hash

    Returns:
        True if match, False otherwise
    """
    return ChecksumCalculator.verify_checksum(file_path, expected_hash, 'SHA-256')
