"""
mcp_python_streamable_e2e_test_template package.

Provides the package version via ``__version__``. Falls back to a
development value when the distribution metadata is not available
(e.g. when running from source without installation).
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__: str = _version("mcp-python-streamable-e2e-test-template")
except PackageNotFoundError:  # pragma: no cover – not installed
    __version__ = "0.0.0.dev0"

__all__: list[str] = ["__version__"]