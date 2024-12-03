"""Shared test utilities."""

from pathlib import Path


class MockPath:
    """Mock Path object that supports sorting and string conversion."""

    def __init__(self, path_str, is_dir=True):
        self.path_str = path_str
        self._is_dir = is_dir
        self.name = Path(path_str).name
        self._path = Path(path_str)

    def __str__(self):
        return self.path_str

    def __repr__(self):
        return f"MockPath('{self.path_str}')"

    def __eq__(self, other):
        if isinstance(other, (MockPath, Path)):
            return str(self) == str(other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (MockPath, Path)):
            return str(self) < str(other)
        return NotImplemented

    def __hash__(self):
        return hash(self.path_str)

    def is_dir(self):
        return self._is_dir

    def exists(self):
        return True

    def __truediv__(self, other):
        return MockPath(str(self._path / other))
