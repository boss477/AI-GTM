def get_flask_session_secret(environ):
    """Return the configured Flask session key or fail closed."""
    secret = environ.get("FLASK_SECRET_KEY")
    if not secret or not secret.strip():
        raise RuntimeError("FLASK_SECRET_KEY must be set before starting the dashboard")
    return secret
