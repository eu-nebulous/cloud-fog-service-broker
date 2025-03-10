import uuid
import json
import os
import time
import logging
import sys
import threading
from datetime import datetime
from proton import Message
from proton.reactor import Container
from exn.connector import EXN
from exn.core.synced_publisher import SyncedPublisher
from exn.core.consumer import Consumer
from exn.core.context import Context
from exn.handler.connector_handler import ConnectorHandler

project_root = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(project_root, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
LOG_FILE = os.path.join(logs_dir, "CFSB_Debug.log")


root_logger = logging.getLogger()
if root_logger.handlers:
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode='w', encoding="utf-8", delay=False)
    ]
)
logging.getLogger("proton").setLevel(logging.WARNING)

# Add the function here
def flush_logs():
    sys.stdout.flush()
    sys.stderr.flush()
    for handler in logging.getLogger().handlers:
        handler.flush()
        handler.close()


logging.info("✅ Logging system initialized!")
flush_logs()
sys.stdout.flush()
sys.stderr.flush()

for handler in logging.getLogger().handlers:
    handler.flush()

class CFSBTestHandler(ConnectorHandler):
    """ Handles responses from CFSB. """
    def __init__(self):
        super().__init__()
        self.responses = {}
        self.lock = threading.Lock()
        self.context = None  # Ensure context is set when ready

    def ready(self, context: Context):
        """ Called when the context is initialized. """
        self.context = context
        logging.info("✅ Handler is now ready and context is initialized.")


    # def on_message(self, key, address, body, message: Message, context=None):
    #     """ Handles incoming responses. """
    #     correlation_id = message.correlation_id
    #     logging.info(f"[RECEIVED] Message from {address}: {body} (Correlation ID: {correlation_id})")
    #     # logging.debug(f"Message details: {message}")
    #
    #     if correlation_id is None:
    #         logging.error("❌ Received message without correlation ID!")
    #         return
    #
    #     with self.lock:
    #         self.responses[correlation_id] = body
    #         logging.info(f"✅ Response stored for {correlation_id}: {body}")
    #
    #     try:
    #         message.ack()
    #         logging.info(f"✅ Acknowledged message with Correlation ID: {correlation_id}")
    #     except AttributeError:
    #         logging.warning(f"⚠️ Cannot acknowledge message: {correlation_id}")
    # def on_message(self, key, address, body, message: Message, context=None):
        # correlation_id = message.correlation_id
        # logging.info(f"[RECEIVED] Message from {address}: {body} (Correlation ID: {correlation_id})")
        # logging.debug(f"[DEBUG] Full message: {message}")
        #
        # if correlation_id is None:
        #     logging.error("❌ Received message without correlation ID!")
        #     return
        #
        # with self.lock:
        #     # Log before storing, to see what the dictionary contains
        #     logging.debug(f"Before storing, responses dict: {self.responses}")
        #     self.responses[correlation_id] = body
        #     logging.info(f"✅ Response stored for {correlation_id}: {body}")
        #
        # try:
        #     message.ack()
        #     logging.info(f"✅ Acknowledged message with Correlation ID: {correlation_id}")
        # except Exception as e:
        #     logging.error(f"⚠️ Error acknowledging message for {correlation_id}: {e}")
    def on_message(self, key, address, body, message: Message, context=None):
        correlation_id = message.correlation_id
        # logging.info(f"[RECEIVED] Message from {address}: {body} (Correlation ID: {correlation_id})")
        logging.debug(f"[DEBUG] Full message details: {message} | Properties: {message.properties}")

        if correlation_id is None:
            logging.error("❌ Received message without correlation ID!")
            return

        with self.lock:
            logging.debug(f"Before storing, responses dict: {self.responses}")
            self.responses[correlation_id] = body
            # logging.info(f"✅ Response stored for {correlation_id}: {body}")

        try:
            # message.ack()
            logging.info(f"✅ Acknowledged message with Correlation ID: {correlation_id}")
        except Exception as e:
            logging.error(f"⚠️ Error acknowledging message for {correlation_id}: {e}")



def send_request(correlation_id, request_id, handler):
    """ Sends a request message. """
    logging.info(f"🛫 Preparing to send request - Correlation ID: {correlation_id}, Request ID: {request_id}")
    if handler.context is None:
        logging.error("❌ [ERROR] Context is not initialized yet! Cannot send request.")
        return

    publisher = handler.context.publishers.get("OPT-Triggering-Multi", None)
    if not publisher:
        logging.error(f"❌ [ERROR] Publisher 'OPT-Triggering-Multi' not found! Available publishers: {handler.context.publishers.keys()}")
        return

    message = Message()
    message.correlation_id = correlation_id
    message.properties = {
        "request_id": request_id,
        "correlation_id": correlation_id
    }

    message_dict = {
        "correlation_id": correlation_id,
        "properties": message.properties,
        "body": "[[],[]]"
    }

    logging.info(f"✅ Sending request to ActiveMQ for Correlation ID {correlation_id}")

    publisher.send(message_dict, correlation_id, properties=message.properties, raw=True)

    logging.info(f"📤 Request sent - Correlation ID: {correlation_id}")
    sys.stdout.flush()
    sys.stderr.flush()

def wait_for_context(handler, timeout=30):  # Increased timeout
    """ Wait until the handler's context is initialized, up to a timeout. """
    logging.info("⌛ Waiting for context to be initialized...")
    start_time = time.time()

    while handler.context is None:
        if time.time() - start_time > timeout:
            logging.error("❌ [ERROR] Context initialization timeout! Exiting.")
            return False
        time.sleep(1)  # Increase wait interval

    logging.info("✅ Context initialized successfully.")
    return True

def main():
    # ActiveMQ Connection Info
    BROKER_URL = os.getenv("NEBULOUS_BROKER_URL", "amqp://localhost:5672")
    BROKER_USER = os.getenv("NEBULOUS_BROKER_USERNAME", "admin")
    BROKER_PASS = os.getenv("NEBULOUS_BROKER_PASSWORD", "admin")

    # Initialize handler and connector
    handler = CFSBTestHandler()
    connector = EXN(
        "test_client",
        url=BROKER_URL,
        port=5672,
        username=BROKER_USER,
        password=BROKER_PASS,
        handler=handler,
        publishers=[
            SyncedPublisher("OPT-Triggering-Multi", "eu.nebulouscloud.cfsb.get_node_candidates_multi", True, True)
        ],
        consumers=[
            Consumer("OPT-Triggering-Multi", "eu.nebulouscloud.cfsb.get_node_candidates_multi.reply", handler=handler, topic=True, fqdn=True)  # Try topic=False if needed
        ]

    )

    # Start the connector in a separate thread
    threading.Thread(target=connector.start, daemon=True).start()

    # Ensure the context is ready
    if not wait_for_context(handler):
        logging.error("❌ [ERROR] Exiting because context was not initialized.")
        return

    # Generate two unique correlation IDs
    correlation_id_1 = "A"
    request_id_1 = "A"
    correlation_id_2 = "B"
    request_id_2 = "B"

    # Send two requests
    send_request(correlation_id_1, request_id_1, handler)
    time.sleep(0.5)
    send_request(correlation_id_2, request_id_2, handler)

    # Wait for a maximum of 30 seconds for responses
    max_wait_time = 30  # Maximum time to wait for responses
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        response_1 = handler.responses.get(correlation_id_1, None)
        response_2 = handler.responses.get(correlation_id_2, None)

        if response_1 and response_2:
            break  # Stop waiting if both responses are received

        logging.info(f"⌛ Waiting for responses... {int(time.time() - start_time)}s elapsed")
        time.sleep(1)

    # Check final responses
    response_1 = handler.responses.get(correlation_id_1, None)
    response_2 = handler.responses.get(correlation_id_2, None)

    # logging.info(f"📥 Final Response 1: {response_1}")
    # logging.info(f"📥 Final Response 2: {response_2}")

    if response_1 is None or response_2 is None:
        logging.error("🔴 Issue detected! One or both responses are missing!")
    elif (isinstance(response_1, dict) and response_1.get("message") == "No resources returned from SAL 1") or \
            (isinstance(response_2, dict) and response_2.get("message") == "No resources returned from SAL 2"):
        logging.error("🔴 Issue detected! One request returned 'No resources returned from SAL'.")
    else:
        logging.info("✅ Both requests returned valid responses.")


    logging.info("✅ CFSB Test Completed. Exiting now.")
    flush_logs()



if __name__ == "__main__":
    logging.info("🚀 CFSB Test Started.")
    main()
