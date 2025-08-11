#!/usr/bin/env python3
"""
Minimal test script to reproduce Hyperdrive DNS resolution issue.
This runs inside a Cloudflare Workers container.
"""

import json
import os
import sys
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
import psycopg2


class TestHandler(BaseHTTPRequestHandler):
    """HTTP handler for testing Hyperdrive connection."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/test":
            self.test_hyperdrive_connection()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Hyperdrive DNS Test Container\n\nEndpoint: /test")
    
    def test_hyperdrive_connection(self):
        """Test the Hyperdrive PostgreSQL connection."""
        print(f"[Container] test_hyperdrive_connection called at {self.path}")
        
        result = {
            "success": False,
            "hyperdrive_url": None,
            "error": None,
            "error_type": None,
            "traceback": None,
            "environment_vars": {},
            "headers_received": {}
        }
        
        try:
            # Log all environment variables (redacted)
            print("[Container] Environment variables:")
            for key, value in os.environ.items():
                if 'HYPERDRIVE' in key or 'DATABASE' in key or 'DB_' in key:
                    redacted = value[:20] + "..." if len(value) > 20 else value
                    result["environment_vars"][key] = redacted
                    print(f"  {key}: {redacted}")
            
            # Check headers for Hyperdrive URL (fallback method)
            hyperdrive_from_header = self.headers.get('X-Hyperdrive-URL')
            if hyperdrive_from_header:
                print(f"[Container] Found Hyperdrive URL in header: {hyperdrive_from_header[:50]}...")
                result["headers_received"]["X-Hyperdrive-URL"] = hyperdrive_from_header[:50] + "..."
            
            # Get Hyperdrive connection string from environment
            # In Cloudflare Workers containers, this should be injected
            hyperdrive_url = os.getenv("HYPERDRIVE_CONNECTION_STRING") or hyperdrive_from_header
            
            if not hyperdrive_url:
                print("[Container] ERROR: No Hyperdrive connection string found!")
                result["error"] = "HYPERDRIVE_CONNECTION_STRING not found in environment or headers"
                result["error_type"] = "EnvironmentError"
            else:
                # Log the connection string (first 50 chars for security)
                result["hyperdrive_url"] = hyperdrive_url[:50] + "..."
                
                print(f"[Container] Attempting PostgreSQL connection...")
                print(f"[Container] Connection string: {result['hyperdrive_url']}")
                
                # Parse the URL to log hostname
                from urllib.parse import urlparse
                parsed = urlparse(hyperdrive_url)
                print(f"[Container] Hostname: {parsed.hostname}")
                print(f"[Container] Port: {parsed.port or 5432}")
                
                # Attempt to connect - this is where the DNS error occurs
                print("[Container] Calling psycopg2.connect()...")
                conn = psycopg2.connect(hyperdrive_url)
                
                # If we get here, connection succeeded
                print("[Container] Connection established! Running test query...")
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()
                
                result["success"] = True
                result["database_version"] = version[0] if version else None
                
                cursor.close()
                conn.close()
                
                print(f"[Container] SUCCESS! Database version: {version[0] if version else 'Unknown'}")
                
        except psycopg2.OperationalError as e:
            # This is the expected error
            print(f"[Container] psycopg2.OperationalError caught!")
            print(f"[Container] Error message: {e}")
            result["error"] = str(e)
            result["error_type"] = "psycopg2.OperationalError"
            result["traceback"] = traceback.format_exc()
            
            # Check if it's the DNS error
            if "could not translate host name" in str(e):
                print("[Container] DNS RESOLUTION FAILURE CONFIRMED")
                print(f"[Container] Failed to resolve: {parsed.hostname if 'parsed' in locals() else 'unknown'}")
            
        except Exception as e:
            # Any other unexpected error
            print(f"[Container] Unexpected error: {type(e).__name__}")
            print(f"[Container] Error message: {e}")
            result["error"] = str(e)
            result["error_type"] = type(e).__name__
            result["traceback"] = traceback.format_exc()
        
        # Send response
        status_code = 200 if result["success"] else 500
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result, indent=2).encode())
    
    def log_message(self, format, *args):
        """Override to control logging."""
        print(f"{self.address_string()} - {format % args}")


def main():
    """Run the test HTTP server."""
    port = int(os.getenv("PORT", "8000"))
    server_address = ("", port)
    
    print(f"[Container] Starting Hyperdrive DNS test server on port {port}")
    print(f"[Container] Test endpoint: http://localhost:{port}/test")
    print(f"[Container] Python version: {sys.version}")
    print(f"[Container] psycopg2 version: {psycopg2.__version__}")
    
    httpd = HTTPServer(server_address, TestHandler)
    print("[Container] Server ready, waiting for requests...")
    httpd.serve_forever()


if __name__ == "__main__":
    main()