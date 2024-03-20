from app_factory import create_app
from dotenv import load_dotenv
from activemq import start_exn_connector_in_background
from activemqOLD import start_exn_connector_in_background1
from app_factory import create_app  # Import your Flask app factory

load_dotenv()

app = create_app()
# Start the EXN connector in the background
start_exn_connector_in_background()

if __name__ == '__main__':
    app.run(debug=True)