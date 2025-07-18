def generate_tool_api_catalog(intent_name, method, url, params):
    return {
        intent_name: {
            "method": method,
            "url": url,
            "params": params
        }
    }