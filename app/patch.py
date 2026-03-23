"""Auto-patch pymobiledevice3 buffer size for Apple TV 4K screenshots.

Apple TV 4K screenshots are ~33MB, but pymobiledevice3's DTX reader has a
30MB buffer limit. This patches it to 64MB at runtime before any screenshot.
"""
def ensure_buffer_patched():
    """Patch MAX_BUFFERED_SIZE if needed. Safe to call multiple times."""
    try:
        from pymobiledevice3.dtx import _reader
        target = 64 * 1024 * 1024  # 64 MiB
        if _reader.MAX_BUFFERED_SIZE < target:
            _reader.MAX_BUFFERED_SIZE = target
    except ImportError:
        pass  # pymobiledevice3 not installed — screenshot won't work anyway
