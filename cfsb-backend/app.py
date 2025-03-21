from app_factory import create_app
from activemq import start_exn_connector_in_background

app = create_app()
# Start the EXN connector in the background
start_exn_connector_in_background()

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False) # --no-reload in config