# log_ip_middleware.py
import logging

logger = logging.getLogger('core.middleware')

class LogIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the client's IP address from request.META
        ip_address_1 = request.META.get('REMOTE_ADDR', None)
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

        # You can also log more request-related information, like the User-Agent, etc.
        method = request.method
        url = request.get_full_path()
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')

        # Log the information
        logger.info(f"Incoming request from {ip_address} and proxy {ip_address_1} | Method: {method} | URL: {url} | User-Agent: {user_agent}")
        logger.debug(f"Debug message: {ip_address}")
        
        # Log some warning message if something goes wrong in the view
        if request.method == 'POST':
            logger.warning(f"POST request from {ip_address} | Method: {method} | URL: {url} | User-Agent: {user_agent}")

        # Call the next middleware or view
        response = self.get_response(request)
        return response
