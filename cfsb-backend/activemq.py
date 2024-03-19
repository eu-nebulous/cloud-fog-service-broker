# ActiveMQ communication logic
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
import uuid

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.getLogger('exn.connector').setLevel(logging.CRITICAL)

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
            uuid.uuid4().hex.encode("utf-8") # for Correlation id

            # Optimizer_correlation_id = '88334290cad34ad9b21eb468a9f8ff11' # dummy correlation_id
            correlation_id_optimizer = message.correlation_id
            # logging.info(f"Optimizer_correlation_id {message.correlation_id}")
            print("Optimizer Correlation Id: ", correlation_id_optimizer)

            # application_id_optimizer = message.properties.application # can be taken also from message.annotations.application
            application_id_optimizer = message.subject
            # application_id_optimizer = 'd535cf554ea66fbebfc415ac837a5828' #dummy application_id_optimizer
            print("Application Id: ", application_id_optimizer)

            try:
                # Read the Message Sent from Optimizer
                opt_message_data = body
                print("Whole Message Sent from Optimizer:", opt_message_data)

                # Extract 'body' from opt_message_data
                body_sent_from_optimizer = opt_message_data.get('body', {})

                # 100 Nodes
                # body_sent_from_optimizer = [
                #     {
                #         "type": "NodeTypeRequirement",
                #         "nodeTypes": ["IAAS"],
                #         "jobIdForByon": "dummy-app-id",
                #         "jobIdForEDGE": "dummy-app-id"
                #     }
                # ]


                # 58 Nodes
                # body_sent_from_optimizer = [
                #     {
                #         "type": "NodeTypeRequirement",
                #         "nodeTypes": ["IAAS"],
                #         "jobIdForByon": "dummy-app-id",
                #         "jobIdForEDGE": "dummy-app-id"
                #     },
                #     {
                #         "type": "AttributeRequirement",
                #         "requirementClass": "hardware",
                #         "requirementAttribute": "cores",
                #         "requirementOperator": "EQ",
                #         "value": "2"
                #     },
                #     {
                #         "type": "AttributeRequirement",
                #         "requirementClass": "hardware",
                #         "requirementAttribute": "ram",
                #         "requirementOperator": "EQ",
                #         "value": "4096"
                #     }
                # ]

                # "jobIdForByon": "null",
                # "jobIdForEDGE": "null"
                # body_sent_from_optimizer =[
                # {
                #     "type": "NodeTypeRequirement",
                #     "nodeTypes": ["IAAS"]
                # },
                # {
                #     "type": "AttributeRequirement",
                #     "requirementClass": "image",
                #     "requirementAttribute": "operatingSystem.family",
                #      "requirementOperator": "IN","value":"UBUNTU"},
                # {
                #     "type":"AttributeRequirement",
                #     "requirementClass":"hardware",
                #     "requirementAttribute":"ram",
                #     "requirementOperator":"GEQ",
                #     "value":"4096"
                # },
                # {"type":"AttributeRequirement","requirementClass":"hardware","requirementAttribute":"cores",
                #  "requirementOperator":"GEQ","value":"4"}
                # ]

                # body_sent_from_optimizer = [
                #     {
                #         "type": "NodeTypeRequirement",
                #         "nodeTypes": ["IAAS"]
                #     }
                # ]
                # "nodeTypes": ["EDGE"]
                # "nodeTypes": ["IAAS", "PAAS", "FAAS", "BYON", "EDGE", "SIMULATION"]
                # "jobIdForEDGE": "FCRnewLight0"
                # "jobIdForByon":"dummy-app-id",
                # "jobIdForEDGE":"dummy-app-id"

                # body_sent_from_optimizer = [
                #     {
                #         "type": "NodeTypeRequirement",
                #         "nodeTypes": ["IAAS"]
                #     },
                #     {
                #         "type": "AttributeRequirement",
                #         "requirementClass": "hardware",
                #         "requirementAttribute": "cores",
                #         "requirementOperator": "EQ",
                #         "value": "2"
                #     },
                #     {
                #         "type": "AttributeRequirement",
                #         "requirementClass": "hardware",
                #         "requirementAttribute": "ram",
                #         "requirementOperator": "EQ",
                #         "value": "4096"
                #     }
                # ]

                # body_sent_from_optimizer =[
                #     {
                #         "type": "NodeTypeRequirement",
                #         "nodeTypes": ["IAAS"],
                #         "jobIdForByon": "dummy-app-id",
                #         "jobIdForEDGE": "dummy-app-id"
                #     },
                #     {
                #         "type": "AttributeRequirement",
                #         "requirementClass": "hardware",
                #         "requirementAttribute": "cores",
                #         "requirementOperator": "EQ",
                #         "value": "2"
                #     },
                #     {
                #         "type": "AttributeRequirement",
                #         "requirementClass": "hardware",
                #         "requirementAttribute": "ram",
                #         "requirementOperator": "EQ",
                #         "value": "4096"
                #     }
                # ]

                # logging.info(body_sent_from_optimizer)
                # print("Extracted body from Optimizer Message:", body_sent_from_optimizer)

                ## Prepare message to be send to SAL
                # Convert the body data to a JSON string

                # body_json_string = json.dumps(body_sent_from_optimizer)
                body_json_string = body_sent_from_optimizer
                RequestToSal = {  # Dictionary
                    "metaData": {"user": "admin"},   # key [String "metaData"] value [dictionary]
                    "body": body_json_string   # key [String "body"] value [JSON String]
                }
                # logging.info("RequestToSal: %s", RequestToSal)
                print("RequestToSal:", RequestToSal)

                # print("Is RequestToSal a valid dictionary:", isinstance(RequestToSal, dict))
                # print("Is the 'body' string in RequestToSal a valid JSON string:", is_json(RequestToSal["body"]))

                ## Request the node candidates from SAL
                sal_reply = context.publishers['SAL-GET'].send_sync(RequestToSal)

                ## Process SAL's Reply
                # sal_reply_body = sal_reply.get('body')
                sal_body = sal_reply.get('body')  # Get the 'body' as a JSON string

                # try:
                #     # Parse the JSON string to a Python object
                #     nodes_data = json.loads(sal_body)
                #     total_nodes = len(nodes_data)  # Get the total number of nodes
                #
                #     # Check if more than 51 nodes exist
                #     if total_nodes > 58:
                #         print("More than 58 nodes exist. Only the first 51 nodes will be processed.")
                #         # Filter to only include the first 51 nodes
                #         sal_reply_body = nodes_data[:60]
                #     else:
                #         print(f"Total {total_nodes} nodes found. Processing all nodes.")
                #         sal_reply_body = sal_reply.get('body')
                #
                # except json.JSONDecodeError as e:
                #     print(f"Error parsing JSON: {e}")


                # filename = 'SAL_Response_10EdgeDevs.json'
                # with open(filename, 'r') as file:
                #    sal_reply_body = json.load(file)
                #    print("SAL's Reply from JSON File:", sal_reply_body)


                try:
                    # Parse the JSON string to a Python object
                    nodes_data = json.loads(sal_body)
                    total_nodes = len(nodes_data)  # Get the total number of nodes

                    # Check if more than 58 nodes exist
                    if total_nodes > 58:
                        print("More than 58 nodes exist. Only the first 51 nodes will be processed.")
                        # Filter to only include the first 51 nodes and convert back to JSON string
                        sal_reply_body = json.dumps(nodes_data[:15])
                    else:
                        print(f"Total {total_nodes} nodes found. Processing all nodes.")
                        # Keep sal_reply_body as is since it's already a JSON string
                        sal_reply_body = sal_body

                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    sal_reply_body = "[]"  # Default to an empty JSON array as a string in case of error

                if sal_reply_body: # Check whether SAL's reply body is empty
                    # logging.info(f"Whole reply Received from SAL: {sal_reply}")
                    # print("SAL reply Body:", sal_reply_body)

                    # Search for application_id, Read JSON and create data to pass to Evaluation
                    if check_json_file_exists(application_id_optimizer): # Application JSON exist in DB
                        print(f"JSON file for application ID {application_id_optimizer} exists.")
                        node_ids = extract_SAL_node_candidate_data(sal_reply)[2] # 0,1,2nd Position returns the function
                        # node_ids = ['8a7482868df473cc018df47d8ea60003', '8a7482868df473cc018df47d8fc70005', '8a7482868df473cc018df47d90e70007', '8a7482868df473cc018df47d92090009', '8a7482868df473cc018df47d9326000b', '8a7482868df473cc018df47d9445000d', '8a7482868df473cc018df47d957f000f', '8a7482868df473cc018df47d96a50011', '8a7482868df473cc018df47d97c70013', '8a7482868df473cc018df47d98e30015']
                        # print("node_ids_SAL:", node_ids_SAL)

                        # Check if there is any difference in available nodes between saved data in DB and SAL's reply
                        data_table, relative_wr_data, immediate_wr_data, node_names = read_application_data(application_id_optimizer, node_ids)
                        if not node_names:
                            node_names = node_ids
                        print("data_table filtered from DB:", data_table)
                        print("node_ids filtered from DB:", node_ids)
                        print("node_names filtered from DB:", node_names)

                        # I need to use the most updated data for nodes sent from SAL,
                        # I can modify the function to retrieve only WR info but there is a problem if other criteria are used
                        # Maybe I have to use the new data only for the criteria with data coming from SAL and the saved ones for the
                        # rest criteria
                        # In case a new node sent from SAL which I have not data saved, then do not consider it if also other crieria
                        # exist rather than the ones

                    else:  # Application JSON does not exist in DB
                        print(f"JSON file for application ID {application_id_optimizer} does not exist.")
                        # Read data from SAL's response by calling the function extract_node_candidate_data()
                        # extracted_data, number_of_nodes, node_ids, node_names = extract_node_candidate_data('SAL_Response_11EdgeDevs.json')
                        extracted_data, number_of_nodes, node_ids, node_names = extract_SAL_node_candidate_data(sal_reply_body)
                        # print("extracted_data:", extracted_data)
                        print("node_ids:", node_ids)

                        # Use the create_criteria_mapping() to get the criteria mappings
                        # selected_criteria = ["Operating cost", "Memory Price", "Number of CPU Cores", "Memory Size", "Storage Capacity"]
                        selected_criteria = ["Number of CPU Cores", "Memory Size"]
                        field_mapping = create_criteria_mapping(selected_criteria, extracted_data)
                        # Create data_table:
                        data_table = create_data_table(selected_criteria, extracted_data, field_mapping)
                        relative_wr_data = []
                        immediate_wr_data = []
                        print("created_data_table:", data_table)

                    # Check the number of nodes before Evaluation
                    print("There are " + str(len(node_ids)) + " elements in node_ids")

                    ## Run evaluation
                    evaluation_results = perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_names, node_ids)
                    # print("Evaluation Results:", evaluation_results)

                    ## Extract and save the results
                    # ScoresAndRanks = evaluation_results['results']
                    ScoresAndRanks = evaluation_results.get('results', [])
                    print("Scores and Ranks:", ScoresAndRanks)

                    # Append the Score and Rank of each node to SAL's Response
                    SAL_and_Scores_Body = append_evaluation_results(sal_reply_body, ScoresAndRanks)
                    # SAL_and_Scores_Body = append_evaluation_results('SAL_Response_11EdgeDevs.json', ScoresAndRanks)
                    #  print("SAL_and_Scores_Body:", SAL_and_Scores_Body)

                    ## Prepare message to be sent to OPTIMIZER
                    # CFSBResponse = read_dummy_response_data_toOpt('CFSB_Body_Response.json')  # Data and Scores for 5 Nodes

                    CFSBResponse = {
                            "metaData": {"user": "admin"},
                            "body": SAL_and_Scores_Body
                    }
                    print("CFSBResponse:", CFSBResponse)

                    formatted_json = json.dumps(CFSBResponse, indent=4)
                    # Writing the formatted JSON to a file named test.json
                    with open('CFSBResponse.json', 'w') as file:
                         file.write(formatted_json)
                         print("Formatted JSON has been saved to CFSBResponse.json")

                else: # Then SAL's reply body is empty send an empty body to Optimizer
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

     # # Start the EXN connector in a separate thread
     thread = threading.Thread(target=run_connector)
     thread.daemon = True  # Daemon threads will shut down immediately when the program exits
     thread.start()

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

