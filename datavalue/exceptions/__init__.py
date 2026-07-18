"""DataValue exception hierarchy."""


class DataValueException(Exception):
    pass


class DataTypeException(DataValueException):
    pass


class LengthException(DataValueException):
    pass


class SizeException(DataValueException):
    pass


class PossibleValueException(DataValueException):
    pass


class RegularExpressionException(DataValueException):
    pass


class ValidationModeException(DataValueException):
    pass


class PositionalLengthException(LengthException):
    def __init__(self, expected: int, received: int):
        self.expected = expected
        self.received = received

        super().__init__(
            "Incorrect positional length. "
            f"Expected: {expected} - Received: {received}"
        )


class PositionalValueException(PossibleValueException):
    def __init__(self, index: int, value, schema):
        self.index = index
        self.value = value
        self.schema = schema

        schema_name = getattr(schema, "name", None)
        schema_type = getattr(schema, "data_type", None)

        if schema_name:
            schema_description = schema_name
        elif schema_type is not None:
            schema_description = getattr(
                schema_type,
                "__name__",
                repr(schema_type),
            )
        elif isinstance(schema, type):
            schema_description = schema.__name__
        else:
            schema_description = repr(schema)

        super().__init__(
            "Invalid positional value. "
            f"Index: {index} - Schema: {schema_description} - "
            f"Value: {value!r}"
        )