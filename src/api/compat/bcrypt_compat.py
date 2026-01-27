"""Compatibility patch for passlib with bcrypt>=4."""

try:
    import bcrypt

    if not hasattr(bcrypt, "__about__"):
        class _About:
            __version__ = getattr(bcrypt, "__version__", "unknown")

        bcrypt.__about__ = _About()

    if hasattr(bcrypt, "hashpw") and not hasattr(bcrypt, "_passlib_truncate_patch"):
        _orig_hashpw = bcrypt.hashpw

        def _hashpw_truncate(password, salt):
            if isinstance(password, (bytes, bytearray)) and len(password) > 72:
                password = password[:72]
            return _orig_hashpw(password, salt)

        bcrypt.hashpw = _hashpw_truncate
        bcrypt._passlib_truncate_patch = True
except Exception:
    # If bcrypt isn't available, passlib will fall back to other backends.
    pass

try:
    from passlib.handlers import bcrypt as passlib_bcrypt

    if hasattr(passlib_bcrypt, "detect_wrap_bug"):
        _orig_detect_wrap_bug = passlib_bcrypt.detect_wrap_bug

        def _safe_detect_wrap_bug(ident):
            try:
                return _orig_detect_wrap_bug(ident)
            except ValueError:
                # bcrypt>=4 raises for >72 byte secrets during detection.
                return False

        passlib_bcrypt.detect_wrap_bug = _safe_detect_wrap_bug
except Exception:
    # If passlib isn't available yet, this module is a no-op.
    pass
