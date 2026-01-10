import os
import subprocess
from typing import List

class AudioProcessor:
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Returns the file size in bytes."""
        if not os.path.exists(file_path):
            return 0
        return os.path.getsize(file_path)

    @staticmethod
    def is_under_limit(file_path: str, limit_mb: int = 20) -> bool:
        """Checks if the file size is under the specified limit in MB."""
        size_bytes = AudioProcessor.get_file_size(file_path)
        limit_bytes = limit_mb * 1024 * 1024
        return size_bytes < limit_bytes
