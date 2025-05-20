import logging
import traceback
from django.http import HttpResponse

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Log the full exception with traceback
            logger.error(f"Unhandled exception in request: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Return a simple error response that will help debug
            return HttpResponse(
                f"""
                <html>
                <head><title>CodeX - Error Occurred</title></head>
                <body>
                    <h1>CodeX is experiencing an error</h1>
                    <p>We've detected an issue and our team has been notified.</p>
                    <div style="background-color: #f8f8f8; padding: 10px; border: 1px solid #ddd; margin-top: 20px;">
                        <h3>Error Details (DEBUG mode)</h3>
                        <p>{str(e)}</p>
                        <pre>{traceback.format_exc()}</pre>
                    </div>
                </body>
                </html>
                """,
                content_type='text/html',
                status=500
            )
