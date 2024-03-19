Linguistic = 1
Float = 2
Seconds = 3
Percentage = 4
Boolean = 5
Integer = 6
Linguistic_bad = 7

# 1 for LOW, 2 for MEDIUM, etc.
linguistic_low_choices = ["Low", "Medium", "High"]
linguistic_very_low_choices = ["Very low", "LOW", "MEDIUM", "HIGH", "VERY HIGH", "PERFECT"]
linguistic_bad_choices = ["Bad", "OK", "Good"]
boolean_choices = ["True", "False"]

linguistic_low_attributes = [
    "attr-accountability-auditability",
    "attr-78baf8b3-2d1d-4899-88ef-ca74990f07eb",
    "attr-agility-adaptability",
    "attr-agility-portability",
    "attr-assurance-maintainability",
    "attr-assurance-service-stability",
    "attr-financial-structure",
    "attr-performance-accuracy",
    "attr-usability-installability",
    "attr-usability-learnability",
    "attr-usability-operability",
    "attr-usability-transparency",
    "attr-usability-understandability",
    "attr-usability-reusability",
    "d503cabe-17d7-4b9b-9231-a8b211f3ce11",
    'attr-reputation',
    "attr-reputation-contracting-experience",
    "attr-reputation-ease-of-doing-business",
    "attr-reputation-provider-ethicality",
    "attr-reputation-sustainability-economical-impact",
    "attr-reputation-sustainability-societal-impact"
]

linguistic_very_low_attributes = [
    "attr-assurance",  # TODO delete this, we keep it for testing
    "attr-assurance-serviceability-support-satisfaction"
]

linguistic_bad_attributes = [
    "attr-reputation-brand-name",
    "attr-reputation-service-reputation",
]

boolean_attributes = [
    "fd871ec6-d953-430d-a354-f13c66fa8bc9", "dcedb196-2c60-4c29-a66d-0e768cfd698a",
    "0cf00a53-fd33-4887-bb38-e0bbb04e3f3e", "d95c1dae-1e22-4fb4-9cdc-743e96d0dddc", "8cd09fe9-c119-4ccd-b651-0f18334dbbe4",
    "7147995c-8e68-4106-ab24-f0a7673eb5f5", "c1c5b3c9-6178-4d67-a7e3-0285c2bf98ef",
    "16030149-6fd5-4066-ac80-8da605dc964f", # Desired Move Support
    "attr-assurance-serviceability-free-support", # Free Support
    "c1c5b3c9-6178-4d67-a7e3-0285c2bf98ef", # Solid State Drive
    "attr-security-access-control-privilege-management-rbac",
    "bced9c2a-7234-44f8-9f51-ccd9da39f15e", # Attribute based Access Control supported(ABAC)
    "attr-security-data-privacy-loss-audit-trailing", "attr-security-proactive-threat-vulnerability-management-firewall-utm",
    "attr-security-management-encrypted-storage", "attr-security-management-transport-security-guarantees",
    "5759cddd-ec82-4273-88c4-5f55981469d0" # Process Transparency
]

time_in_seconds_attributes = [
    "attr-assurance-reliability",
]

# Resources stability
percentage_attributes = ["55a60ec3-55f7-48db-83bc-be2875c5210c",
    "attr-assurance-availability", "attr-reputation-provider-business-stability"]

# 11+3 (Secs) = 14. Uptime, CPU MFLOPs, GPU MFLOPS, Bandwidth, Upload Speed, Download Speed,
# Proximity to Data Source, Proximity to POI
float_attributes = ["49c8d03f-5ceb-4994-8257-cd319190a62a", "3b414a80-83b4-472c-8166-715d4c9d7508",
                    "b945c916-2873-4528-bc4a-e3b0c9d603d9", "876397bf-599f-40a7-91ec-93cca7c392b4",
                    "ea2e12db-b52a-42f4-86cb-f654cfe09a92", "e8180e25-d58c-49d3-862e-cbb18dd1820e",
                    "9f5706e3-08bd-412d-8d59-04f464e867a8", "b9f4f982-3809-4eac-831c-37288c046133",
                    "attr-reputation-sustainability-energy-consumption", "attr-reputation-sustainability-carbon-footprint",
                    "attr-assurance-recoverability-recovery-time", "attr-financial-cost-operation-cost",
                    "attr-performance-capacity-clock-speed"]

# Geographic Coverage, Total number of available Fog resources, Total number of available Edge devices,
# Number of GPU Cores, Storage, Network Throughput
integer_attributes = ["8968013b-e2af-487b-9140-25e6f857204c", "2da82ab2-8ae9-4aa2-a842-0d3f846c4b47",
                      "203ecada-25fd-469c-92f6-dd84f2c7cba6", "7a77f809-8aba-4550-9f0c-8b619183b1cd",
                      "47a2c5e9-f74d-4ff3-98fe-4c66b98eaaef", "6e648d7b-c09b-4c69-8c70-5030b2d21eed",
                      "attr-financial-cost-data-inbound", "attr-security-management-encryption-type",
                      "attr-financial-cost-data-outbound", "attr-performance-capacity-num-of-cores",
                      "attr-performance-capacity-memory-speed", "attr-performance-capacity-memory",
                      "attr-performance-capacity-storage-capacity", "attr-performance-capacity-storage-throughput",
                      "attr-agility-elasticity-time"]

# Features
unordered_set_attributes = ["7104ee2b-52ba-4655-991f-845a1397d850", "attr-assurance-serviceability-type-of-support",
                            "attr-security-access-control-privilege-management-authentication-schemes"]

def get_attr_data_type(attribute):
    data = {}
    # print("get type for " + attribute)
    if attribute in linguistic_low_attributes:
        data["type"] = 1
        data["values"] = linguistic_low_choices
    elif attribute in linguistic_very_low_attributes:
        data["type"] = 1
        data["values"] = linguistic_low_choices
    elif attribute in boolean_attributes:
        data["type"] = 5
        data["values"] = boolean_choices
    elif attribute in linguistic_bad_attributes:
        data["type"] = 1 # Instead of 7
        data["values"] = linguistic_low_choices
    elif attribute in float_attributes or attribute in percentage_attributes or attribute in integer_attributes:
        data["type"] = 2 # float, seconds or percentage or Integer
    # elif attribute in integer_attributes:
    #     data["type"] = 6 # Integer
    else: # all other cases Ordinal
        data["type"] = 1
        data["values"] = linguistic_low_choices
    #print(data)
    return data
