def validate_request(request: dict) -> bool:
    if not isinstance(request, dict):
        return False
    method = request.get('method')
    if not isinstance(method, str) or method.upper() not in {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'}:
        return False
    url = request.get('url')
    if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
        return False
    headers = request.get('headers', {})
    if not isinstance(headers, dict):
        return False
    for k, v in headers.items():
        if not isinstance(k, str) or not isinstance(v, str):
            return False
    body = request.get('body')
    if body is not None and not isinstance(body, (str, bytes)):
        return False
    return True