from app_factory import create_app
from activemq import start_exn_connector_in_background
from app_factory import create_app  # Import your Flask app factory

app = create_app()
# Start the EXN connector in the background
start_exn_connector_in_background()

if __name__ == '__main__':
    app.run(debug=True)