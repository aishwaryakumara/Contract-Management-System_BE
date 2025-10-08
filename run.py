"""Flask application entry point"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )
