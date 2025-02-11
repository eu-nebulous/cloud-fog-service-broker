# ActiveMQ Communication Logic
import sys
import threading

sys.path.insert(0, '../exn')
import logging
from dotenv import load_dotenv
import get_data
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
        print_start_message()

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
                application_id_optimizer = 'd535cf554ea66fbebfc415ac837a5828'  # dummy application_id_optimizer
            # print("Application Id: ", application_id_optimizer)
            ## Read the Message Sent from Optimizer
            opt_message_data = body
            print("Whole Message Sent from Optimizer Single:", opt_message_data)
            ## Extract 'body' from opt_message_data
            body_sent_from_optimizer = opt_message_data.get('body', {})

            # if the body is str --> json it will be converted as python. On SAL we have to pass json.
            if isinstance(body_sent_from_optimizer, str):
                # print(type(body_sent_from_optimizer))
                try:
                    body_sent_from_optimizer = json.loads(body_sent_from_optimizer)
                except json.JSONDecodeError:
                    print("body_sent_from_optimizer is not json")

            print("-------------------------------------------------")
            print("Extracted body from Optimizer Message:", body_sent_from_optimizer)
            print("Check if the request should be handled as Multi or Single")
            # Check if the request should be handled as multi or single
            if isinstance(body_sent_from_optimizer, (list, str)):
                # print(type(body_sent_from_optimizer[0]))
                if isinstance(body_sent_from_optimizer[0], list):
                    print("The Request contains Multi lists")
                    self.handle_multi(application_id_optimizer, correlation_id_optimizer, body_sent_from_optimizer,
                                      context)
                else:
                    print("The Request contains a Single list")
                    body_sent_from_optimizer = json.dumps(body_sent_from_optimizer) # When SENDER is used then Convert the body data to a JSON string
                    self.handle_single(application_id_optimizer, correlation_id_optimizer, body_sent_from_optimizer,
                                       context)
            else:
                print("No list in body")

        elif key == "OPT-Triggering-Multi":  # Handle Multiple Requests from Optimizer
            print("Entered in OPT-Multi-triggering with key: ", key)
            uuid.uuid4().hex.encode("utf-8")  # for Correlation id
            correlation_id_optimizer = message.correlation_id
            if not correlation_id_optimizer:
                correlation_id_optimizer = '88334290cad34ad9b21eb468a9f8ff11'  # dummy correlation_id
            print("Optimizer Correlation Id: ", correlation_id_optimizer)

            application_id_optimizer = message.subject
            if not application_id_optimizer:
                application_id_optimizer = 'd535cf554ea66fbebfc415ac837a5828'  # dummy application_id_optimizer

            ## Read the Message Sent from Optimizer
            opt_message_data = body
            print("Whole Message Sent from Optimizer Multi:", opt_message_data)
            print("-------------------------------------------------")

            ## Extract 'body' from opt_message_data
            # body_sent_from_optimizer = json.loads(opt_message_data['body'])  # Comment this when on sender - Parse the JSON string in body into a Python object (a list of lists in this case)
            body_sent_from_optimizer = opt_message_data.get('body', {})  # Use ONLY for SENDER !!!
            if isinstance(body_sent_from_optimizer, str):
                # print(type(body_sent_from_optimizer))
                try:
                    body_sent_from_optimizer = json.loads(body_sent_from_optimizer)
                except json.JSONDecodeError:
                    print("body_sent_from_optimizer is not json")

            print("Extracted body from Optimizer Message:", body_sent_from_optimizer)
            print("-------------------------------------------------")
            print("Check if the request should be handled as Multi or Single")
            # check if request should be handled as multi or single
            if isinstance(body_sent_from_optimizer, (list, str)):
                # print(type(body_sent_from_optimizer[0]))
                if isinstance(body_sent_from_optimizer[0], list):
                    print("The Request contains Multi lists")
                    self.handle_multi(application_id_optimizer, correlation_id_optimizer, body_sent_from_optimizer,
                                      context)
                else:
                    print("The Request contains a Single list")
                    body_sent_from_optimizer = json.dumps(body_sent_from_optimizer)  # When SENDER is used then Convert the body data to a JSON string
                    self.handle_single(application_id_optimizer, correlation_id_optimizer, body_sent_from_optimizer,
                                       context)

    def handle_single(self, application_id_optimizer, correlation_id_optimizer, body_json_string, context):
        try:
            ## Prepare message to be send to SAL
            # locations = []
            print("--------Before Retrieving Locations --------")
            print("Message to SAL:", body_json_string)
            body_json_string, locations = remove_request_attribute('CFSB-datasource-geolocations', json.loads(body_json_string))
            print("--------After Retrieving Locations --------")
            # print(body_json_string)
            if locations:
                print("The Locations sent from Optimizer are: ", locations)
                body_json_string = json.dumps(body_json_string)  # Convert the body data to a JSON string

            RequestToSal = {  # Dictionary
                "metaData": {"user": "admin"},  # key [String "metaData"] value [dictionary]
                "body": body_json_string  # key [String "body"] value [JSON String]
            }
            print("Request to SAL:", RequestToSal)
            # print("Is RequestToSal a valid dictionary:", isinstance(RequestToSal, dict))
            # print("Is the 'body' string in RequestToSal a valid JSON string:", is_json(RequestToSal["body"]))

            ## Request the node candidates from SAL
            sal_reply = context.publishers['SAL-GET'].send_sync(RequestToSal)

            ## Process SAL's Reply
            if sal_reply is not None and sal_reply != '':
                sal_body = sal_reply.get('body')  # Get the 'body' as a JSON string Replace sal_body with sal_reply_body
            else:
                sal_body = '{"key": "error", "message": "SAL did not reply or returned empty response"}'

            try:
                # Parse the JSON string to a Python object
                nodes_data = json.loads(sal_body)
                # Check if there is any error in SAL's reply body
                if 'key' in nodes_data and any(
                        keyword in nodes_data['key'].lower() for keyword in ['error', 'exception']):
                    print("Error found in SAL's message body:", nodes_data['message'])
                    sal_reply_body = '' # Make it an Empty string in case of error
                else:  # No error found in SAL's reply body
                    total_nodes = len(nodes_data)  # Get the total number of nodes
                    sal_reply_body = sal_body # Keep sal_reply_body as is since it's already a JSON string
                    print("Total Nodes in SAL's reply:", total_nodes)

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON reply from SAL: {e}")
                sal_reply_body = '' #  Make it an Empty string in case of error

            if sal_reply_body.strip() not in ('', '[]'): # Check whether SAL's reply body is empty
                # print("SAL reply Body:", sal_reply_body)
                # print(type(sal_reply_body))  # Check the data type
                # print(f"Raw content: {repr(sal_reply_body)}")

                # Check the number of nodes before Evaluation
                if total_nodes > 1:
                    # Search for application_id, Read JSON and create data to pass to Evaluation
                    if check_json_file_exists(application_id_optimizer):  # Application JSON exist in DB
                        print(f"JSON file for application ID {application_id_optimizer} exists.")

                        # The read_application_data returns int the app_data the policy from the saved file, in order to check it to do the convert or not.
                        app_data, selected_criteria, provider_criteria, relative_wr_data, immediate_wr_data = read_application_data(application_id_optimizer)
                        extracted_data_SAL, node_ids, node_names, providers = extract_SAL_node_candidate_data_NEW(sal_reply_body, app_data, application_id_optimizer,selected_criteria)
                        data_table = create_data_table(extracted_data_SAL, selected_criteria, provider_criteria, locations)
                        # print("relative_wr_data:", relative_wr_data)
                        # print("immediate_wr_data:", immediate_wr_data)
                    else:  # Application does not exist in directory
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
                        app_data = {"app_specific": 0}
                        extracted_data_SAL, node_ids, node_names, providers = extract_SAL_node_candidate_data_NEW(
                            sal_reply_body, app_data, application_id_optimizer, selected_criteria)

                        # Create data_table:
                        # provider_criteria do not exist when the application file does not exist. None is treated like false
                        data_table = create_data_table(extracted_data_SAL, selected_criteria, None, locations)
                        print(data_table)
                        relative_wr_data = []
                        immediate_wr_data = []
                        # create default app_data dictionary for policy and app_specific when file not exists for the application
                        app_data = {'policy': '0', 'app_specific': False}

                    # Check the number of nodes before Evaluation
                    print("There are " + str(len(node_ids)) + " nodes for Evaluation")

                    # Convert the original data of RAM and # of Cores, e.g. 1/X, if they are selected
                    print("Original data_table:", data_table)
                    # TODO: INCORPORATE THIS INTO create_data_table function
                    if (app_data['policy'] == '0'):
                        data_table = convert_data_table(data_table)  # Convert RAM and # of Cores, e.g. 1/X
                        print("Converted data_table:", data_table)
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
                        # Check the length and truncate if necessary
                        if len(ScoresAndRanks) > 250:
                            print("More than: ", len(ScoresAndRanks))
                            ScoresAndRanks = ScoresAndRanks[:250]
                            print("Now: ", len(ScoresAndRanks))
                        # print("Scores and Ranks:", ScoresAndRanks)

                        # Append the Score and Rank of each node to SAL's Response
                        Evaluation_Results = append_evaluation_results(sal_reply_body, ScoresAndRanks)
                        #  print("Evaluation_Results:", Evaluation_Results)
                    else:
                        # problem is infeasible
                        feasibility = False
                        results = evaluation_results.get('results')
                        Evaluation_Results = results  # Evaluation_Results variable may contain info about the infeasible case also
                # when SAL returns only ΟΝΕ node thus no evaluation needed
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
                    with open('CFSB_Response.json', 'w') as file:
                        file.write(formatted_json)
                        print("Data with Scores and Ranks for Nodes are saved to CFSB_Response.json")

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

            ## Send message to OPTIMIZER
            context.get_publisher('SendToOPT').send(CFSBResponse, application_id_optimizer,
                                                    properties={'correlation_id': correlation_id_optimizer}, raw=True)
            print("-------------------------------------------------")
            print("Message to Optimizer has been sent from OPT-Triggering")

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse message body from Optimizer as JSON: {e}")
        print_end_message()

    def handle_multi(self, application_id_optimizer, correlation_id_optimizer, body_sent_from_optimizer, context):
        try:
            # Initialize a dictionary to insert every node by id
            unique_nodes_dict = {}  # Before Evaluation Check for Duplicates using the id
            list_number = 0  # Count the # of Lists and requests to SAL
            locations = []
            for requirement in body_sent_from_optimizer:
                list_number += 1
                print("Process List: ", list_number)
                # print("Within requirements loop:", requirement)
                print("--------Before Removal--------")
                print(requirement)
                requirement, locations = remove_request_attribute('CFSB-datasource-geolocations', requirement)
                print("--------After Removal--------")
                print(requirement)
                if locations:
                    print(locations)
                requirement = json.dumps(requirement)  # Convert the body data to a JSON string

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

                ## Process SAL's Reply if sal_reply is not None and sal_reply != '' and isinstance(sal_reply, dict):
                if sal_reply is None or sal_reply == '':
                    print("SAL did not reply or returned empty response")
                    continue

                sal_body = sal_reply.get('body')  # Get the 'body' as a JSON string
                if sal_body:
                    print("SAL Replied Successfully: ", list_number)
                    # iterate over all nodes to keep unique nodes
                    nodes_by_requirement = json.loads(sal_body)
                    # print("nodes_by_requirement from OPT-Triggering-Multi: ", nodes_by_requirement)
                    nodes_per_list = len(nodes_by_requirement)
                    print(f"Number of Nodes: {nodes_per_list} in List: {list_number}")

                    for node in nodes_by_requirement:
                        unique_nodes_dict[node["id"]] = node
                    print("------------------------------------------------------------")

            print("----------------List Loop is Ended--------------------------")
            print("Total Lists and Requests to SAL: ", list_number)
            print("Total unique nodes: " + str(len(unique_nodes_dict)))
            unique_list = list(unique_nodes_dict.values())

            try:
                # here we do a change from the SINGLE request
                nodes_data = unique_list
                # Check if there is any error in SAL's reply body
                if 'key' in nodes_data and any(
                        keyword in nodes_data['key'].lower() for keyword in ['error', 'exception']):
                    print("Error found in SAL's message body using Multi:", nodes_data['message'])
                    sal_reply_body = []
                else:  # No error found in SAL's reply body
                    total_nodes = len(nodes_data)  # Get the total number of nodes
                    print("Total Nodes in SAL's reply:", total_nodes)
                    sal_reply_body = json.dumps(nodes_data)

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON reply from SAL: {e}")
                sal_reply_body = ''  # Make it an Empty string in case of error

            if sal_reply_body.strip() not in ('', '[]'): # Check whether SAL's reply body is empty
                # print("SAL reply Body:", sal_reply_body)
                # Check the number of nodes before Evaluation
                if total_nodes > 1:
                    # Search for application_id, Read JSON and create data to pass to Evaluation
                    if check_json_file_exists(application_id_optimizer):  # Application JSON exist in DB
                        print(f"JSON file for application ID {application_id_optimizer} exists.")

                        # The read_application_data returns in app_data the policy from the saved file to check it and convert or not
                        app_data, selected_criteria, provider_criteria, relative_wr_data, immediate_wr_data = read_application_data(
                            application_id_optimizer)
                        extracted_data_SAL, node_ids, node_names, providers = extract_SAL_node_candidate_data_NEW(
                            sal_reply_body, app_data, application_id_optimizer, selected_criteria)
                        data_table = create_data_table(extracted_data_SAL, selected_criteria, provider_criteria,
                                                       locations)
                        # print("relative_wr_data:", relative_wr_data)
                        # print("immediate_wr_data:", immediate_wr_data)
                    else:  # Application does not exist in directory
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
                        app_data = {"app_specific": 0}
                        extracted_data_SAL, node_ids, node_names, providers = extract_SAL_node_candidate_data_NEW(
                            sal_reply_body, app_data, application_id_optimizer, selected_criteria)
                        # Create data_table:
                        # provider_criteria do not exist when the application file does not exist. None is treated like false
                        data_table = create_data_table(extracted_data_SAL, selected_criteria, None, locations)

                        relative_wr_data = []
                        immediate_wr_data = []
                        # create default app_data dictionary for policy and app_specific when file not exists for the application
                        app_data = {'policy': '0', 'app_specific': False} # Use the default policy (minimal)
                        # print("app_data:", app_data['policy'])

                    # Check the number of nodes before Evaluation
                    print("There are " + str(len(node_ids)) + " nodes for Evaluation")
                    print("Original Data", data_table)
                    # Convert the original data of RAM and # of Cores, e.g. 1/X, if they are selected
                    if (app_data['policy'] == '0'):
                        data_table = convert_data_table(data_table)  # Convert RAM and # of Cores, e.g. 1/X
                        print("Converted data_table:", data_table)
                    else:
                        print("Policy is MAX for this application")

                    # Calculate the simple average score for each node
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
                        # Check the length and truncate if necessary
                        if len(ScoresAndRanks) > 250:
                            print("More than: ", len(ScoresAndRanks))
                            ScoresAndRanks = ScoresAndRanks[:250]
                            print("Now: ", len(ScoresAndRanks))
                        # print("Scores and Ranks:", ScoresAndRanks)

                        # Append the Score and Rank of each node to SAL's Response
                        Evaluation_Results = append_evaluation_results(sal_reply_body, ScoresAndRanks)
                        #  print("Evaluation_Results:", Evaluation_Results)
                    else:
                        # problem is infeasible
                        feasibility = False
                        results = evaluation_results.get('results')
                        Evaluation_Results = results  # Evaluation_Results variable may contain info about the infeasible case also
                        print(results)

                else: # SAL returned only one node, thus no evaluation needed
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
                    with open('CFSB_Response.json', 'w') as file:
                        file.write(formatted_json)
                        print("Data with Scores and Ranks for Nodes are saved to CFSB_Response.json")

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
            print("-------------------------------------------------")
            print("Message to Optimizer has been sent from OPT-Triggering-Multi")
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
        reply = Context.publishers[RequestBody['key']].send_sync(RequestBody)
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

        connector = EXN('ui', url=os.getenv('NEBULOUS_BROKER_URL'), port=os.getenv('NEBULOUS_BROKER_PORT'),
                        username=os.getenv('NEBULOUS_BROKER_USERNAME'), password=os.getenv('NEBULOUS_BROKER_PASSWORD'),
                        handler=Bootstrap(),
                        publishers=[
                            SyncedPublisher('SAL-GET', addressSAL_GET, True, True),
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


def call_publisher(body):
    handler = SyncedHandler()
    request = handler.requestSAL(body)
    return request


def call_otp_publisher(body):
    handler = SyncedHandler()
    request = handler.requestEmulate(body)
    return request


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

def print_start_message():
    ascii_art = """
  CCCC   FFFFF  SSSSS  BBBBB  
 C       F      S      B    B     
 C       FFF    SSSSS  BBBBB      
 C       F          S  B    B
  CCCC   F      SSSSS  BBBBB
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "="*50)
    print(ascii_art)
    print(f"Started to Process the Received Request at Timestamp: {timestamp:^50}")
    print("="*50 + "\n")


def print_end_message():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Use datetime.now() directly
    print("\n" + "="*50)
    print(f"{'CFSB Evaluation has been Completed':^50}")
    print(f"Timestamp: {timestamp:^50}")
    print("="*50 + "\n")
