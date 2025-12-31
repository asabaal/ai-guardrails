def process_request(request):
    if not isinstance(request, dict):
        raise TypeError("request must be a dict")
    required_keys = {"method", "path"}
    missing = required_keys - request.keys()
    if missing:
        raise ValueError(f"Missing required keys: {missing}")
    method = request["method"]
    path = request["path"]
    params = request.get("params", {})
    if not isinstance(method, str):
        raise TypeError("method must be a string")
    if not isinstance(path, str):
        raise TypeError("path must be a string")
    if not isinstance(params, dict):
        raise TypeError("params must be a dict")
    for key in params.keys():
        if not isinstance(key, str):
            raise TypeError("param keys must be strings")
    sorted_params = sorted(params.items())
    return method, path, sorted_params