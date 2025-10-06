# ActiveMQ Communication Logic
import sys
import logging
import threading
import uuid
sys.path.insert(0, '../exn')
import get_data
from dotenv import load_dotenv
load_dotenv()
from proton import Message
from exn import core
from exn.connector import EXN
from exn.core.consumer import Consumer
from exn.core.synced_publisher import SyncedPublisher
from exn.core.context import Context
from exn.core.handler import Handler
from exn.handler.connector_handler import ConnectorHandler
from node_functions import *
from node_evaluation import perform_evaluation
import os

import time
from proton import Message

VALID_AWS_INSTANCE_TYPES ="g2.2xlarge, c6a.24xlarge, g5.2xlarge, r7iz.12xlarge, g6.24xlarge, m4.4xlarge, m5ad.12xlarge, u7i-6tb.112xlarge, m6idn.large, i3en.3xlarge, r6in.24xlarge, c3.large, c4.4xlarge, t2.2xlarge, m6id.xlarge, c6a.16xlarge, r6a.2xlarge, r3.large, r7iz.8xlarge, r5.24xlarge, i7ie.18xlarge, d3en.2xlarge, m5n.16xlarge, m6id.2xlarge, r7a.2xlarge, x1e.2xlarge, m6a.2xlarge, r6a.metal, m5zn.2xlarge, m7i-flex.12xlarge, r5dn.8xlarge, c5ad.24xlarge, c6in.24xlarge, r5a.2xlarge, r7iz.16xlarge, r6id.16xlarge, g6e.48xlarge, f1.2xlarge, c6in.xlarge, r5n.12xlarge, r6a.xlarge, c7i.2xlarge, r7a.xlarge, c5n.2xlarge, m7i.metal-24xl, g6e.8xlarge, x2iedn.2xlarge, r6idn.16xlarge, m7i.16xlarge, i3en.12xlarge, i7ie.24xlarge, inf2.48xlarge, i4i.16xlarge, g5.4xlarge, c6id.8xlarge, c6i.32xlarge, x1e.8xlarge, t1.micro, x2iezn.4xlarge, m2.4xlarge, r5a.xlarge, r6i.xlarge, m5a.16xlarge, c7a.xlarge, trn1.32xlarge, m5a.2xlarge, c3.8xlarge, m5dn.12xlarge, r6in.metal, m5d.xlarge, i3en.24xlarge, r6id.12xlarge, x2iedn.xlarge, c5ad.12xlarge, i7ie.xlarge, m6id.32xlarge, c6i.2xlarge, r7iz.xlarge, m7i.8xlarge, m5zn.6xlarge, m5zn.large, m6idn.12xlarge, r7a.4xlarge, r6idn.xlarge, m6idn.4xlarge, r3.8xlarge, r6in.12xlarge, inf2.8xlarge, z1d.2xlarge, trn1n.32xlarge, m5dn.2xlarge, d3en.8xlarge, t3a.2xlarge, c4.8xlarge, m5ad.large, c6i.4xlarge, trn1.2xlarge, m7a.xlarge, c7a.large, c7i-flex.16xlarge, c7a.medium, r6idn.8xlarge, c5.4xlarge, i4i.24xlarge, m6a.large, i2.2xlarge, m5d.8xlarge, r5b.12xlarge, m6id.12xlarge, c5d.large, c7i-flex.8xlarge, r7a.32xlarge, x1e.32xlarge, r6id.xlarge, c6id.24xlarge, m7i.2xlarge, m5.24xlarge, c6a.48xlarge, m6i.24xlarge, c6i.8xlarge, c7i.8xlarge, m5.12xlarge, c5n.large, c6i.large, m7i.24xlarge, x1.16xlarge, d2.8xlarge, r6idn.2xlarge, c6a.32xlarge, m7i-flex.2xlarge, r4.16xlarge, r6id.2xlarge, m5dn.large, m6i.large, r7iz.32xlarge, c5ad.4xlarge, m5a.4xlarge, m5.8xlarge, r5ad.24xlarge, m5ad.4xlarge, c5d.12xlarge, c7i-flex.2xlarge, r7i.metal-48xl, c7a.metal-48xl, u7i-12tb.224xlarge, c6in.12xlarge, p2.8xlarge, m5d.16xlarge, m6in.12xlarge, r5a.16xlarge, m5d.large, m5d.metal, c5n.4xlarge, r5b.metal, c6id.large, x2idn.24xlarge, m6in.32xlarge, g6.8xlarge, i7ie.3xlarge, r5n.4xlarge, g4dn.12xlarge, r6id.4xlarge, g6.48xlarge, m5.xlarge, c7a.2xlarge, m2.2xlarge, c6in.16xlarge, c5ad.16xlarge, c7a.4xlarge, g4ad.8xlarge, g4ad.2xlarge, c5a.4xlarge, t3.2xlarge, u-3tb1.56xlarge, g5.24xlarge, g4dn.metal, m6in.16xlarge, r6i.24xlarge, m5.metal, i4i.4xlarge, m5dn.xlarge, r5ad.8xlarge, r5ad.12xlarge, inf1.xlarge, m7a.32xlarge, r7a.large, m7a.16xlarge, t3.medium, r7a.medium, m6a.metal, m6in.24xlarge, t3.xlarge, z1d.xlarge, c5.xlarge, r5a.large, i7ie.12xlarge, r6idn.24xlarge, c6i.24xlarge, g4ad.4xlarge, r7iz.metal-16xl, r6a.12xlarge, d3.8xlarge, d2.2xlarge, m5ad.2xlarge, c5a.12xlarge, x2iezn.8xlarge, r7i.16xlarge, t3a.small, r5a.12xlarge, r6a.32xlarge, r6in.large, c5d.2xlarge, m5ad.8xlarge, g6e.16xlarge, m6i.8xlarge, i4i.metal, m5dn.8xlarge, r6i.4xlarge, c4.large, m6idn.xlarge, r7i.2xlarge, p3.2xlarge, d3en.4xlarge, r5b.large, r5ad.large, c6a.8xlarge, c5n.9xlarge, d3.2xlarge, m7i.48xlarge, x2iedn.metal, r5.large, r5n.16xlarge, vt1.6xlarge, c7a.12xlarge, h1.2xlarge, u-12tb1.112xlarge, c7i.16xlarge, vt1.3xlarge, c5ad.xlarge, r5.4xlarge, r5b.24xlarge, m6i.metal, c7a.8xlarge, h1.8xlarge, m6i.16xlarge, c6in.8xlarge, c6i.16xlarge, c7i-flex.4xlarge, r5dn.xlarge, m5zn.3xlarge, t3.large, r7i.8xlarge, g6e.12xlarge, m5n.12xlarge, m4.xlarge, t2.micro, r7i.12xlarge, m5n.8xlarge, r5d.4xlarge, c7i-flex.xlarge, c5.12xlarge, inf1.6xlarge, c5a.2xlarge, c5d.24xlarge, t3a.medium, r6a.8xlarge, c6a.12xlarge, i7ie.48xlarge, r5.metal, i4i.2xlarge, c6in.2xlarge, c5a.24xlarge, c6id.16xlarge, u7in-24tb.224xlarge, r3.2xlarge, r6id.32xlarge, d3.xlarge, c7i.metal-24xl, r3.4xlarge, t2.large, m4.large, c7i.xlarge, c5a.xlarge, inf2.24xlarge, c7i.large, r5a.4xlarge, u-6tb1.56xlarge, inf1.2xlarge, m6i.32xlarge, c4.2xlarge, m6in.4xlarge, c7i.24xlarge, m5zn.12xlarge, r7a.24xlarge, m6a.4xlarge, m5d.24xlarge, m5n.metal, c5.metal, c3.xlarge, m5n.large, r7i.metal-24xl, r6a.48xlarge, u-24tb1.112xlarge, d3en.6xlarge, r5d.large, c5ad.2xlarge, i2.xlarge, u-6tb1.112xlarge, r5.16xlarge, c7i-flex.12xlarge, m6in.metal, m5.4xlarge, r5n.24xlarge, m3.xlarge, m5n.4xlarge, c6id.32xlarge, x2idn.metal, c5.24xlarge, g5.12xlarge, r6a.4xlarge, r5d.xlarge, c7i-flex.large, r5b.4xlarge, m6i.4xlarge, h1.4xlarge, r5d.16xlarge, t3.nano, m5dn.metal, r5dn.metal, c5d.18xlarge, c5.9xlarge, m6idn.32xlarge, m4.16xlarge, m1.xlarge, u7in-16tb.224xlarge, c6in.large, m5a.8xlarge, r7iz.2xlarge, r5n.2xlarge, r4.2xlarge, m7a.medium, p5.48xlarge, c5n.18xlarge, r5d.24xlarge, c5d.4xlarge, x2iezn.12xlarge, p4d.24xlarge, m5zn.metal, r5dn.large, r5b.2xlarge, r6in.32xlarge, r6id.24xlarge, c6a.metal, r5d.2xlarge, h1.16xlarge, r5b.xlarge, c6id.metal, r7i.large, r5dn.12xlarge, t3.micro, m6id.metal, g6.xlarge, i2.8xlarge, x2idn.16xlarge, r5d.8xlarge, c4.xlarge, inf2.xlarge, m7a.4xlarge, m6in.large, c7a.24xlarge, r5b.16xlarge, g6.2xlarge, c7a.48xlarge, m6id.16xlarge, m6idn.2xlarge, g5.16xlarge, m7a.48xlarge, c5a.16xlarge, m5.16xlarge, t3a.large, m7a.8xlarge, z1d.metal, r6i.12xlarge, m6a.16xlarge, r3.xlarge, g4dn.xlarge, x1e.16xlarge, r5.8xlarge, r6idn.large, r6in.4xlarge, z1d.12xlarge, r5.xlarge, m4.2xlarge, c6in.32xlarge, r7a.metal-48xl, i3.xlarge, r6in.8xlarge, r6idn.4xlarge, i3.large, m7i-flex.16xlarge, r6i.16xlarge, r7i.xlarge, c6a.xlarge, m7a.12xlarge, m3.2xlarge, t2.medium, c6a.4xlarge, c5.large, u7i-8tb.112xlarge, m6idn.24xlarge, c5n.metal, m7a.24xlarge, c7i.metal-48xl, c7a.16xlarge, m7i-flex.4xlarge, m6idn.metal, r5ad.2xlarge, m5ad.24xlarge, x2iedn.4xlarge, i2.4xlarge, m6in.xlarge, r4.xlarge, c7a.32xlarge, r5dn.16xlarge, r5ad.16xlarge, m5ad.xlarge, c3.4xlarge, i4i.large, r6a.24xlarge, r6id.large, m7a.2xlarge, m5n.2xlarge, g4dn.16xlarge, r4.8xlarge, vt1.24xlarge, x1e.xlarge, r6idn.metal, m5.large, r5d.metal, m5dn.4xlarge, c5ad.8xlarge, t2.xlarge, x2iezn.6xlarge, c7i.12xlarge, m5a.large, c3.2xlarge, m7i.xlarge, m5zn.xlarge, g6e.4xlarge, c5d.xlarge, m5d.12xlarge, c7i.4xlarge, i3.16xlarge, x2iedn.16xlarge, m5n.24xlarge, d2.4xlarge, r4.large, r5ad.xlarge, p3.16xlarge, c5.2xlarge, r6i.metal, z1d.large, m5.2xlarge, r5.2xlarge, m4.10xlarge, i4i.12xlarge, m5dn.16xlarge, r5n.8xlarge, x2idn.32xlarge, g5.xlarge, c5d.metal, i3en.2xlarge, r7i.24xlarge, i3.8xlarge, r6idn.32xlarge, r5.12xlarge, m5n.xlarge, c6id.12xlarge, m6idn.8xlarge, g4ad.16xlarge, r7iz.metal-32xl, r7a.8xlarge, r5n.xlarge, r6id.8xlarge, x2iezn.metal, g6.12xlarge, c5a.8xlarge, m7i.large, f2.48xlarge, r5ad.4xlarge, z1d.6xlarge, m6i.xlarge, m5dn.24xlarge, m6id.4xlarge, x2iedn.24xlarge, r6id.metal, x2iezn.2xlarge, r6in.16xlarge, dl1.24xlarge, g6.16xlarge, m7i-flex.8xlarge, r6a.16xlarge, c6in.4xlarge, m5d.2xlarge, c5ad.large, i4i.32xlarge, x1.32xlarge, r6i.8xlarge, m6id.24xlarge, c6id.4xlarge, g6.4xlarge, m5a.xlarge, m6idn.16xlarge, r7a.12xlarge, m6id.8xlarge, m5a.24xlarge, p2.xlarge, m3.medium, m7i.12xlarge, c6a.2xlarge, r6i.32xlarge, r7a.16xlarge, i3.4xlarge, gr6.4xlarge, m7i-flex.large, t3.small, inf1.24xlarge, m6id.large, c6id.xlarge, gr6.8xlarge, r5b.8xlarge, m2.xlarge, m7i.4xlarge, u-18tb1.112xlarge, c6i.metal, i3en.large, r6a.large, g5.48xlarge, m6in.8xlarge, x2iedn.32xlarge, m6a.24xlarge, r7i.48xlarge, f2.12xlarge, m6a.xlarge, m5ad.16xlarge, t2.nano, m3.large, c6id.2xlarge, r5a.24xlarge, m6a.32xlarge, d3.4xlarge, i3.2xlarge, c6i.12xlarge, m6in.2xlarge, m6a.8xlarge, r6idn.12xlarge, x1e.4xlarge, r5a.8xlarge, g6e.xlarge, g6e.2xlarge, p3.8xlarge, t2.small, r5d.12xlarge, r5dn.2xlarge, c6i.xlarge, i4i.xlarge, t3a.nano, i3.metal, p2.16xlarge, u7in-32tb.224xlarge, g5.8xlarge, m7a.metal-48xl, x2iedn.8xlarge, i3en.xlarge, r5dn.4xlarge, r6in.xlarge, m6a.12xlarge, r7i.4xlarge, g6e.24xlarge, c5n.xlarge, r6i.large, g4dn.2xlarge, d3en.12xlarge, d3en.xlarge, c5.18xlarge, g4dn.4xlarge, r7iz.large, m7i.metal-48xl, r7a.48xlarge, i3en.6xlarge, m7a.large, i3en.metal, r5n.large, r7iz.4xlarge, p3dn.24xlarge, i7ie.large, m7i-flex.xlarge, u-9tb1.112xlarge, m1.small, i4i.8xlarge, m6i.2xlarge, g4dn.8xlarge, i7ie.2xlarge, r5dn.24xlarge, c6in.metal, f1.16xlarge, r6in.2xlarge, t3a.xlarge, t3a.micro, c5a.large, m5a.12xlarge, f1.4xlarge, r4.4xlarge, d2.xlarge, m6a.48xlarge, c5d.9xlarge, m1.medium, g4ad.xlarge, m6i.12xlarge, c7i.48xlarge, r5n.metal, m1.large, m5d.4xlarge, c6a.large, r6i.2xlarge, z1d.3xlarge, i7ie.6xlarge"

logging.getLogger('exn.connector').setLevel(logging.CRITICAL)
# log_lock = threading.Lock() # Global lock for logging

class SyncedHandler(Handler):
    def __init__(self):
        super().__init__()  # Ensure parent class is initialized
        self.responses = {}  # Initialize responses dictionary
        self.lock = threading.Lock()  # Initialize lock for thread safety
        self.processed_requests = set()

    def on_message(self, key, address, body, message: Message, context=None):
        # Check if the message is a heartbeat
        if message.subject == "heartbeat":
            print("Received heartbeat message; ignoring it...")
            return  # Skip further processing for heartbeat messages
        # Triggered by OPTIMIZER, Get app id, correlation id and filters
        print_start_message()  # Print CFSB initialization message
        try:
            # Use correlation_id if exists, else generate one and Set Request ID
            request_id = message.correlation_id or uuid.uuid4().hex
            # Store it in the message properties for later reference
            message.correlation_id = request_id  # Ensuring uniformity in logs
            print(f"[Processing] Request ID: {request_id}")
            self.process_optimizer_message(request_id, key, body, message, context)
        except Exception as e:
            print(f"[ERROR] Exception in `on_message()`: {e}")
            logging.error(f"[ERROR] Exception in `on_message()`: {e}")

    def process_optimizer_message(self, request_id, key, body, message, context):
        """
        Processes an incoming message from the optimizer, ensuring the same request ID is used throughout.
        """
        print(f"Whole Message Sent from Optimizer [{key}]:", body)

        # Extract Application ID (Set dummy if missing)
        application_id_optimizer = message.subject or 'dummy-application-id-123'

        # Extract and process body
        body_sent_from_optimizer = body.get('body', [])
        if isinstance(body_sent_from_optimizer, str):
            try:
                body_sent_from_optimizer = json.loads(body_sent_from_optimizer)
            except json.JSONDecodeError:
                print(f"ERROR: body_sent_from_optimizer is not valid JSON! Request ID: {request_id}")
                body_sent_from_optimizer = []

        print(f"Extracted Body from Optimizer Message [Request ID: {request_id}]:", body_sent_from_optimizer)
        print("-------------------------------------------------")

        # **Ensure only one request is processed at a time**
        with self.lock:
            print(f"[Processing] Request ID: {request_id}, App ID: {application_id_optimizer}")

            # Handle Multi or Single requests
            if isinstance(body_sent_from_optimizer, list):
                if body_sent_from_optimizer and isinstance(body_sent_from_optimizer[0], list): # Multiple Lists
                    print(f"[Request {request_id}] The Request contains Multiple Lists")
                    print(f"-------------------------------------------------")
                    try:
                        # Ensure all arguments are correctly passed, including context
                        self.handle_multi(application_id_optimizer, request_id, body_sent_from_optimizer, context)
                    except Exception as e:
                        # print(f"Before Exception {body_sent_from_optimizer}")
                        print(f"Exception in handle_multi [Request ID: {request_id}]: {e}")
                else: # Single List
                    print(f"[Request {request_id}] The Request contains a Single List or an Empty List")
                    print("-------------------------------------------------")
                    body_sent_from_optimizer = json.dumps(body_sent_from_optimizer)  # Convert to JSON string
                    try:
                        self.handle_single(application_id_optimizer, request_id, body_sent_from_optimizer, context)
                    except Exception as e:
                        print(f"Exception in handle_single [Request ID: {request_id}]: {e}")

    def handle_single(self, application_id_optimizer, correlation_id_optimizer, body_json_string, context):
        request_id = correlation_id_optimizer
        print(f"Entered handle_single - Request ID: {request_id}, App ID: {application_id_optimizer}")
        feasibility = False

        try:
            ## Prepare message to be send to SAL - remove locations if needed
            body_json_string, locations = remove_request_attribute('CFSB-datasource-geolocations', json.loads(body_json_string))
            if locations:
                body_json_string = json.dumps(body_json_string)  # Convert the body data to a JSON string

            RequestToSal = {  # Dictionary
                "metaData": {"user": "admin"},  # key [String "metaData"] value [dictionary]
                "body": body_json_string  # key [String "body"] value [JSON String]
            }
            print(f"[Request {request_id}] Sending to SAL: {RequestToSal}")
            sal_reply = context.publishers['SAL-GET'].send_sync(RequestToSal)
            if sal_reply is None:
                context.get_publisher('SendToOPTMulti').send({"success": False, "message": "SAL-GET request failed"},
                                                             application_id_optimizer,
                                                             properties={'correlation_id': correlation_id_optimizer},
                                                             raw=True)
                print(f"[Request {request_id}] SAL-GET request failed")
                return

            print(f"[Request {request_id}] Received response from SAL")

            # Test possible problematic response from SAL or Server
            # sal_reply = {
            #     'when': '2025-05-29T14:53:50.398298Z',
            #     'body': '{"key":"gateway-server-exception-error","message":" Request processing failed; nested exception is java.lang.NullPointerException</p><p><b>Description</b> The server encountered an unexpected condition that prevented it from fulfilling the request."}',
            #     'metaData': {
            #         'user': 'admin',
            #         'status': 500,  # Note: just use int directly
            #         'protocol': 'HTTP'
            #     }
            # }

            status = sal_reply.get('metaData', {}).get('status', None)

            if sal_reply and status == 200:
                sal_body = sal_reply.get('body')
                try:
                    # Parse the JSON string to a Python object
                    nodes_data = json.loads(sal_body)
                    # print(nodes_data)
                    # Check if there is any error in SAL's reply body
                    if 'key' in nodes_data and any(
                            keyword in nodes_data['key'].lower() for keyword in ['error', 'exception']):
                        print("Error found in SAL's message body:", nodes_data['message'])
                        sal_reply_body = '' # Make it an Empty string in case of error
                    else:  # No error found in SAL's reply body
                        total_nodes = len(nodes_data)  # Get the total number of nodes
                        sal_reply_body = sal_body # Keep sal_reply_body as is since it's already a JSON string
                        # print("Total Nodes in SAL's reply:", total_nodes)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON reply from SAL: {e}")

                if sal_reply_body.strip() not in ('', '[]'): # Check whether SAL's reply body is empty
                    # print("SAL reply Body:", sal_reply_body)
                    # print(type(sal_reply_body))  # Check the data type
                    # print(f"Raw content: {repr(sal_reply_body)}")

                    # Check the number of nodes before Evaluation
                    if total_nodes > 1:
                        # Search for application_id, Read JSON and create data to pass to Evaluation
                        if check_json_file_exists(application_id_optimizer):  # Application JSON exists
                            print("-------------------------------------------------")
                            print(f"JSON file for application ID {application_id_optimizer} exists.")

                            # The read_application_data returns int the app_data the policy from the saved file, in order to check it to do the convert or not.
                            app_data, selected_criteria, provider_criteria, relative_wr_data, immediate_wr_data = read_application_data(application_id_optimizer)
                            extracted_data_SAL, node_ids, node_names, providers, filtered_nodes_message = extract_SAL_node_candidate_data(sal_reply_body, app_data, application_id_optimizer, selected_criteria, correlation_id_optimizer)
                            data_table = create_data_table(extracted_data_SAL, selected_criteria, provider_criteria, locations)
                            # print("relative_wr_data:", relative_wr_data)
                            # print("immediate_wr_data:", immediate_wr_data)
                        else:  # Application does not exist in directory
                            print("-------------------------------------------------")
                            print(f"JSON file for application ID {application_id_optimizer} does not exist.")
                            # Use the create_criteria_mapping() to get the criteria mappings
                            # selected criteria must be a list of dictionaries like when reading it from file
                            json_selected_criteria = {
                                "selectedCriteria": [
                                    {
                                        "name": "attr-performance-capacity-num-of-cores",
                                        "type": 2,
                                        "title": "Number of CPU Cores"
                                    },
                                    {
                                        "name": "attr-performance-capacity-memory",
                                        "type": 2,
                                        "title": "Memory Size"
                                    }
                                ]
                            }
                            # check if distance was asked by optimizer
                            if locations:
                                distance_item = {
                                    "name": "9f5706e3-08bd-412d-8d59-04f464e867a8",
                                    "type": 2,
                                    "title": "Proximity to Data Source"
                                }
                                json_selected_criteria["selectedCriteria"].append(distance_item)
                            selected_criteria = {criterion['title']: criterion for criterion in json_selected_criteria.get('selectedCriteria', [])}
                            app_data = {"app_specific": 1}
                            extracted_data_SAL, node_ids, node_names, providers, filtered_nodes_message = extract_SAL_node_candidate_data(
                                sal_reply_body, app_data, application_id_optimizer, selected_criteria, correlation_id_optimizer)

                            # Create data_table:
                            # provider_criteria do not exist when the application file does not exist. None is treated like false
                            data_table = create_data_table(extracted_data_SAL, selected_criteria, None, locations)
                            # print(data_table)
                            relative_wr_data = []
                            immediate_wr_data = []
                            # create default app_data dictionary for policy and app_specific when file not exists for the application
                            app_data = {'policy': '0', 'app_specific': True}

                        # Check the number of nodes before Evaluation
                        print("There are " + str(len(node_ids)) + " nodes for Evaluation")
                        if len(node_ids) == 0:
                            feasibility = False
                            Message_Results = {
                                "message": filtered_nodes_message
                            }
                        else:
                            # Convert the original data of RAM and # of Cores, e.g. 1/X, if they are selected
                            # print("Original data_table:", data_table)
                            # TODO: INCORPORATE THIS INTO create_data_table function
                            if (app_data['policy'] == '0'):
                                data_table = convert_data_table(data_table)  # Convert RAM and # of Cores, e.g. 1/X
                                # print("Converted data_table:", data_table)
                            else:
                                print("Policy is MAX for this application")

                            ## Run evaluation
                            evaluation_results = perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_names,
                                                                    node_ids)
                            # print("Evaluation Results:", evaluation_results)

                            if evaluation_results.get('LPstatus') == 'feasible':
                                feasibility = True
                                ## Extract and Save the Results
                                ScoresAndRanks = evaluation_results.get('results', [])
                                # Sort scores and ranks to order first the best nodes
                                ScoresAndRanks = sorted(ScoresAndRanks, key=lambda x: x['Score'], reverse=True)
                                # Check the length and truncate if necessary
                                if len(ScoresAndRanks) > 250:
                                    print("Evaluated Nodes: ", len(ScoresAndRanks))
                                    ScoresAndRanks = ScoresAndRanks[:250]
                                    # print("Remaining Nodes: ", len(ScoresAndRanks))
                                # print("Scores and Ranks:", ScoresAndRanks)

                                # Append the Score and Rank of each node to SAL's Response
                                Message_Results = append_evaluation_results(sal_reply_body, ScoresAndRanks)
                                Message_Results = sorted(Message_Results, key=lambda x: x['rank'], reverse=False)
                                #  print("Message_Results:", Message_Results)
                            else:
                                # problem is infeasible
                                feasibility = False
                                results = evaluation_results.get('results')
                                Message_Results = results  # Message_Results variable may contain info about the infeasible case also

                    else:  # SAL returned only one node, thus no evaluation needed
                        feasibility = True
                        print("There is only one node!")
                        # Append the Score and Rank of each node to SAL's Response
                        Message_Results = append_evaluation_results(sal_reply_body, [])

                else:  # Then SAL's reply body is empty send an empty body to Optimizer
                    print("No Body in reply from SAL!")
                    Message_Results = {
                        "message": "No resources returned from SAL"
                    }

            else: # Status <> 200 or sal_reply is  None or sal_reply == ''
                Message_Results = {
                    "message": status
                }

            ## Prepare message to be sent to OPTIMIZER
            try: # Measure the size of the message in bytes and MB
                message_str = json.dumps(Message_Results)
                message_bytes = message_str.encode('utf-8')
                message_size_bytes = len(message_bytes)
                message_size_mb = message_size_bytes / (1024 * 1024)  # Convert bytes to MB
                print(f"Message Size: {message_size_bytes} bytes ({message_size_mb:.2f} MB)")
            except Exception as e:
                print("Error measuring message size:", e)

            # Check against the 104857600 bytes limit (~100 MB) of ActiveMQ
            if message_size_bytes > 104857600:
                print(f"Message size exceeds limit of 104857600 bytes (100 MB). Message not sent.")
                Message_Results = {
                    "message": "The message size exceeds limit of 104857600 bytes (100 MB) imposed by ActiveMQ"
                }

            CFSBResponse = {
                    "metaData": {"user": "admin"},
                    "body": Message_Results
            }
            ## Send message to OPTIMIZER
            context.get_publisher('SendToOPT').send(CFSBResponse, application_id_optimizer,
                                                    properties={'correlation_id': correlation_id_optimizer}, raw=True)
            print(f"Message to Optimizer: {Message_Results}")
            print("-------------------------------------------------")
            print("Message to Optimizer has been sent from Key: OPT-Triggering with Correlation Id: ", correlation_id_optimizer)

        except json.JSONDecodeError as e:
            print(f"Failed to parse message body from Optimizer as JSON: {e}")

        # For debugging purposes, it can be removed for production
        if feasibility: # Write CFSBResponse to file
            # print("CFSBResponse:", CFSBResponse)
            # Writing the formatted JSON to a json file
            formatted_json = json.dumps(CFSBResponse, indent=4)
            with open('CFSB_Response.json', 'w') as file:
                file.write(formatted_json)
                print("-------------------------------------------------")
                print("Data with Scores and Ranks for Nodes are saved to CFSB_Response.json")
        print_end_message()

    def handle_multi(self, application_id_optimizer, correlation_id_optimizer, body_sent_from_optimizer, context):
        request_id = correlation_id_optimizer
        print(f"Entered handle_multi - Request ID: {request_id}, App ID: {application_id_optimizer}")
        feasibility = False

        try:
            unique_nodes_dict = {}  # Store unique nodes
            list_number = 0  # Count the # of Lists and requests to SAL
            locations = []

            for requirement in body_sent_from_optimizer:
                list_number += 1
                print("-----------------------------------------------------------")
                print(f"[Request {request_id}] Processing List: {list_number}")

                requirement, locations = remove_request_attribute('CFSB-datasource-geolocations', requirement)
                requirement = json.dumps(requirement)  # Convert to JSON

                ## Prepare message to be sent to SAL
                RequestToSal = {"metaData": {"user": "admin"}, "body": requirement}
                print(f"[Request {request_id}] Sending to SAL: {RequestToSal}")
                sal_reply = context.publishers['SAL-GET'].send_sync(RequestToSal)
                if sal_reply is None:
                    context.get_publisher('SendToOPTMulti').send(
                        {"success": False, "message": "SAL-GET request failed"}, application_id_optimizer,
                        properties={'correlation_id': correlation_id_optimizer}, raw=True)
                    print(f"[Request {request_id}] SAL-GET request failed")
                    return
                # **Prevent Blocking on send_sync()**
                print(f"[Request {request_id}] Received response from SAL")

                ## Process SAL's Reply
                # Test possible problematic response from SAL or Server
                # sal_reply = {
                #     'when': '2025-05-29T14:53:50.398298Z',
                #     'body': '{"key":"gateway-server-exception-error","message":" Request processing failed; nested exception is java.lang.NullPointerException</p><p><b>Description</b> The server encountered an unexpected condition that prevented it from fulfilling the request."}',
                #     'metaData': {
                #         'user': 'admin',
                #         'status': 500,  # Note: just use int directly
                #         'protocol': 'HTTP'
                #     }
                # }
                status = sal_reply.get('metaData', {}).get('status', None)

                if sal_reply is not None and sal_reply != '' and status == 200:
                    sal_body = sal_reply.get('body') if isinstance(sal_reply, dict) else None

                    ## ── Begin error‐checκ ──
                    try:
                        parsed = json.loads(sal_body) # Do this as sal_body is a raw string
                    except (TypeError, json.JSONDecodeError):
                        parsed = sal_body

                    if isinstance(parsed, dict) \
                            and 'key' in parsed \
                            and any(kw in parsed['key'].lower() for kw in ('error', 'exception')):
                        print("Error found in SAL’s reply:", parsed.get('message'))
                        sal_body = []
                        Message_Results = {
                            "message": f"An error returned from SAL for list {list_number}"
                        }
                    ## ── End error‐check ──

                    if not sal_body or sal_body.strip() == '[]': # Check whether SAL's reply body is empty
                        print(f"[Request {request_id}] returned an empty body: {sal_reply}")
                    else:
                        print(f"[Request {request_id}] SAL Replied for List {list_number}")
                        nodes_by_requirement = json.loads(sal_body)
                        print(f"[Request {request_id}] Nodes in List {list_number}: {len(nodes_by_requirement)}")

                        # Remove aws invalid instance types
                        # This is a temporary workaround to be removed when proper node candidate filtering is in place.
                        filtered_nodes_by_requirement = []
                        for node in nodes_by_requirement:
                            try:
                                if ("cloud" in node and node["cloud"]["id"] != "edge" and "api" in node[
                                    "cloud"] and "providerName" in node["cloud"]["api"] and "aws-ec2" ==
                                        node["cloud"]["api"]["providerName"] and node["hardware"][
                                            "name"] not in VALID_AWS_INSTANCE_TYPES):
                                    print(f"Skipping invalid instance type {node['hardware']['name']}")
                                    continue
                                else:
                                    filtered_nodes_by_requirement.append(node)
                            except Exception as e:
                                print(f"Exception filtering {node}: {e}")
                        nodes_by_requirement = filtered_nodes_by_requirement

                        for node in nodes_by_requirement:
                            unique_nodes_dict[node["id"]] = node

                else: # Some error occured and SAL did not reply
                    Message_Results = {
                        "message": status
                    }
                    print(f"STATUS: {status}")

            total_nodes = len(unique_nodes_dict)  # Get the total number of nodes
            print(f"[Request {request_id}] Finished Processing Lists. Unique Nodes: {total_nodes}")

            ## Continue with Evaluation
            if total_nodes != 0:
                # Here the code differentiates from the SINGLE request
                nodes_data = list(unique_nodes_dict.values())

                print("Total Nodes in SAL's reply:", total_nodes)
                # print(nodes_data)
                sal_reply_body = json.dumps(nodes_data)
                # print("SAL reply Body:", sal_reply_body)  # print(type(sal_reply))

                # Check the number of nodes before Evaluation
                if total_nodes > 1:
                    # Search for application_id, Read JSON and create data to pass to Evaluation
                    if check_json_file_exists(application_id_optimizer):  # Application JSON exists
                        print("-------------------------------------------------")
                        print(f"JSON file for application ID {application_id_optimizer} exists.")

                        # The read_application_data returns in app_data the policy from the saved file to check it and convert or not
                        app_data, selected_criteria, provider_criteria, relative_wr_data, immediate_wr_data = read_application_data(
                            application_id_optimizer)
                        extracted_data_SAL, node_ids, node_names, providers, filtered_nodes_message = extract_SAL_node_candidate_data(
                            sal_reply_body, app_data, application_id_optimizer, selected_criteria, correlation_id_optimizer)
                        data_table = create_data_table(extracted_data_SAL, selected_criteria, provider_criteria, locations)
                        # print("relative_wr_data:", relative_wr_data)
                        # print("immediate_wr_data:", immediate_wr_data)
                    else:  # Application does not exist in directory
                        print("-------------------------------------------------")
                        print(f"JSON file for application ID {application_id_optimizer} does not exist.")
                        # selected_criteria = ["Operating cost", "Memory Price", "Number of CPU Cores", "Memory Size", "Storage Capacity"]
                        json_selected_criteria = {
                            "selectedCriteria": [
                                {
                                    "name": "attr-performance-capacity-num-of-cores",
                                    "type": 2,
                                    "title": "Number of CPU Cores"
                                },
                                {
                                    "name": "attr-performance-capacity-memory",
                                    "type": 2,
                                    "title": "Memory Size"
                                }
                            ]
                        }
                        # Check if distance was asked by optimizer
                        if locations:
                            distance_item = {
                                "name": "9f5706e3-08bd-412d-8d59-04f464e867a8",
                                "type": 2,
                                "title": "Proximity to Data Source"
                            }
                            json_selected_criteria["selectedCriteria"].append(distance_item)
                        selected_criteria = {criterion['title']: criterion for criterion in
                                             json_selected_criteria.get('selectedCriteria', [])}
                        app_data = {"app_specific": 1}
                        extracted_data_SAL, node_ids, node_names, providers, filtered_nodes_message = extract_SAL_node_candidate_data(
                            sal_reply_body, app_data, application_id_optimizer, selected_criteria, correlation_id_optimizer)

                        # Create data_table:
                        # provider_criteria do not exist when the application file does not exist. None is treated like false
                        data_table = create_data_table(extracted_data_SAL, selected_criteria, None, locations)

                        relative_wr_data = []
                        immediate_wr_data = []
                        # create default app_data dictionary for policy and app_specific when file not exists for the application
                        app_data = {'policy': '0', 'app_specific': True} # Use the default policy (minimal)
                        # print("app_data:", app_data['policy'])

                    # Check the number of nodes before Evaluation
                    print("There are " + str(len(node_ids)) + " nodes for Evaluation")
                    if len(node_ids) == 0:
                        feasibility = False
                        Message_Results = {
                            "message": filtered_nodes_message
                        }
                    else: # print("Original Data", data_table)
                        # Convert the original data of RAM and # of Cores, e.g. 1/X, if they are selected
                        if (app_data['policy'] == '0'):
                            data_table = convert_data_table(data_table)  # Convert RAM and # of Cores, e.g. 1/X
                            # print("Converted data_table:", data_table)
                        else:
                            print("Policy is MAX for this application")

                        # Calculate the simple average score for each node (For debugging Purposes ONLY)
                        # columns = list(data_table.keys())
                        # averages = []
                        # for i in range(len(data_table[columns[0]])):
                        #     row_sum = sum(data_table[col][i] for col in columns)
                        #     averages.append(row_sum / len(columns))
                        # # print("Average Scores: ", averages)

                        # Run evaluation for all eligible nodes
                        evaluation_results = perform_evaluation(data_table, relative_wr_data, immediate_wr_data,
                                                                node_names, node_ids)
                        # print("Evaluation Results:", evaluation_results)
                        print("LP Status = " + str(evaluation_results.get('LPstatus')))

                        if evaluation_results.get('LPstatus') == 'feasible':
                            feasibility = True
                            ## Extract and Save the Results
                            ScoresAndRanks = evaluation_results.get('results', [])
                            # Sort scores and ranks to order first the best nodes
                            ScoresAndRanks = sorted(ScoresAndRanks, key=lambda x: x['Score'], reverse=True)
                            # Check the length and truncate if necessary
                            if len(ScoresAndRanks) > 250:
                                print("Evaluated Nodes: ", len(ScoresAndRanks))
                                ScoresAndRanks = ScoresAndRanks[:250]
                                # print("Remaining Nodes: ", len(ScoresAndRanks))
                            # print("Scores and Ranks:", ScoresAndRanks)

                            # Append the Score and Rank of each node to SAL's Response
                            Message_Results = append_evaluation_results(sal_reply_body, ScoresAndRanks)
                            Message_Results = sorted(Message_Results, key=lambda x: x['rank'], reverse=False)
                            #  print("Message_Results:", Message_Results)
                        else:
                            # the problem is infeasible
                            feasibility = False
                            Message_Results = evaluation_results.get('results') # Message_Results contains info about the infeasibility in this case

                else: # SAL returned only one node, thus no evaluation needed
                    feasibility = True
                    print("There is only one node!")
                    Message_Results = append_evaluation_results(sal_reply_body, [])

            else: # Then SAL's reply body is empty, thus send an empty body to Optimizer
                if status == 200: # If Status = 200, then SAL responded with an empty list,
                    # otherwise an error occured with Status code saved above
                    print("No resources returned from SAL!")
                    Message_Results = {
                        "message": "No resources returned from SAL"
                    }

            # Measure the size of the message in bytes and MB
            try:
                message_str = json.dumps(Message_Results)
                message_bytes = message_str.encode('utf-8')
                message_size_bytes = len(message_bytes)
                message_size_mb = message_size_bytes / (1024 * 1024)  # Convert bytes to MB
                print(f"Message Size: {message_size_bytes} bytes ({message_size_mb:.2f} MB)")
            except Exception as e:
                print("Error measuring message size:", e)

            # Check against the 104857600 bytes limit (~100 MB) of ActiveMQ
            if message_size_bytes > 104857600:
                print(f"Message size exceeds limit of 104857600 bytes (100 MB). Message not sent.")
                Message_Results = {
                    "message": "The message size exceeds limit of 104857600 bytes (100 MB) imposed by ActiveMQ"
                }


            ## Prepare message to be sent to OPTIMIZER
            CFSBResponse = {
                "metaData": {"user": "admin"},
                "body": Message_Results
            }

            ## Send message to OPTIMIZER
            logging.debug(f"[DEBUG] About to send response for Request ID: {correlation_id_optimizer} "
                          f"with properties: {{'correlation_id': {correlation_id_optimizer}}}")
            print(f"Message to Optimizer: {Message_Results}")
            print("-------------------------------------------------")
            context.get_publisher('SendToOPTMulti').send(CFSBResponse, application_id_optimizer, properties={'correlation_id': correlation_id_optimizer}, raw=True)
            print("Message to Optimizer has been sent from from Key: OPT-Triggering-Multi with Correlation Id: ", correlation_id_optimizer)


        except json.JSONDecodeError as e:
                print(f"Failed to parse message body from Optimizer as JSON: {e}")

        # For debugging purposes, it can be removed for production
        if feasibility: # Write CFSBResponse to file
           # print("CFSBResponse:", CFSBResponse)
           # Writing the formatted JSON to a json file
            formatted_json = json.dumps(CFSBResponse, indent=4)
            with open('CFSB_Response.json', 'w') as file:
                 file.write(formatted_json)
                 print("-------------------------------------------------")
                 print("Data with Scores and Ranks for Nodes are saved to CFSB_Response.json")
        print_end_message()


    def requestSAL(self, RequestToSal):
        try:
            sal_reply = Context.publishers['SAL-GET'].send_sync(RequestToSal)
            # Process SAL's Reply
            status = sal_reply.get('metaData', {}).get('status', None)
            if sal_reply is not None and sal_reply != '' and status == 200:
                sal_body = sal_reply.get('body')  # Get the 'body' as a JSON string
                # print("sal_body requestSAL function:", sal_body)
                return sal_body
            else:
                return None
        except Exception as e:
            print(f"Error while requesting SAL: {e}")
            return None

    def requestEmulate(self, RequestData):
        body = RequestData.get('body')
        key = RequestData.get('key')
        application_id = RequestData.get('application_id')
        # If body is a list with one element, extract that element
        if isinstance(body, list) and len(body) == 1:
            body = body[0]  # Get the first dictionary from the list
        reply = Context.publishers[key].send_sync(body, application_id)
        return reply


class Bootstrap(ConnectorHandler):
    context = None

    def ready(self, context: Context):
        self.context = context
        # Start the heartbeat to check connectivity with ActiveMQ
        # start_heartbeat(self.context)
def start_exn_connector_in_background():
    print("Starting EXN connector in background")
    def run_connector():
        # connector_handler = Bootstrap()  # Initialize the connector handler
        # eu.nebulouscloud.exn.sal.nodecandidate.*
        addressSAL_GET = 'eu.nebulouscloud.exn.sal.nodecandidate.get'
        # addressSAL_GET_REPLY = 'eu.nebulouscloud.exn.sal.nodecandidate.get.reply'
        addressOPTtriggering = 'eu.nebulouscloud.cfsb.get_node_candidates'
        addressOPTtriggeringMulti = 'eu.nebulouscloud.cfsb.get_node_candidates_multi'
        addressSendToOPT = 'eu.nebulouscloud.cfsb.get_node_candidates.reply'
        addressSendToOPTMulti = 'eu.nebulouscloud.cfsb.get_node_candidates_multi.reply'
        print(f"Init EXN connector with parameters: url={os.getenv('NEBULOUS_BROKER_URL')}, port={os.getenv('NEBULOUS_BROKER_PORT')}, username={os.getenv('NEBULOUS_BROKER_USERNAME')}")
        connector = EXN('ui', url=os.getenv('NEBULOUS_BROKER_URL'), port=os.getenv('NEBULOUS_BROKER_PORT'),
                        username=os.getenv('NEBULOUS_BROKER_USERNAME'), password=os.getenv('NEBULOUS_BROKER_PASSWORD'),
                        handler=Bootstrap(),
                        publishers=[
                            SyncedPublisher('SAL-GET', addressSAL_GET, True, True,timeout=120),
                            core.publisher.Publisher('SendToOPT', addressSendToOPT, True, True),
                            core.publisher.Publisher('SendToOPTMulti', addressSendToOPTMulti, True, True),
                            SyncedPublisher('OPT-Triggering-Multi', addressOPTtriggeringMulti, True, True), # Publisher for OTP multi
                            SyncedPublisher('OPT-Triggering', addressOPTtriggering, True, True) # Publisher for OTP
                        ],
                        consumers=[
                            # Consumer('SAL-GET-REPLY', addressSAL_GET, handler=SyncedHandler(), topic=True, fqdn=True),
                            Consumer('OPT-Triggering', addressOPTtriggering, handler=SyncedHandler(), topic=True,
                                     fqdn=True),
                            Consumer('OPT-Triggering-Multi', addressOPTtriggeringMulti, handler=SyncedHandler(),
                                     topic=True, fqdn=True)
                        ])
        connector.start()

    ## Start the EXN connector in a thread
    thread = threading.Thread(target=run_connector)
    thread.daemon = True  # Daemon threads will shut down immediately when the program exits
    thread.start()

# Used in routes.py
def call_publisher(body):
    handler = SyncedHandler()
    request = handler.requestSAL(body)
    return request

# Used in routes.py
def call_otp_publisher(data):
    handler = SyncedHandler()
    request = handler.requestEmulate(data)
    return request

# def safe_send_sync(publisher, message, *args, **kwargs):
#     """
#     Attempts to send a synchronous message and returns the reply.
#     Measures and prints the size of the message (in bytes) before sending.
#     Catches and logs errors (e.g. disconnection, oversized message).
#
#     Args:
#         publisher: The publisher object that supports send_sync.
#         message: The message (typically a dict) to be sent.
#         *args, **kwargs: Additional arguments to pass to publisher.send_sync.
#
#     Returns:
#         The reply if successful, or None if an error occurred.
#     """
#     try:
#         # Measure the message size before sending.
#         message_str = json.dumps(message)
#         message_size = len(message_str.encode('utf-8'))
#         print(f"Sending synchronous message of size {message_size} bytes")
#     except Exception as e:
#         print("Error measuring synchronous message size:", e)
#
#     try:
#         reply = publisher.send_sync(message, *args, **kwargs)
#         print(f" Send_Sync message sent successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#         return reply
#     except Exception as e:
#         print(f"Error sending synchronous message at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {e}")
#         # Here you might trigger reconnection or other error-handling logic.
#         return None

def is_activemq_connected(context, publisher_key, timeout=1):
    """
    Checks if the ActiveMQ connection is alive by sending a lightweight ping message.

    Args:
        context: The ActiveMQ context containing publishers.
        publisher_key: The key of the publisher to check.
        timeout (int): Timeout in seconds for the ping.

    Returns:
        True if the connection is healthy, False otherwise.
    """
    ping_msg = {
        "metaData": {"user": "admin"},
        "body": "PING"
    }
    publisher = context.publishers[publisher_key]

    # If the publisher supports send_sync, use it.
    if hasattr(publisher, "send_sync"):
        try:
            response = publisher.send_sync(ping_msg)
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connection check failed for publisher '{publisher_key}' using send_sync: {e}")
            return False
    else:
        # Fallback: use the send method (asynchronous) and assume no exception means OK.
        try:
            publisher.send(ping_msg)
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connection check failed for publisher '{publisher_key}' using send: {e}")
            return False


def safe_send(publisher, message, *args, **kwargs):
    """
    Attempts to send a message using the given publisher.
    Measures and prints the size of the message (in bytes) before sending.
    Catches and logs errors (e.g. disconnection, message size issues).

    Args:
        publisher: The publisher object from context.publishers.
        message: The message (typically a dict) to be sent.
        *args, **kwargs: Additional arguments to pass to publisher.send.

    Returns:
        True if the message was sent successfully, False otherwise.
    """
    try:
        publisher.send(message, *args, **kwargs)
        print(f"Heartbeat Message sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    except Exception as e:
        print(f"Error sending Heartbeat message at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {e}")
        # Here you might trigger reconnection logic or retries.
        return False

def heartbeat_sender(context, publisher_key, interval=10):
    """
    Periodically sends a heartbeat message using an existing publisher.

    Args:
        context: The context containing the publishers.
        publisher_key: The key of the publisher to use for the heartbeat.
        interval (int): Heartbeat interval in seconds.
    """
    while True:
        # Construct a lightweight heartbeat message as a dictionary.
        heartbeat_msg = {
            "metaData": {"user": "admin", "type": "heartbeat"},
            "body": "HEARTBEAT"
        }
        # Use safe_send to attempt sending the heartbeat.
        safe_send(context.publishers[publisher_key], heartbeat_msg)
        time.sleep(interval)

def start_heartbeat(context):
    """
    Starts the heartbeat thread using the selected publisher.
    """
    hb_thread = threading.Thread(target=heartbeat_sender, args=(context, 'SAL-GET', 10))
    hb_thread.daemon = True
    hb_thread.start()



def print_start_message():
    ascii_art = """                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                  -#####+                                                                         +  ###+  #      
               ##  #    + ##                                                                    #############       
             -#    +### ##  ##                                                              ######         ######   
             +  #  +  #      +-                                                                ##           #+#     
            +    # +          #         ######  #######  ######  #######                    ######          #####   
            #    #  ##.       #       ##        ##      ##       ##   ##              +##   +#  ### ..... ###  .#   
            -- ##  #  #        #      #         ##       ###     ##   ##         ############# ##############       
             #    -#            #    #          #####     ####   ######+      -  ###+ . .  ###  #.   ###    #       
              -#              #       ##        ##            #  ##     ##    ######         ######                  
                #             #        #######  ##      #######  ##-#####      #+#          #++#                    
                #          _#                                               ######         #######                 
                #        #                                                       .############                      
                #########                                                       ###  ####   ###                     
                                                                                      ##                                                                                                                                                                                                                           
             """
    # ascii_art = ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "="*50)
    print(ascii_art)
    print(f"Started to Process the Received Request at Timestamp: {timestamp:^50}")
    print("="*50 + "\n")

def print_end_message():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Use datetime.now() directly
    print("\n" + "="*50)
    print(f"{'CFSB Processing has been Completed':^50}")
    print(f"Timestamp: {timestamp:^50}")
    print("="*50 + "\n")


# Used to read dummy response and send to Optimizer using JSON
def read_dummy_response_data_toOpt(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    # Encapsulating the data within the "body" structure
    encapsulated_data = {
        "metaData": {"user": "admin"},
        "body": data
    }
    return encapsulated_data


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    except TypeError as e:  # includes simplejson.decoder.JSONDecodeError
        return False
    return True

