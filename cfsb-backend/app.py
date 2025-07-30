import logging
import sys
from flask.logging import default_handler

# Add Flask's handler
logging.getLogger().addHandler(default_handler)

# Ensure the root logger is set to DEBUG
logging.getLogger().setLevel(logging.INFO)

from app_factory import create_app
from message_handler import start_exn_connector_in_background



app = create_app()
# Start the EXN connector in the background
start_exn_connector_in_background()

if __name__ == '__main__':
    print("Starting the application")
    # app.run(debug=True)
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False) # --no-reload in config