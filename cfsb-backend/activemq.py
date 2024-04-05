# ActiveMQ communication logic
import sys
import threading
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
import uuid
from Evaluation import perform_evaluation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('exn.connector').setLevel(logging.CRITICAL)

class SyncedHandler(Handler):
    def on_message(self, key, address, body, message: Message, context=None):
        # logging.info(f"[SyncedHandler] Received {key} => {address}: {body}")
        # logging.info("on_message in SyncedHandler is executed")
        # logging.info(f"[body] {body}")

        # Triggered by OPTIMIZER, Get app id, correlation id and filters
        # if address == "topic://eu.nebulouscloud.cfsb.get_node_candidates":
        if key == "OPT-triggering":
            # logging.info("Entered in OPT-triggering'")

            # Save the correlation_id (We do not have it from the app_side)
            uuid.uuid4().hex.encode("utf-8")  # for Correlation id
            correlation_id_optimizer = message.correlation_id
            if not correlation_id_optimizer:
                correlation_id_optimizer = '88334290cad34ad9b21eb468a9f8ff11'  # dummy correlation_id

            # logging.info(f"Optimizer_correlation_id {message.correlation_id}")
            # print("Optimizer Correlation Id: ", correlation_id_optimizer)

            # application_id_optimizer = message.properties.application # can be taken also from message.annotations.application
            application_id_optimizer = message.subject
            # application_id_optimizer = 'd535cf554ea66fbebfc415ac837a5828' #dummy application_id_optimizer
            # print("Application Id: ", application_id_optimizer)

            try:
                # Read the Message Sent from Optimizer
                opt_message_data = body
                # print("Whole Message Sent from Optimizer:", opt_message_data)

                # Extract 'body' from opt_message_data
                body_sent_from_optimizer = opt_message_data.get('body', {})

                ## Example body
                # body_sent_from_optimizer = [
                #     {
                #         "type": "NodeTypeRequirement",
                #         # "nodeTypes": ["EDGES"]
                #         "nodeTypes": ["IAAS", "PAAS", "FAAS", "BYON", "EDGE", "SIMULATION"]
                #         # ,"jobIdForEDGE": "FCRnewLight0"
                #     }
                #     # ,{
                #     #         "type": "AttributeRequirement",
                #     #         "requirementClass": "hardware",
                #     #         "requirementAttribute": "ram",
                #     #         "requirementOperator": "EQ",
                #     #         "value": "2"
                #     # }
                # ]

                # logging.info(body_sent_from_optimizer)
                print("Extracted body from Optimizer Message:", body_sent_from_optimizer)

                ## Prepare message to be send to SAL
                # Convert the body data to a JSON string
                # body_json_string = json.dumps(body_sent_from_optimizer)  # For Sender
                body_json_string = body_sent_from_optimizer # For Optimizer

                RequestToSal = {  # Dictionary
                    "metaData": {"user": "admin"},   # key [String "metaData"] value [dictionary]
                    "body": body_json_string   # key [String "body"] value [JSON String]
                }
                # logging.info("RequestToSal: %s", RequestToSal)
                # print("RequestToSal:", RequestToSal)
                # print("Is RequestToSal a valid dictionary:", isinstance(RequestToSal, dict))
                # print("Is the 'body' string in RequestToSal a valid JSON string:", is_json(RequestToSal["body"]))

                ## Request the node candidates from SAL
                sal_reply = context.publishers['SAL-GET'].send_sync(RequestToSal)

                ## Process SAL's Reply
                sal_body = sal_reply.get('body')  # Get the 'body' as a JSON string

                try:
                    # Parse the JSON string to a Python object
                    nodes_data = json.loads(sal_body)
                    # Check if there is any error in SAL's reply body
                    if 'key' in nodes_data and any(keyword in nodes_data['key'].lower() for keyword in ['error', 'exception']):
                        print("Error found in message body:", nodes_data['message'])
                        sal_reply_body = []
                    else:  # No error found in SAL's reply body
                        total_nodes = len(nodes_data)  # Get the total number of nodes
                        print("Total Nodes in SAL's reply:", total_nodes)

                        if total_nodes > 400: # Check if more than 400 nodes received
                            print("More than 400 nodes returned from SAL.")
                            # Filter to only include the first 400 nodes and convert back to JSON string
                            sal_reply_body = json.dumps(nodes_data[:400])
                        elif total_nodes > 0 and total_nodes <= 400:
                            print(f"Total {total_nodes} nodes returned from SAL. Processing all nodes.")
                            # Keep sal_reply_body as is since it's already a JSON string
                            sal_reply_body = sal_body
                        else:
                            print(f"Total {total_nodes} nodes returned from SAL.")
                            sal_reply_body = []

                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON reply from SAL: {e}")
                    sal_reply_body = []  # Default to an empty JSON array as a string in case of error

                if sal_reply_body:  # Check whether SAL's reply body is empty
                    # logging.info(f"Reply Received from SAL: {sal_reply}")
                    # print("SAL reply Body:", sal_reply_body)

                    # Check the number of nodes before Evaluation
                    if total_nodes > 1:
                        # Search for application_id, Read JSON and create data to pass to Evaluation
                        if check_json_file_exists(application_id_optimizer): # Application JSON exist in DB
                            print(f"JSON file for application ID {application_id_optimizer} exists.")
                            # Check if there are differences in available nodes between saved data in JSON file and SAL's reply
                            data_table, relative_wr_data, immediate_wr_data, node_names, node_ids = read_application_data(application_id_optimizer, sal_reply_body)
                            # print("sal_reply_body:", sal_reply_body)
                            # print("data_table filtered from JSON and SAL:", data_table)
                            # print("node_ids filtered from JSON and SAL:", node_ids)
                            # print("relative_wr_data:", relative_wr_data)
                            # print("immediate_wr_data:", immediate_wr_data)
                            # print("node_names filtered from JSON and SAL:", node_names)

                        else:  # Application does not exist in directory
                            print(f"JSON file for application ID {application_id_optimizer} does not exist.")
                            # Read data from SAL's response by calling the function extract_node_candidate_data()
                            # extracted_data_SAL, node_ids, node_names = extract_node_candidate_data('SAL_Response_11EdgeDevs.json')
                            extracted_data_SAL, node_ids, node_names = extract_SAL_node_candidate_data(sal_reply_body)
                            # print("extracted_data_SAL:", extracted_data_SAL)
                            # print("node_ids:", node_ids)

                            # Use the create_criteria_mapping() to get the criteria mappings
                            # selected_criteria = ["Operating cost", "Memory Price", "Number of CPU Cores", "Memory Size", "Storage Capacity"]
                            selected_criteria = ["Number of CPU Cores", "Memory Size"]
                            field_mapping = create_criteria_mapping()
                            # Create data_table:
                            data_table = create_data_table(selected_criteria, extracted_data_SAL, field_mapping)
                            relative_wr_data = []
                            immediate_wr_data = []
                            # print("created_data_table:", data_table)

                        # Check the number of nodes before Evaluation
                        print("There are " + str(len(node_ids)) + " nodes for Evaluation")

                        print("Original created_data_table:", data_table)
                        # Convert RAM and Cores
                        data_table = convert_data_table(data_table)
                        print("Converted created_data_table:", data_table)
                        ## Run evaluation
                        evaluation_results = perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_names, node_ids)
                        # print("Evaluation Results:", evaluation_results)

                        ## Extract and save the results
                        # ScoresAndRanks = evaluation_results['results']
                        ScoresAndRanks = evaluation_results.get('results', [])
                        # print("Scores and Ranks:", ScoresAndRanks)

                        # Append the Score and Rank of each node to SAL's Response
                        SAL_and_Scores_Body = append_evaluation_results(sal_reply_body, ScoresAndRanks)
                        #  print("SAL_and_Scores_Body:", SAL_and_Scores_Body)
                    else:
                        print("There is only one node!")
                        # Append the Score and Rank of each node to SAL's Response
                        SAL_and_Scores_Body = append_evaluation_results(sal_reply_body, [])

                    ## Prepare message to be sent to OPTIMIZER
                    # CFSBResponse = read_dummy_response_data_toOpt('CFSB_Body_Response.json')  # Data and Scores for 5 Nodes
                    CFSBResponse = {
                        "metaData": {"user": "admin"},
                        "body": SAL_and_Scores_Body
                    }

                    # print("CFSBResponse:", CFSBResponse)
                    # Writing the formatted JSON to a json file
                    formatted_json = json.dumps(CFSBResponse, indent=4)
                    with open('CFSBResponse.json', 'w') as file:
                         file.write(formatted_json)
                         print("Formatted JSON has been saved to CFSBResponse.json")

                else:  # Then SAL's reply body is empty send an empty body to Optimizer
                    print("No Body in reply from SAL!")
                    # Send [] to Optimizer
                    CFSBResponse = {
                        "metaData": {"user": "admin"},
                        "body": {}
                    }

                ## Send message to OPTIMIZER
                context.get_publisher('SendToOPT').send(CFSBResponse, application_id_optimizer, properties={'correlation_id': correlation_id_optimizer}, raw=True)

            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse message body from Optimizer as JSON: {e}")



    def requestSAL(self, RequestToSal):
        sal_reply = Context.publishers['SAL-GET'].send_sync(RequestToSal)
        # Process SAL's Reply
        sal_body = sal_reply.get('body')  # Get the 'body' as a JSON string
        # print("sal_body requestSAL function:", sal_body)
        return sal_body

class Bootstrap(ConnectorHandler):
    context = None
    def ready(self, context: Context):
        self.context = context

def start_exn_connector_in_background():
     def run_connector():
        # connector_handler = Bootstrap()  # Initialize the connector handler
        # eu.nebulouscloud.exn.sal.nodecandidate.*
        addressSAL_GET = 'eu.nebulouscloud.exn.sal.nodecandidate.get'
        #addressSAL_GET_REPLY = 'eu.nebulouscloud.exn.sal.nodecandidate.get.reply'
        addressOPTtriggering = 'eu.nebulouscloud.cfsb.get_node_candidates'
        addressSendToOPT = 'eu.nebulouscloud.cfsb.get_node_candidates.reply'

        connector = EXN('ui', url=os.getenv('NEBULOUS_BROKER_URL'), port=os.getenv('NEBULOUS_BROKER_PORT'), username=os.getenv('NEBULOUS_BROKER_USERNAME'), password=os.getenv('NEBULOUS_BROKER_PASSWORD'),
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

     # # Start the EXN connector in a separate thread
     thread = threading.Thread(target=run_connector)
     thread.daemon = True  # Daemon threads will shut down immediately when the program exits
     thread.start()


def call_publisher(body):
    handler = SyncedHandler()
    request = handler.requestSAL(body)
    return request


# Used to read dummy response and send to Optimizer using JSON
# I have already sent to Optimizer using this function
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

