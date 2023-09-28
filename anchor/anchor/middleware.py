# anchor/middleware.py

class CustomHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add custom headers to responses here
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "text/plain"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        return response

