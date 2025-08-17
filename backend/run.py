#!/usr/bin/env python3
"""
Main application runner for the coding challenge platform backend.
"""

import os
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting Flask application on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    app.run(host=host, port=port, debug=debug)