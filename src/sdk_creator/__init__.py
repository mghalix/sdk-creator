"""SDK creator utility package.

An abstraction that helps in creating your own wrappers SDKs of existing APIs.
"""

from . import errors
from .adapter import AsyncRestAdapter

__all__ = (
    "AsyncRestAdapter",
    "errors",
)
