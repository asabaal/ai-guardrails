def parse_http_request_line(line: str) -> dict:
    """
    Parse an HTTP request line of the form 'METHOD PATH HTTP/VERSION'.
    Returns a dict with keys 'method', 'path', 'version'.
    Raises ValueError if the line is invalid.
    """
    if not isinstance(line, str):
        raise ValueError("Request line must be a string")
    parts = line.strip().split()
    if len(parts) != 3:
        raise ValueError("Request line must contain exactly three parts")
    method, path, version = parts
    allowed_methods = {"GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH", "TRACE", "CONNECT"}
    if method.upper() not in allowed_methods:
        raise ValueError(f"Unsupported HTTP method: {method}")
    if not path.startswith("/"):
        raise ValueError("Path must start with '/'")
    if not version.startswith("HTTP/"):
        raise ValueError("Version must start with 'HTTP/'")
    if version not in {"HTTP/1.0", "HTTP/1.1", "HTTP/2.0"}:
        raise ValueError(f"Unsupported HTTP version: {version}")
    return {"method": method.upper(), "path": path, "version": version}