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
linguistic_bad_choices = ["BAD", "OK", "GOOD"]
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
    "fd871ec6-d953-430d-a354-f13c66fa8bc9",
    "dcedb196-2c60-4c29-a66d-0e768cfd698a",
    "0cf00a53-fd33-4887-bb38-e0bbb04e3f3e",
    "d95c1dae-1e22-4fb4-9cdc-743e96d0dddc",
    "8cd09fe9-c119-4ccd-b651-0f18334dbbe4",
    "7147995c-8e68-4106-ab24-f0a7673eb5f5",
    "c1c5b3c9-6178-4d67-a7e3-0285c2bf98ef"
]

time_in_seconds_attributes = [
    "attr-assurance-reliability",
]

percentage_attributes = [
    "attr-assurance-availability",
    "attr-reputation-provider-business-stability",
    "55a60ec3-55f7-48db-83bc-be2875c5210c"
]


def get_attr_data_type(attribute):
    data = {}
    print("get type for " + attribute)
    if attribute in linguistic_low_attributes:
        data["type"] = 1
        data["values"] = linguistic_low_choices
    elif attribute in linguistic_very_low_attributes:
        data["type"] = 1
        data["values"] = linguistic_low_choices
    elif attribute in linguistic_bad_attributes:
        data["type"] = 7
        data["values"] = linguistic_low_choices
    # elif attribute in boolean_attributes:
    #     data["type"] = 5
    #     data["values"] = boolean_choices
    else:
        data["type"] = 0  # all other cases
    print(data)
    return data
