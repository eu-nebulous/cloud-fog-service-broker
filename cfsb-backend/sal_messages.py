def create_edge_sal_message(app_specific_setting, app_id):
    # convert what is needed - app_specific_setting comes as string
    if app_specific_setting == 1 or app_specific_setting == "1":
        app_specific = True
    elif app_specific_setting == 0 or app_specific_setting == "0":
        app_specific = False
    else:
        app_specific = False

    if app_id == "dummy-application-id-123" or app_id == "":
        app_specific = False

    typeRequirement = "NodeTypeRequirement"
    nodeTypes = ["EDGE"]
    base_sal_message = [
        {
        "type": typeRequirement,
        "nodeTypes": nodeTypes,
        "jobIdForEDGE": "",
        "jobIdForBYON": "",
        }
    ]
    print("prepare message")
    message_for_SAL = list(base_sal_message)
    # print(base_sal_message)

    app_specific_message = {
        "type": "AttributeRequirement",
        "requirementClass": "hardware",
        "requirementAttribute": "name",
        "requirementOperator": "INC",
        "value": "application_id|"
    }
    if app_specific:
        app_specific_message["value"] = "application_id|" + app_id
    else:
        app_specific_message["value"] = "application_id|all-applications"

    message_for_SAL.append(app_specific_message)
    print("sal_messages: " + str(message_for_SAL))

    return message_for_SAL

def create_iaas_resources_message(app_id):
    message_for_SAL = {
        "appId": str(app_id),
    }
    return message_for_SAL

def create_iaas_sal_message(cloud_id):
    message_for_SAL = [
        {
            "type": "NodeTypeRequirement",
            "nodeTypes": ["IAAS"],
            "jobIdForEDGE": "",
            "jobIdForBYON": "",
        },
        {
            "type": "AttributeRequirement",
            "requirementClass": "cloud",
            "requirementAttribute": "id",
            "requirementOperator": "EQ", "value": str(cloud_id)
        }
    ]
    return message_for_SAL

# print(create_sal_message(0, str(1)))
# iaas_app_id = "160281af-1ac6-4abb-9398-dab35a241e43"