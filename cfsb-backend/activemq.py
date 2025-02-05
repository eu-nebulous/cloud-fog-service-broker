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


VALID_AWS_INSTANCE_TYPES ="c6a.24xlarge, g5.2xlarge, r7iz.12xlarge, g6.24xlarge, m4.4xlarge, m5ad.12xlarge, u7i-6tb.112xlarge, m6idn.large, i3en.3xlarge, r6in.24xlarge, c3.large, c4.4xlarge, t2.2xlarge, m6id.xlarge, c6a.16xlarge, r6a.2xlarge, r3.large, r7iz.8xlarge, r5.24xlarge, i7ie.18xlarge, d3en.2xlarge, m5n.16xlarge, m6id.2xlarge, r7a.2xlarge, x1e.2xlarge, m6a.2xlarge, r6a.metal, m5zn.2xlarge, m7i-flex.12xlarge, r5dn.8xlarge, c5ad.24xlarge, c6in.24xlarge, r5a.2xlarge, r7iz.16xlarge, r6id.16xlarge, g6e.48xlarge, f1.2xlarge, c6in.xlarge, r5n.12xlarge, r6a.xlarge, c7i.2xlarge, r7a.xlarge, c5n.2xlarge, m7i.metal-24xl, g6e.8xlarge, x2iedn.2xlarge, r6idn.16xlarge, m7i.16xlarge, i3en.12xlarge, i7ie.24xlarge, inf2.48xlarge, i4i.16xlarge, g5.4xlarge, c6id.8xlarge, c6i.32xlarge, x1e.8xlarge, t1.micro, x2iezn.4xlarge, m2.4xlarge, r5a.xlarge, r6i.xlarge, m5a.16xlarge, c7a.xlarge, trn1.32xlarge, m5a.2xlarge, c3.8xlarge, m5dn.12xlarge, r6in.metal, m5d.xlarge, i3en.24xlarge, r6id.12xlarge, x2iedn.xlarge, c5ad.12xlarge, i7ie.xlarge, m6id.32xlarge, c6i.2xlarge, r7iz.xlarge, m7i.8xlarge, m5zn.6xlarge, m5zn.large, m6idn.12xlarge, r7a.4xlarge, r6idn.xlarge, m6idn.4xlarge, r3.8xlarge, r6in.12xlarge, inf2.8xlarge, z1d.2xlarge, trn1n.32xlarge, m5dn.2xlarge, d3en.8xlarge, t3a.2xlarge, c4.8xlarge, m5ad.large, c6i.4xlarge, trn1.2xlarge, m7a.xlarge, c7a.large, c7i-flex.16xlarge, c7a.medium, r6idn.8xlarge, c5.4xlarge, i4i.24xlarge, m6a.large, i2.2xlarge, m5d.8xlarge, r5b.12xlarge, m6id.12xlarge, c5d.large, c7i-flex.8xlarge, r7a.32xlarge, x1e.32xlarge, r6id.xlarge, c6id.24xlarge, m7i.2xlarge, m5.24xlarge, c6a.48xlarge, m6i.24xlarge, c6i.8xlarge, c7i.8xlarge, m5.12xlarge, c5n.large, c6i.large, m7i.24xlarge, x1.16xlarge, d2.8xlarge, r6idn.2xlarge, c6a.32xlarge, m7i-flex.2xlarge, r4.16xlarge, r6id.2xlarge, m5dn.large, m6i.large, r7iz.32xlarge, c5ad.4xlarge, m5a.4xlarge, m5.8xlarge, r5ad.24xlarge, m5ad.4xlarge, c5d.12xlarge, c7i-flex.2xlarge, r7i.metal-48xl, c7a.metal-48xl, u7i-12tb.224xlarge, c6in.12xlarge, p2.8xlarge, m5d.16xlarge, m6in.12xlarge, r5a.16xlarge, m5d.large, m5d.metal, c5n.4xlarge, r5b.metal, c6id.large, x2idn.24xlarge, m6in.32xlarge, g6.8xlarge, i7ie.3xlarge, r5n.4xlarge, g4dn.12xlarge, r6id.4xlarge, g6.48xlarge, m5.xlarge, c7a.2xlarge, m2.2xlarge, c6in.16xlarge, c5ad.16xlarge, c7a.4xlarge, g4ad.8xlarge, g4ad.2xlarge, c5a.4xlarge, t3.2xlarge, u-3tb1.56xlarge, g5.24xlarge, g4dn.metal, m6in.16xlarge, r6i.24xlarge, m5.metal, i4i.4xlarge, m5dn.xlarge, r5ad.8xlarge, r5ad.12xlarge, inf1.xlarge, m7a.32xlarge, r7a.large, m7a.16xlarge, t3.medium, r7a.medium, m6a.metal, m6in.24xlarge, t3.xlarge, z1d.xlarge, c5.xlarge, r5a.large, i7ie.12xlarge, r6idn.24xlarge, c6i.24xlarge, g4ad.4xlarge, r7iz.metal-16xl, r6a.12xlarge, d3.8xlarge, d2.2xlarge, m5ad.2xlarge, c5a.12xlarge, x2iezn.8xlarge, r7i.16xlarge, t3a.small, r5a.12xlarge, r6a.32xlarge, r6in.large, c5d.2xlarge, m5ad.8xlarge, g6e.16xlarge, m6i.8xlarge, i4i.metal, m5dn.8xlarge, r6i.4xlarge, c4.large, m6idn.xlarge, r7i.2xlarge, p3.2xlarge, d3en.4xlarge, r5b.large, r5ad.large, c6a.8xlarge, c5n.9xlarge, d3.2xlarge, m7i.48xlarge, x2iedn.metal, r5.large, r5n.16xlarge, vt1.6xlarge, c7a.12xlarge, h1.2xlarge, u-12tb1.112xlarge, c7i.16xlarge, vt1.3xlarge, c5ad.xlarge, r5.4xlarge, r5b.24xlarge, m6i.metal, c7a.8xlarge, h1.8xlarge, m6i.16xlarge, c6in.8xlarge, c6i.16xlarge, c7i-flex.4xlarge, r5dn.xlarge, m5zn.3xlarge, t3.large, r7i.8xlarge, g6e.12xlarge, m5n.12xlarge, m4.xlarge, t2.micro, r7i.12xlarge, m5n.8xlarge, r5d.4xlarge, c7i-flex.xlarge, c5.12xlarge, inf1.6xlarge, c5a.2xlarge, c5d.24xlarge, t3a.medium, r6a.8xlarge, c6a.12xlarge, i7ie.48xlarge, r5.metal, i4i.2xlarge, c6in.2xlarge, c5a.24xlarge, c6id.16xlarge, u7in-24tb.224xlarge, r3.2xlarge, r6id.32xlarge, d3.xlarge, c7i.metal-24xl, r3.4xlarge, t2.large, m4.large, c7i.xlarge, c5a.xlarge, inf2.24xlarge, c7i.large, r5a.4xlarge, u-6tb1.56xlarge, inf1.2xlarge, m6i.32xlarge, c4.2xlarge, m6in.4xlarge, c7i.24xlarge, m5zn.12xlarge, r7a.24xlarge, m6a.4xlarge, m5d.24xlarge, m5n.metal, c5.metal, c3.xlarge, m5n.large, r7i.metal-24xl, r6a.48xlarge, u-24tb1.112xlarge, d3en.6xlarge, r5d.large, c5ad.2xlarge, i2.xlarge, u-6tb1.112xlarge, r5.16xlarge, c7i-flex.12xlarge, m6in.metal, m5.4xlarge, r5n.24xlarge, m3.xlarge, m5n.4xlarge, c6id.32xlarge, x2idn.metal, c5.24xlarge, g5.12xlarge, r6a.4xlarge, r5d.xlarge, c7i-flex.large, r5b.4xlarge, m6i.4xlarge, h1.4xlarge, r5d.16xlarge, t3.nano, m5dn.metal, r5dn.metal, c5d.18xlarge, c5.9xlarge, m6idn.32xlarge, m4.16xlarge, m1.xlarge, u7in-16tb.224xlarge, c6in.large, m5a.8xlarge, r7iz.2xlarge, r5n.2xlarge, r4.2xlarge, m7a.medium, p5.48xlarge, c5n.18xlarge, r5d.24xlarge, c5d.4xlarge, x2iezn.12xlarge, p4d.24xlarge, m5zn.metal, r5dn.large, r5b.2xlarge, r6in.32xlarge, r6id.24xlarge, c6a.metal, r5d.2xlarge, h1.16xlarge, r5b.xlarge, c6id.metal, r7i.large, r5dn.12xlarge, t3.micro, m6id.metal, g6.xlarge, i2.8xlarge, x2idn.16xlarge, r5d.8xlarge, c4.xlarge, inf2.xlarge, m7a.4xlarge, m6in.large, c7a.24xlarge, r5b.16xlarge, g6.2xlarge, c7a.48xlarge, m6id.16xlarge, m6idn.2xlarge, g5.16xlarge, m7a.48xlarge, c5a.16xlarge, m5.16xlarge, t3a.large, m7a.8xlarge, z1d.metal, r6i.12xlarge, m6a.16xlarge, r3.xlarge, g4dn.xlarge, x1e.16xlarge, r5.8xlarge, r6idn.large, r6in.4xlarge, z1d.12xlarge, r5.xlarge, m4.2xlarge, c6in.32xlarge, r7a.metal-48xl, i3.xlarge, r6in.8xlarge, r6idn.4xlarge, i3.large, m7i-flex.16xlarge, r6i.16xlarge, r7i.xlarge, c6a.xlarge, m7a.12xlarge, m3.2xlarge, t2.medium, c6a.4xlarge, c5.large, u7i-8tb.112xlarge, m6idn.24xlarge, c5n.metal, m7a.24xlarge, c7i.metal-48xl, c7a.16xlarge, m7i-flex.4xlarge, m6idn.metal, r5ad.2xlarge, m5ad.24xlarge, x2iedn.4xlarge, i2.4xlarge, m6in.xlarge, r4.xlarge, c7a.32xlarge, r5dn.16xlarge, r5ad.16xlarge, m5ad.xlarge, c3.4xlarge, i4i.large, r6a.24xlarge, r6id.large, m7a.2xlarge, m5n.2xlarge, g4dn.16xlarge, r4.8xlarge, vt1.24xlarge, x1e.xlarge, r6idn.metal, m5.large, r5d.metal, m5dn.4xlarge, c5ad.8xlarge, t2.xlarge, x2iezn.6xlarge, c7i.12xlarge, m5a.large, c3.2xlarge, m7i.xlarge, m5zn.xlarge, g6e.4xlarge, c5d.xlarge, m5d.12xlarge, c7i.4xlarge, i3.16xlarge, x2iedn.16xlarge, m5n.24xlarge, d2.4xlarge, r4.large, r5ad.xlarge, p3.16xlarge, c5.2xlarge, r6i.metal, z1d.large, m5.2xlarge, r5.2xlarge, m4.10xlarge, i4i.12xlarge, m5dn.16xlarge, r5n.8xlarge, x2idn.32xlarge, g5.xlarge, c5d.metal, i3en.2xlarge, r7i.24xlarge, i3.8xlarge, r6idn.32xlarge, r5.12xlarge, m5n.xlarge, c6id.12xlarge, m6idn.8xlarge, g4ad.16xlarge, r7iz.metal-32xl, r7a.8xlarge, r5n.xlarge, r6id.8xlarge, x2iezn.metal, g6.12xlarge, c5a.8xlarge, m7i.large, f2.48xlarge, r5ad.4xlarge, z1d.6xlarge, m6i.xlarge, m5dn.24xlarge, m6id.4xlarge, x2iedn.24xlarge, r6id.metal, x2iezn.2xlarge, r6in.16xlarge, dl1.24xlarge, g6.16xlarge, m7i-flex.8xlarge, r6a.16xlarge, c6in.4xlarge, m5d.2xlarge, c5ad.large, i4i.32xlarge, x1.32xlarge, r6i.8xlarge, m6id.24xlarge, c6id.4xlarge, g6.4xlarge, m5a.xlarge, m6idn.16xlarge, r7a.12xlarge, m6id.8xlarge, m5a.24xlarge, p2.xlarge, m3.medium, m7i.12xlarge, c6a.2xlarge, r6i.32xlarge, r7a.16xlarge, i3.4xlarge, gr6.4xlarge, m7i-flex.large, t3.small, inf1.24xlarge, m6id.large, c6id.xlarge, gr6.8xlarge, r5b.8xlarge, m2.xlarge, m7i.4xlarge, u-18tb1.112xlarge, c6i.metal, i3en.large, r6a.large, g5.48xlarge, m6in.8xlarge, x2iedn.32xlarge, m6a.24xlarge, r7i.48xlarge, f2.12xlarge, m6a.xlarge, m5ad.16xlarge, t2.nano, m3.large, c6id.2xlarge, r5a.24xlarge, m6a.32xlarge, d3.4xlarge, i3.2xlarge, c6i.12xlarge, m6in.2xlarge, m6a.8xlarge, r6idn.12xlarge, x1e.4xlarge, r5a.8xlarge, g6e.xlarge, g6e.2xlarge, p3.8xlarge, t2.small, r5d.12xlarge, r5dn.2xlarge, c6i.xlarge, i4i.xlarge, t3a.nano, i3.metal, p2.16xlarge, u7in-32tb.224xlarge, g5.8xlarge, m7a.metal-48xl, x2iedn.8xlarge, i3en.xlarge, r5dn.4xlarge, r6in.xlarge, m6a.12xlarge, r7i.4xlarge, g6e.24xlarge, c5n.xlarge, r6i.large, g4dn.2xlarge, d3en.12xlarge, d3en.xlarge, c5.18xlarge, g4dn.4xlarge, r7iz.large, m7i.metal-48xl, r7a.48xlarge, i3en.6xlarge, m7a.large, i3en.metal, r5n.large, r7iz.4xlarge, p3dn.24xlarge, i7ie.large, m7i-flex.xlarge, u-9tb1.112xlarge, m1.small, i4i.8xlarge, m6i.2xlarge, g4dn.8xlarge, i7ie.2xlarge, r5dn.24xlarge, c6in.metal, f1.16xlarge, r6in.2xlarge, t3a.xlarge, t3a.micro, c5a.large, m5a.12xlarge, f1.4xlarge, r4.4xlarge, d2.xlarge, m6a.48xlarge, c5d.9xlarge, m1.medium, g4ad.xlarge, m6i.12xlarge, c7i.48xlarge, r5n.metal, m1.large, m5d.4xlarge, c6a.large, r6i.2xlarge, z1d.3xlarge, i7ie.6xlarge"

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

                        # Remove nodes that have a value for jobIdForEdge
                        filtered_nodes_data = []
                        for node in nodes_data:
                            if ("jobIdForEdge" in node and node["jobIdForEdge"] not in [None, "any","all-applications"]):
                                print(f"Skipping used node {node['id']} on {node['jobIdForEdge']}")
                                continue
                            else:
                                filtered_nodes_data.append(node)
                        nodes_data = filtered_nodes_data

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

                        # Remove nodes that have a value for jobIdForEdge
                        filtered_nodes_by_requirement = []
                        for node in nodes_by_requirement:
                            if ("jobIdForEdge" in node and node["jobIdForEdge"] not in [None, "any", "all-applications"]):
                                print(f"Skipping used node {node['id']} on {node['jobIdForEdge']}")
                                continue
                            else:
                                filtered_nodes_by_requirement.append(node)
                        nodes_by_requirement = filtered_nodes_by_requirement


                        # Remove aws invalid instance types
                        # This is a temporary workaround to be removed when proper node candidate filtering is in place.
                        filtered_nodes_by_requirement = []
                        for node in nodes_by_requirement:
                            if ("cloud" in node and "api" in node["cloud"] and "providerName" in node["cloud"]["api"] and "aws-ec2" == node["cloud"]["api"]["providerName"] and node["hardware"]["name"] not in VALID_AWS_INSTANCE_TYPES):
                                print(f"Skipping invalid instance type {node['hardware']['name']}")
                                continue
                            else:
                                filtered_nodes_by_requirement.append(node)
                        nodes_by_requirement = filtered_nodes_by_requirement
                        ########




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
