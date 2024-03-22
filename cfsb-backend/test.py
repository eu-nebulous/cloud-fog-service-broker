# ActiveMQ communication logic via EXN library
import sys
import threading
import json
import time
sys.path.insert(0,'../exn')
import logging
from dotenv import load_dotenv
load_dotenv()
from proton import Message
from exn import core
from exn.connector import EXN
from exn.core.consumer import Consumer
from exn.core.synced_publisher import SyncedPublisher
from exn.core.publisher import Publisher
from exn.core.context import Context
from exn.core.handler import Handler
from exn.handler.connector_handler import ConnectorHandler
from User_Functions import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('exn.connector').setLevel(logging.DEBUG)


class SyncedHandler(Handler):
    def on_message(self, key, address, body, message: Message, context=None):
        logging.info(f"[SyncedHandler] Received {key} => {address}: {body}")
        logging.info("on_message in SyncedHandler is executed")
        logging.info(f"[body] {body}")

        # Triggered by OPTIMIZER, Get app id, correlation id and filters
        # if address == "topic://eu.nebulouscloud.cfsb.get_node_candidates":
        if key == "OPT-triggering":
            logging.info("Entered in OPT-triggering Key")

            # Save the correlation_id (We do not have it from the app_side)
            # Optimizer_correlation_id = '88334290cad34ad9b21eb468a9f8ff11' # dummy correlation_id
            Optimizer_correlation_id = message.correlation_id
            logging.info(f"Optimizer_correlation_id {message.correlation_id}")
            application_id = message.subject # can be taken also from message.annotations.application

            try:
                opt_message_data = body
                print("Message from Optimizer:", opt_message_data)

                # Extract 'body' from opt_message_data
                # opt_body_data = opt_message_data.get('body', {})
                opt_body_data =[
                    {
                        "type": "NodeTypeRequirement",
                        "nodeTypes": ["EDGE"],
                        "jobIdForEDGE": "FCRnewLight0"
                    }
                ]
                logging.info(opt_body_data)
                print("Extracted body from Optim Message:", opt_body_data)

                ## Prepare message to be send to SAL
                RequestToSal = {
                    "metaData": {"user": "admin"},
                    "body": opt_body_data
                }
                print("RequestToSal:", RequestToSal)

                # Convert the Python structure to a JSON string
                # RequestToSal = json.dumps(RequestToSal)

                # Request the node candidates from SAL
                sal_reply = context.publishers['SAL-GET'].send_sync(RequestToSal, application_id,
                                                                    properties={'correlation_id': Optimizer_correlation_id}, raw=False)
                # sal_reply = context.publishers['SAL-GET'].send_sync(RequestToSal, application_id)
                if sal_reply:
                    logging.info(f"Received reply from SAL: {sal_reply}")
                    print("SAL reply:", sal_reply)
                else:
                    print("No reply from SAL!")

                ## Prepare message to be sent to OPTIMIZER
                CFSBResponse = read_dummy_response_data_toOpt('CFSB_Body_Response.json')

                # SAL_and_Scores_Body = Give me a short example
                # Encapsulate the data within the "body" structure
                # CFSBResponse = {
                #     "metaData": {"user": "admin"},
                #     "body": SAL_and_Scores_Body
                # }
                # print("CFSBResponse:", CFSBResponse)

                # Send message to Optimizer
                context.get_publisher('SendToOPT').send(CFSBResponse, application_id)
                # context.publishers['SendToOPT'].send(CFSBResponse, application_id, properties={
                #      'correlation_id': Optimizer_correlation_id}, raw=True)

            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse message body from Optimizer as JSON: {e}")

class Bootstrap(ConnectorHandler):
    context = None
    def ready(self, context: Context):
        self.context = context


def start_exn_connector_in_background():
    def run_connector():
        # eu.nebulouscloud.exn.sal.nodecandidate.*
        addressSAL_GET = 'eu.nebulouscloud.exn.sal.nodecandidate.get'

        addressSAL_GET_REPLY = 'eu.nebulouscloud.exn.sal.nodecandidate.get.reply'
        addressOPTtriggering = 'eu.nebulouscloud.cfsb.get_node_candidates'
        addressSendToOPT = 'eu.nebulouscloud.cfsb.get_node_candidates.reply'

        connector = EXN('ui', url="localhost", port=5672, username="admin", password="admin",
                        handler=Bootstrap(),
                        publishers=[
                            SyncedPublisher('SAL-GET', addressSAL_GET, True, True),
                            core.publisher.Publisher('SendToOPT', addressSendToOPT, True, True)
                        ],
                        consumers=[
                            # Consumer('SAL-GET-REPLY', addressSAL_GET, handler=SyncedHandler(), topic=True, fqdn=True),
                            Consumer('OPT-triggering', addressOPTtriggering, handler=SyncedHandler(), topic=True, fqdn=True)
                        ])
        connector.start()

    # Start the EXN connector in a separate thread
    thread = threading.Thread(target=run_connector)
    thread.daemon = True  # Daemon threads will shut down immediately when the program exits
    thread.start()


# Used to read dummy JSON and send to Optimizer
def read_dummy_response_data_toOpt(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    # Encapsulating the data within the "body" structure
    encapsulated_data = {
        "metaData": {"user": "admin"},
        "body": data
    }
    return encapsulated_data

