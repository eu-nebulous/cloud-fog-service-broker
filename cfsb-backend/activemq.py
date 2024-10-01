# ActiveMQ Communication Logic
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
        if key == "OPT-Triggering":
            # logging.info("Entered in OPT-Triggering'")
            # Save the correlation_id (We do not have it from the app_side)
            uuid.uuid4().hex.encode("utf-8")  # for Correlation id
            correlation_id_optimizer = message.correlation_id
            if not correlation_id_optimizer:
                correlation_id_optimizer = '88334290cad34ad9b21eb468a9f8ff11'  # dummy correlation_id
            # print("Optimizer Correlation Id: ", correlation_id_optimizer)

            # application_id_optimizer = message.properties.application # can be taken also from message.annotations.application
            application_id_optimizer = message.subject
            if not application_id_optimizer:
                application_id_optimizer = 'd535cf554ea66fbebfc415ac837a5828' #dummy application_id_optimizer
            # print("Application Id: ", application_id_optimizer)

            try:
                ###-------- Extract body from Optimizer's message --------###
                ## Read the Message Sent from Optimizer
                opt_message_data = body
                print("Whole Message Sent from Optimizer Single:", opt_message_data)
                ## Extract 'body' from opt_message_data
                body_sent_from_optimizer = opt_message_data.get('body', {})
                body_json_string = body_sent_from_optimizer
                ###-------- Extract body from Optimizer's message --------###

                ###-------- Dummy body for DEMO when we emulate the message sent from Optimizer--------###
                # body_sent_from_optimizer = [
                #     {
                #         "type": "NodeTypeRequirement",
                #         "nodeTypes": ["IAAS", "PAAS", "FAAS", "BYON", "EDGE", "SIMULATION"]
                #         # "nodeTypes": ["EDGES"]
                #         ,"jobIdForEDGE": "FCRnewLight0"
                #     }
                    # ,{
                    #     "type": "AttributeRequirement",
                    #     "requirementClass": "hardware",
                    #     "requirementAttribute": "cores",
                    #     "requirementOperator": "GEQ",
                    #     "value": "64"
                    # }
                    # ,{
                    #         "type": "AttributeRequirement",
                    #         "requirementClass": "hardware",
                    #         "requirementAttribute": "ram",
                    #         "requirementOperator": "GEQ",
                    #         "value": "131072"
                    # }
                # ]

                # body_json_string = json.dumps(body_sent_from_optimizer) # When SENDER is used then Convert the body data to a JSON string
                ###-------- Dummy body for DEMO when we emulate the message sent from Optimizer--------###

                ###--- For Review, use ONLY ONE block, Optimizer's body or dummy body ----------------------###

                print("-------------------------------------------------")
                print("Extracted body from Optimizer Message:", body_sent_from_optimizer)

                ## Prepare message to be send to SAL
                RequestToSal = {  # Dictionary
                    "metaData": {"user": "admin"},   # key [String "metaData"] value [dictionary]
                    "body": body_json_string   # key [String "body"] value [JSON String]
                }
                print("Request to SAL:", RequestToSal)
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
                        print("Error found in SAL's message body:", nodes_data['message'])
                        sal_reply_body = []
                    else:  # No error found in SAL's reply body
                        total_nodes = len(nodes_data)  # Get the total number of nodes
                        print("Total Nodes in SAL's reply:", total_nodes)

                        if total_nodes > 400: # Check if more than 400 nodes received
                            print("More than 400 nodes returned from SAL.")
                            # Filter to only include the first 400 nodes and convert back to JSON string
                            sal_reply_body = json.dumps(nodes_data[:400])
                        elif total_nodes > 0 and total_nodes <= 400:
                            # print(f"Total {total_nodes} nodes returned from SAL. Processing all nodes.")
                            # Keep sal_reply_body as is since it's already a JSON string
                            sal_reply_body = sal_body
                        else:
                            sal_reply_body = []

                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON reply from SAL: {e}")
                    sal_reply_body = []  # Default to an empty JSON array as a string in case of error

                if sal_reply_body:  # Check whether SAL's reply body is empty
                    # print("SAL reply Body:", sal_reply_body)

                    # Check the number of nodes before Evaluation
                    if total_nodes > 1:
                        # Search for application_id, Read JSON and create data to pass to Evaluation
                        if check_json_file_exists(application_id_optimizer): # Application JSON exist in DB
                            print(f"JSON file for application ID {application_id_optimizer} exists.")

                            ###-------- Extract data from dummy JSON file --------###
                            # json_file_path = 'dummySALresponse.json'
                            # sal_reply_body = read_json_file_as_string(json_file_path)
                            ###-------- Extract data from dummy JSON file --------###

                            # Check if there are differences in available nodes between saved data in JSON file and SAL's reply
                            data_table, relative_wr_data, immediate_wr_data, node_names, node_ids = read_application_data(application_id_optimizer, sal_reply_body)
                            # print("relative_wr_data:", relative_wr_data)
                            # print("immediate_wr_data:", immediate_wr_data)
                        else:  # Application does not exist in directory
                            # print(f"JSON file for application ID {application_id_optimizer} does not exist.")

                            ###-------- Extract data from SAL's response --------###
                            # Extract data from SAL's response
                            extracted_data_SAL, node_ids, node_names = extract_SAL_node_candidate_data(sal_reply_body)
                            ###-------- Extract data from SAL's response --------###

                            ###-------- Extract data from dummy JSON file --------###
                            # json_file_path = 'dummySALresponse.json'
                            # sal_reply_body = read_json_file_as_string(json_file_path)
                            # if sal_reply_body:
                            #     extracted_data_SAL, node_ids, node_names = extract_SAL_node_candidate_data(sal_reply_body)
                            ###-------- Extract data from dummy JSON file --------###


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


                        # Check the number of nodes before Evaluation
                        print("There are " + str(len(node_ids)) + " nodes for Evaluation")

                        # Convert the original data of RAM and # of Cores, e.g. 1/X, if they are selected
                        # print("Original created_data_table:", data_table)
                        data_table = convert_data_table(data_table)  # Convert RAM and # of Cores, e.g. 1/X
                        # print("Converted created_data_table:", data_table)

                        ## Run evaluation
                        evaluation_results = perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_names, node_ids)
                        # print("Evaluation Results:", evaluation_results)

                        if evaluation_results.get('LPstatus') == 'feasible':
                            feasibility = True
                            ## Extract and Save the Results
                            # ScoresAndRanks = evaluation_results['results']
                            ScoresAndRanks = evaluation_results.get('results', [])
                            print("Scores and Ranks:", ScoresAndRanks)

                            # Append the Score and Rank of each node to SAL's Response
                            Evaluation_Results = append_evaluation_results(sal_reply_body, ScoresAndRanks)
                            #  print("Evaluation_Results:", Evaluation_Results)
                        else:
                            # problem is infeasible
                            feasibility = False
                            results = evaluation_results.get('results')
                            Evaluation_Results = results  # Evaluation_Results variable may contain info about the infeasible case also
                    # when SAL returns only one node thus no evaluation needed
                    else:
                        feasibility = True
                        print("There is only one node!")
                        # Append the Score and Rank of each node to SAL's Response
                        Evaluation_Results = append_evaluation_results(sal_reply_body, [])

                    ## Prepare message to be sent to OPTIMIZER
                    # CFSBResponse = read_dummy_response_data_toOpt('CFSB_Body_Response.json')  # Data and Scores for 5 Nodes
                    CFSBResponse = {
                        "metaData": {"user": "admin"},
                        "body": Evaluation_Results
                    }

                    if feasibility:
                        # print("CFSBResponse:", CFSBResponse)
                        # Writing the formatted JSON to a json file
                        formatted_json = json.dumps(CFSBResponse, indent=4)
                        with open('CFSBResponse.json', 'w') as file:
                             file.write(formatted_json)
                             print("Data with Scores and Ranks for Nodes are saved to CFSBResponse.json")

                else:  # Then SAL's reply body is empty send an empty body to Optimizer
                    print("No Body in reply from SAL!")
                    sal_reply_body_empty = {
                        "message": "No resources returned from SAL"
                    }
                    CFSBResponse = {
                        "metaData": {"user": "admin"},
                        # "body": {} # Send empty body [] to Optimizer
                        "body": sal_reply_body_empty
                    }

                print(CFSBResponse)
                ## Send message to OPTIMIZER
                context.get_publisher('SendToOPT').send(CFSBResponse, application_id_optimizer, properties={'correlation_id': correlation_id_optimizer}, raw=True)
                print("Message to Optimizer has been sent from OPT-Triggering")
                print("-------------------------------------------------")

            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse message body from Optimizer as JSON: {e}")

        elif key == "OPT-Triggering-Multi":  # Handle Multiple Requests from Optimizer
            print("-------------------------------------------------")
            print("Entered in OPT-Multi-triggering with key: ", key)

            uuid.uuid4().hex.encode("utf-8")  # for Correlation id
            correlation_id_optimizer = message.correlation_id
            if not correlation_id_optimizer:
                correlation_id_optimizer = '88334290cad34ad9b21eb468a9f8ff11'  # dummy correlation_id

            print("Optimizer Correlation Id: ", correlation_id_optimizer)

            application_id_optimizer = message.subject
            if not application_id_optimizer:
                application_id_optimizer = 'd535cf554ea66fbebfc415ac837a5828'   # dummy application_id_optimizer

            try:
                ## Read the Message Sent from Optimizer
                opt_message_data = body
                print("Whole Message Sent from Optimizer Multi:", opt_message_data)
                print("-------------------------------------------------")

                ## Extract 'body' from opt_message_data
                # body_sent_from_optimizer = opt_message_data.get('body', {}) # Use ONLY for SENDER !!!
                body_sent_from_optimizer = json.loads(opt_message_data['body'])  # Parse the JSON string in body into a Python object (a list of lists in this case)
                print("Extracted body from Optimizer Message:", body_sent_from_optimizer)
                print("-------------------------------------------------")

                # Initialize a dictionary to insert every node by id
                unique_nodes_dict = {}   # Before Evaluation Check for Duplicates using the id
                list_number = 0 # Count the # of Lists and requests to SAL
                for requirement in body_sent_from_optimizer:
                    list_number += 1
                    print("Process List: ", list_number)
                    # print("Within requirements loop:", requirement)
                    requirement = json.dumps(requirement)   # Convert the body data to a JSON string

                    ## Prepare message to be sent to SAL
                    RequestToSal = {  # Dictionary
                        "metaData": {"user": "admin"},  # key [String "metaData"] value [dictionary]
                        "body": requirement  # key [String "body"] value [JSON String]
                    }
                    print("Request to SAL:", RequestToSal)
                    # print("Is RequestToSal a valid dictionary:", isinstance(RequestToSal, dict))
                    # print("Is the 'body' string in RequestToSal a valid JSON string:", is_json(RequestToSal["body"]))

                    ## Request the node candidates from SAL
                    sal_reply = context.publishers['SAL-GET'].send_sync(RequestToSal)

                    ## Process SAL's Reply
                    sal_body = sal_reply.get('body')  # Get the 'body' as a JSON string
                    if sal_body:
                        print("Request to SAL is OK: ", list_number)

                        # iterate over all nodes to keep unique nodes
                        nodes_by_requirement = json.loads(sal_body)
                        # print("nodes_by_requirement from OPT-Triggering-Multi: ", nodes_by_requirement)
                        nodes_per_list = len(nodes_by_requirement)
                        # print("Nuber of Nodes: ", nodes_per_list + "in List:", list_number)
                        print(f"Number of Nodes: {nodes_per_list} in List: {list_number}")

                        for node in nodes_by_requirement:
                            unique_nodes_dict[node["id"]] = node
                        print("------------------------------------------------------------")

                print("----------------List Loop is Ended--------------------------")
                print("Total Lists and Requests to SAL: ", list_number)
                print("Total unique nodes: " + str(len(unique_nodes_dict)))
                unique_list = list(unique_nodes_dict.values())

                try:
                    # here we do a change from the non multi request
                    nodes_data = unique_list
                    # Parse the JSON string to a Python object
                    # nodes_data = json.loads(sal_body)
                    # Check if there is any error in SAL's reply body
                    if 'key' in nodes_data and any(
                            keyword in nodes_data['key'].lower() for keyword in ['error', 'exception']):
                        print("Error found in SAL's message body using Multi:", nodes_data['message'])
                        sal_reply_body = []
                    else:  # No error found in SAL's reply body
                        total_nodes = len(nodes_data)  # Get the total number of nodes
                        print("Total Nodes in SAL's reply:", total_nodes)

                        if total_nodes > 400:  # Check if more than 400 nodes received
                            print("More than 400 nodes returned from SAL.")
                            # Filter to only include the first 400 nodes and convert back to JSON string
                            # sal_reply_body = json.dumps(nodes_data[:400])
                            sliced_data = nodes_data[:400]
                            sal_reply_body = json.dumps(sliced_data)
                        elif total_nodes > 0 and total_nodes <= 400:
                            # print(f"Total {total_nodes} nodes returned from SAL. Processing all nodes.")
                            # here we use nodes_data for multi requests instead of sal_reply_body = sal_body
                            sal_reply_body = json.dumps(nodes_data)
                        else:
                            sal_reply_body = []

                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON reply from SAL: {e}")
                    sal_reply_body = []  # Default to an empty JSON array as a string in case of error

                if sal_reply_body:  # Check whether SAL's reply body is empty
                    print("SAL reply Body:", sal_reply_body)

                    # Check the number of nodes before Evaluation
                    if total_nodes > 1:
                        # Search for application_id, Read JSON and create data to pass to Evaluation
                        if check_json_file_exists(application_id_optimizer):  # Application JSON exist in DB
                            print(f"JSON file for application ID {application_id_optimizer} exists.")

                            ###-------- Extract data from dummy JSON file --------###
                            # json_file_path = 'dummySALresponse.json'
                            # sal_reply_body = read_json_file_as_string(json_file_path)
                            ###-------- Extract data from dummy JSON file --------###

                            # Check if there are differences in available nodes between saved data in JSON file and SAL's reply
                            data_table, relative_wr_data, immediate_wr_data, node_names, node_ids = read_application_data(
                                application_id_optimizer, sal_reply_body)
                            # print("relative_wr_data:", relative_wr_data)
                            # print("immediate_wr_data:", immediate_wr_data)
                        else:  # Application does not exist in directory
                            # print(f"JSON file for application ID {application_id_optimizer} does not exist.")

                            ###-------- Extract data from SAL's response --------###
                            # Extract data from SAL's response
                            extracted_data_SAL, node_ids, node_names = extract_SAL_node_candidate_data(sal_reply_body)
                            ###-------- Extract data from SAL's response --------###

                            ###-------- Extract data from dummy JSON file --------###
                            # json_file_path = 'dummySALresponse.json'
                            # sal_reply_body = read_json_file_as_string(json_file_path)
                            # if sal_reply_body:
                            #     extracted_data_SAL, node_ids, node_names = extract_SAL_node_candidate_data(sal_reply_body)
                            ###-------- Extract data from dummy JSON file --------###

                            # print("extracted_data_SAL:", extracted_data_SAL)
                            print("node_ids:", node_ids)

                            # Use the create_criteria_mapping() to get the criteria mappings
                            # selected_criteria = ["Operating cost", "Memory Price", "Number of CPU Cores", "Memory Size", "Storage Capacity"]
                            selected_criteria = ["Number of CPU Cores", "Memory Size"]
                            field_mapping = create_criteria_mapping()
                            # Create data_table:
                            data_table = create_data_table(selected_criteria, extracted_data_SAL, field_mapping)
                            relative_wr_data = []
                            immediate_wr_data = []

                        # Check the number of nodes before Evaluation
                        print("There are " + str(len(node_ids)) + " nodes for Evaluation")

                        # Convert the original data of RAM and # of Cores, e.g. 1/X, if they are selected
                        # print("Original created_data_table:", data_table)
                        data_table = convert_data_table(data_table)  # Convert RAM and # of Cores, e.g. 1/X
                        # print("Converted created_data_table:", data_table)

                        ## Run evaluation
                        evaluation_results = perform_evaluation(data_table, relative_wr_data, immediate_wr_data,
                                                                node_names, node_ids)
                        # print("Evaluation Results:", evaluation_results)
                        print("lp status = " + str(evaluation_results.get('LPstatus')))

                        if evaluation_results.get('LPstatus') == 'feasible':
                            feasibility = True
                            ## Extract and Save the Results
                            # ScoresAndRanks = evaluation_results['results']
                            ScoresAndRanks = evaluation_results.get('results', [])
                            print("Scores and Ranks:", ScoresAndRanks)

                            # Append the Score and Rank of each node to SAL's Response
                            Evaluation_Results = append_evaluation_results(sal_reply_body, ScoresAndRanks)
                            #  print("Evaluation_Results:", Evaluation_Results)
                        else:
                            # problem is infeasible
                            feasibility = False
                            results = evaluation_results.get('results')
                            Evaluation_Results = results #  Evaluation_Results variable may contain info about the infeasible case also
                            print(results)
                    # when SAL returns only one node thus no evaluation needed
                    else:
                        feasibility = True
                        print("There is only one node!")
                        # Append the Score and Rank of each node to SAL's Response
                        Evaluation_Results = append_evaluation_results(sal_reply_body, [])

                    ## Prepare message to be sent to OPTIMIZER
                    # CFSBResponse = read_dummy_response_data_toOpt('CFSB_Body_Response.json')  # Data and Scores for 5 Nodes
                    CFSBResponse = {
                        "metaData": {"user": "admin"},
                        "body": Evaluation_Results
                    }

                    if feasibility:
                        # print("CFSBResponse:", CFSBResponse)
                        # Writing the formatted JSON to a json file
                        formatted_json = json.dumps(CFSBResponse, indent=4)
                        with open('CFSBResponse.json', 'w') as file:
                            file.write(formatted_json)
                            print("Data with Scores and Ranks for Nodes are saved to CFSBResponse.json")

                else:  # Then SAL's reply body is empty send an empty body to Optimizer
                    print("No Body in reply from SAL!")
                    sal_reply_body_empty = {
                        "message": "No resources returned from SAL"
                    }
                    CFSBResponse = {
                        "metaData": {"user": "admin"},
                        # "body": {} # Send empty body [] to Optimizer
                        "body": sal_reply_body_empty
                    }
                    # print(CFSBResponse)

                ## Send message to OPTIMIZER
                context.get_publisher('SendToOPTMulti').send(CFSBResponse, application_id_optimizer,
                                                        properties={'correlation_id': correlation_id_optimizer},
                                                        raw=True)
                print("Message to Optimizer has been sent from OPT-Triggering-Multi")
                print("-------------------------------------------------")
                print("Correlation Id sent from OPT-Triggering-Multi: ", correlation_id_optimizer)

            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse message body from Optimizer as JSON: {e}")



    def requestSAL(self, RequestToSal):
        sal_reply = Context.publishers['SAL-GET'].send_sync(RequestToSal)
        # Process SAL's Reply
        sal_body = sal_reply.get('body')  # Get the 'body' as a JSON string
        # print("sal_body requestSAL function:", sal_body)
        return sal_body

    def requestEmulate(self, RequestBody):
        reply = Context.publishers['OPT-Triggering-Multi'].send_sync(RequestBody)
        return reply

class Bootstrap(ConnectorHandler):
    context = None
    def ready(self, context: Context):
        self.context = context

def start_exn_connector_in_background():
     def run_connector():
        # connector_handler = Bootstrap()  # Initialize the connector handler
        # eu.nebulouscloud.exn.sal.nodecandidate.*
        addressSAL_GET = 'eu.nebulouscloud.exn.sal.nodecandidate.get'
        # addressSAL_GET_REPLY = 'eu.nebulouscloud.exn.sal.nodecandidate.get.reply'
        addressOPTtriggering = 'eu.nebulouscloud.cfsb.get_node_candidates'
        addressOPTtriggeringMulti = 'eu.nebulouscloud.cfsb.get_node_candidates_multi'
        addressSendToOPT = 'eu.nebulouscloud.cfsb.get_node_candidates.reply'
        addressSendToOPTMulti = 'eu.nebulouscloud.cfsb.get_node_candidates_multi.reply'


        connector = EXN('ui', url=os.getenv('NEBULOUS_BROKER_URL'), port=os.getenv('NEBULOUS_BROKER_PORT'), username=os.getenv('NEBULOUS_BROKER_USERNAME'), password=os.getenv('NEBULOUS_BROKER_PASSWORD'),
                        handler=Bootstrap(),
                        publishers=[
                            SyncedPublisher('SAL-GET', addressSAL_GET, True, True),
                            core.publisher.Publisher('SendToOPT', addressSendToOPT, True, True),
                            core.publisher.Publisher('SendToOPTMulti', addressSendToOPTMulti, True, True),
                            # SyncedPublisher('OPT-Triggering-Multi', addressOPTtriggeringMulti, True, True) # Publisher for OTP multi
                        ],
                        consumers=[
                            # Consumer('SAL-GET-REPLY', addressSAL_GET, handler=SyncedHandler(), topic=True, fqdn=True),
                            Consumer('OPT-Triggering', addressOPTtriggering, handler=SyncedHandler(), topic=True, fqdn=True),
                            Consumer('OPT-Triggering-Multi', addressOPTtriggeringMulti, handler=SyncedHandler(), topic=True, fqdn=True)
                        ])
        connector.start()

     ## Start the EXN connector in a thread
     thread = threading.Thread(target=run_connector)
     thread.daemon = True  # Daemon threads will shut down immediately when the program exits
     thread.start()


def call_publisher(body):
    handler = SyncedHandler()
    request = handler.requestSAL(body)
    return request


def call_otp_publisher(body):
    handler = SyncedHandler()
    request = handler.requestEmulate(body)
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
