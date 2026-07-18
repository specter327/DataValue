"""Demanding examples for DataValue positional validation."""

from datavalue import ComplexData, PrimitiveData, ValidationMode


def primitive(
    data_type,
    name,
    **constraints,
):
    return PrimitiveData(
        data_type=data_type,
        value=None,
        name=name,
        data_class=True,
        **constraints,
    )


# =========================================================
# EXAMPLE 1: SCIC FUNCTION CONTRACT
# =========================================================


manager_filepath = primitive(
    str,
    "manager_filepath",
    description="Public Manager profile path.",
    minimum_length=1,
    maximum_length=4096,
    regular_expression=r"^.+\.public\.json$",
)

overwrite = primitive(
    bool,
    "overwrite",
    description="Replace an existing imported profile.",
)

timeout = primitive(
    int,
    "timeout",
    description="Operation timeout in seconds.",
    minimum_size=1,
    maximum_size=300,
)

import_manager_parameters = ComplexData(
    data_type=list,
    value=None,
    name="import_manager_parameters",
    description="Ordered arguments for import_manager().",
    possible_values=(
        manager_filepath,
        overwrite,
        timeout,
    ),
    data_class=True,
    validation_mode=ValidationMode.POSITIONAL,
)


valid_arguments = [
    "./profiles/manager.public.json",
    False,
    30,
]

assert import_manager_parameters.validate(valid_arguments)


# =========================================================
# EXAMPLE 2: NETWORK ENDPOINT WITH NESTED METADATA
# =========================================================


protocol = primitive(
    str,
    "protocol",
    possible_values=("TCP", "UDP"),
)

ip_address = primitive(
    str,
    "ip_address",
    regular_expression=(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    ),
)

port = primitive(
    int,
    "port",
    minimum_size=1,
    maximum_size=65535,
)

tls_enabled = primitive(
    bool,
    "tls_enabled",
)

metadata = ComplexData(
    data_type=dict,
    value=None,
    name="metadata",
    possible_values=(
        [str],
        [str, int, bool],
    ),
    data_class=True,
)

endpoint = ComplexData(
    data_type=tuple,
    value=None,
    name="endpoint",
    possible_values=(
        protocol,
        ip_address,
        port,
        tls_enabled,
        metadata,
    ),
    data_class=True,
    validation_mode="positional",
)

assert endpoint.validate(
    (
        "TCP",
        "192.168.1.25",
        443,
        True,
        {
            "source": "OSAM",
            "priority": 100,
            "persistent": True,
        },
    )
)


# =========================================================
# EXAMPLE 3: NESTED FUNCTION RESULTS
# =========================================================


manager_uid = primitive(
    str,
    "uid",
    regular_expression=r"^[a-zA-Z0-9-]{3,64}$",
)

manager_name = primitive(
    str,
    "name",
    minimum_length=1,
    maximum_length=100,
)

role = primitive(
    str,
    "role",
    possible_values=(
        "administrator",
        "operator",
        "auditor",
    ),
)

roles = ComplexData(
    data_type=list,
    value=None,
    name="roles",
    minimum_length=1,
    possible_values=(role,),
    data_class=True,
)

manager_profile = ComplexData(
    data_type=dict,
    value=None,
    name="manager",
    possible_values={
        "uid": manager_uid,
        "name": manager_name,
        "roles": roles,
    },
    data_class=True,
)

created = primitive(bool, "created")

import_manager_results = ComplexData(
    data_type=list,
    value=None,
    name="import_manager_results",
    possible_values=(
        manager_profile,
        created,
    ),
    data_class=True,
    validation_mode="positional",
)

results = [
    {
        "uid": "manager-001",
        "name": "Primary Manager",
        "roles": [
            "administrator",
            "auditor",
        ],
    },
    True,
]

assert import_manager_results.validate(results)


# =========================================================
# SERIALIZATION
# =========================================================


serialized = import_manager_results.to_json()
restored = ComplexData.from_json(serialized)

assert restored.validation_mode is ValidationMode.POSITIONAL
assert restored.validate(results)


print("All demanding DataValue examples passed.")