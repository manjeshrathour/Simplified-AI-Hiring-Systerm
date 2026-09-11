# API middleware
"""
API Middleware for request/response processing
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logger import log
import time
import json


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        # Start time
        start_time = time.time()
        
        # Log request
        log.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        log.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} Duration: {duration:.3f}s"
        )
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        current_time = time.time()
        
        # Initialize or clean old requests
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests outside window
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            log.warning(f"Rate limit exceeded for {client_ip}")
            return Response(
                content=json.dumps({
                    "error": "Rate limit exceeded. Please try again later."
                }),
                status_code=429,
                media_type="application/json"
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.max_requests - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(current_time + self.window_seconds)
        )
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle and log errors"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            log.error(f"Unhandled error: {e}", exc_info=True)
            return Response(
                content=json.dumps({
                    "error": "Internal server error",
                    "detail": str(e)
                }),
                status_code=500,
                media_type="application/json"
            )


class CORSHeadersMiddleware(BaseHTTPMiddleware):
    """Additional CORS headers middleware"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add additional security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request"""
    
    async def dispatch(self, request: Request, call_next):
        import uuid
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Add to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response