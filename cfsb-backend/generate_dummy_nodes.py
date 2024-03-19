import json
import uuid
import random

def generate_dummy_nodes(k):
    nodes = []
    for _ in range(k):
        eu_west = random.randint(1, 3)
        city, country = random.choice([("Paris", "France"), ("Lyon", "France"), ("Marseille", "France")])
        latitude = round(random.uniform(40.0, 50.0), 4)
        longitude = round(random.uniform(2.0, 8.0), 4)

        node = {
            "id": str(uuid.uuid4()),
            "nodeCandidateType": random.choice(["EDGE", "IAAS", "PAAS", "SAAS"]),
            "jobIdForByon": None,
            "jobIdForEdge": None,
            "price": round(random.uniform(0.01, 0.1), 4),
            "cloud": {
                "id": f"nebulous-aws-sal-{eu_west}",
                "endpoint": None,
                "cloudType": "PUBLIC",
                "api": {"providerName": "aws-ec2"},
                "credential": None,
                "cloudConfiguration": {"nodeGroup": "", "properties": {}},
                "owner": None,
                "state": None,
                "diagnostic": None
            },
            "location": {
                "id": f"nebulous-aws-sal-{eu_west}/eu-west-{eu_west}",
                "name": f"eu-west-{eu_west}",
                "providerId": f"eu-west-{eu_west}",
                "locationScope": "REGION",
                "isAssignable": True,
                "geoLocation": {"city": city, "country": country, "latitude": latitude, "longitude": longitude},
                "parent": None,
                "state": None,
                "owner": None
            },
            # Repeating for 'image' and 'hardware' with appropriate modifications
            "score": round(random.uniform(0.7, 1.0), 5),
            # 'rank' will be assigned after sorting by score
        }
        # Additional details for 'image', 'hardware', etc., should follow the same pattern
        nodes.append(node)

    # Assign ranks after sorting nodes by score
    nodes_sorted_by_score = sorted(nodes, key=lambda x: x['score'], reverse=True)
    for index, node in enumerate(nodes_sorted_by_score):
        node['rank'] = index + 1

    return {"nodes": nodes_sorted_by_score}

# Assuming the function is defined as above, here's how you'd call it and use json.dump():
nodes_data = generate_dummy_nodes(1000)
file_path = 'CFSB_Body_Response_1000.json'  # Replace with your desired file path

with open(file_path, 'w') as file:
    json.dump(nodes_data, file, indent=4)

print(f"Data for 1000 nodes has been saved to {file_path}")
