class CustomHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if the request path matches the stellar.toml file
        if request.path == '/.well-known/stellar.toml':
            # Set custom headers for the stellar.toml file
            response['Access-Control-Allow-Origin'] = '*'
            response['Content-Type'] = 'text/plain'
        
        return response

        
