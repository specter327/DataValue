"""Regression and feature tests for DataValue positional validation.

Run without external test frameworks:

    python3 -m unittest -v test_datavalue_positional.py
"""

import json
import unittest

from datavalue import ComplexData, PrimitiveData, ValidationMode
from datavalue import exceptions


def primitive(data_type, name=None, **constraints):
    return PrimitiveData(
        data_type=data_type,
        value=None,
        name=name,
        data_class=True,
        **constraints,
    )


class LegacyCompatibilityTests(unittest.TestCase):
    def test_default_mode_is_any(self):
        schema = ComplexData(
            data_type=list,
            value=None,
            possible_values=(str, int),
            data_class=True,
        )

        self.assertIs(schema.validation_mode, ValidationMode.ANY)
        self.assertTrue(schema.validate(["a", 1, 2, "b"]))
        self.assertTrue(schema.validate([1, "a"]))

    def test_legacy_collection_rejects_unknown_type(self):
        schema = ComplexData(
            data_type=list,
            value=None,
            possible_values=(str, int),
            data_class=True,
        )

        with self.assertRaises(ValueError):
            schema.validate(["a", 1, False, 2.5])

    def test_legacy_dictionary_key_value_schema(self):
        schema = ComplexData(
            data_type=dict,
            value=None,
            possible_values=([str], [str, int]),
            data_class=True,
        )

        self.assertTrue(
            schema.validate({"name": "Specter", "level": 100})
        )

        with self.assertRaises(ValueError):
            schema.validate({"ratio": 1.5})

    def test_old_serialized_schema_defaults_to_any(self):
        old_document = {
            "DATA_TYPE": "list",
            "NAME": "legacy",
            "DESCRIPTION": None,
            "VALUE": None,
            "MAXIMUM_LENGTH": None,
            "MINIMUM_LENGTH": None,
            "POSSIBLE_VALUES": [
                {"__class__": "str"},
                {"__class__": "int"},
            ],
            "DATA_CLASS": True,
            "__type__": "ComplexData",
        }

        restored = ComplexData.from_dict(old_document)

        self.assertIs(restored.validation_mode, ValidationMode.ANY)
        self.assertTrue(restored.validate([1, "one", 2, "two"]))


class PositionalValidationTests(unittest.TestCase):
    def setUp(self):
        self.name = primitive(
            str,
            "name",
            minimum_length=1,
            maximum_length=50,
        )
        self.age = primitive(
            int,
            "age",
            minimum_size=0,
            maximum_size=150,
        )
        self.active = primitive(bool, "active")

        self.schema = ComplexData(
            data_type=list,
            value=None,
            name="user_parameters",
            possible_values=(self.name, self.age, self.active),
            data_class=True,
            validation_mode="positional",
        )

    def test_accepts_correct_order(self):
        self.assertTrue(self.schema.validate(["Specter", 25, True]))

    def test_rejects_swapped_values(self):
        with self.assertRaises(
            exceptions.PositionalValueException
        ) as captured:
            self.schema.validate([25, "Specter", True])

        self.assertEqual(captured.exception.index, 0)
        self.assertEqual(captured.exception.value, 25)
        self.assertIs(captured.exception.schema, self.name)

    def test_rejects_missing_value(self):
        with self.assertRaises(
            exceptions.PositionalLengthException
        ) as captured:
            self.schema.validate(["Specter", 25])

        self.assertEqual(captured.exception.expected, 3)
        self.assertEqual(captured.exception.received, 2)

    def test_rejects_additional_value(self):
        with self.assertRaises(exceptions.PositionalLengthException):
            self.schema.validate(["Specter", 25, True, "unexpected"])

    def test_applies_nested_primitive_constraints(self):
        with self.assertRaises(exceptions.PositionalValueException):
            self.schema.validate(["Specter", 200, True])

    def test_accepts_tuple_contract(self):
        schema = ComplexData(
            data_type=tuple,
            value=None,
            possible_values=(str, int, bool),
            data_class=True,
            validation_mode=ValidationMode.POSITIONAL,
        )

        self.assertTrue(schema.validate(("hello", 10, False)))

    def test_literal_position(self):
        schema = ComplexData(
            data_type=list,
            value=None,
            possible_values=("CONTROL", int),
            data_class=True,
            validation_mode="positional",
        )

        self.assertTrue(schema.validate(["CONTROL", 100]))

        with self.assertRaises(exceptions.PositionalValueException):
            schema.validate(["DATA", 100])

    def test_empty_contract_accepts_only_empty_collection(self):
        schema = ComplexData(
            data_type=list,
            value=None,
            possible_values=(),
            data_class=True,
            validation_mode="positional",
        )

        self.assertTrue(schema.validate([]))

        with self.assertRaises(exceptions.PositionalLengthException):
            schema.validate(["unexpected"])

    def test_rejects_unordered_collection_types(self):
        for data_type in (set, frozenset, dict):
            with self.subTest(data_type=data_type):
                with self.assertRaises(
                    exceptions.ValidationModeException
                ):
                    ComplexData(
                        data_type=data_type,
                        value=None,
                        possible_values=(),
                        data_class=True,
                        validation_mode="positional",
                    )

    def test_rejects_unknown_mode(self):
        with self.assertRaises(exceptions.ValidationModeException):
            ComplexData(
                data_type=list,
                value=None,
                possible_values=(),
                data_class=True,
                validation_mode="unknown",
            )

    def test_requires_possible_values(self):
        with self.assertRaises(ValueError):
            ComplexData(
                data_type=list,
                value=None,
                possible_values=None,
                data_class=True,
                validation_mode="positional",
            )


class NestedSchemaTests(unittest.TestCase):
    def test_demanding_nested_contract(self):
        protocol = primitive(
            str,
            "protocol",
            possible_values=("TCP", "UDP"),
        )
        address = primitive(
            str,
            "address",
            regular_expression=r"^[a-z0-9.-]+$",
        )
        port = primitive(
            int,
            "port",
            minimum_size=1,
            maximum_size=65535,
        )
        metadata = ComplexData(
            data_type=dict,
            value=None,
            name="metadata",
            possible_values=([str], [str, int, bool]),
            data_class=True,
        )

        endpoint = ComplexData(
            data_type=list,
            value=None,
            possible_values=(protocol, address, port, metadata),
            data_class=True,
            validation_mode="positional",
        )

        value = [
            "TCP",
            "manager.openshell.local",
            443,
            {
                "priority": 100,
                "persistent": True,
                "source": "OSAM",
            },
        ]

        self.assertTrue(endpoint.validate(value))

        with self.assertRaises(exceptions.PositionalValueException):
            endpoint.validate([
                "TCP",
                "manager.openshell.local",
                70000,
                value[3],
            ])


class SerializationTests(unittest.TestCase):
    def setUp(self):
        self.schema = ComplexData(
            data_type=list,
            value=None,
            name="call_signature",
            possible_values=(
                primitive(str, "name", minimum_length=1),
                primitive(int, "count", minimum_size=1),
                ComplexData(
                    data_type=dict,
                    value=None,
                    name="options",
                    possible_values=([str], [str, int, bool]),
                    data_class=True,
                ),
            ),
            data_class=True,
            validation_mode=ValidationMode.POSITIONAL,
        )

    def test_to_dict_includes_mode(self):
        document = self.schema.to_dict()
        self.assertEqual(document["VALIDATION_MODE"], "positional")

    def test_json_round_trip_preserves_mode_and_nested_schemas(self):
        encoded = self.schema.to_json()
        restored = ComplexData.from_json(encoded)

        self.assertIs(restored.validation_mode, ValidationMode.POSITIONAL)
        self.assertEqual(restored.name, "call_signature")
        self.assertEqual(len(restored.possible_values), 3)
        self.assertIsInstance(restored.possible_values[0], PrimitiveData)
        self.assertIsInstance(restored.possible_values[2], ComplexData)
        self.assertTrue(
            restored.validate([
                "Specter",
                3,
                {
                    "transport": "TCP",
                    "priority": 100,
                    "secure": True,
                },
            ])
        )

    def test_stored_tuple_value_round_trip(self):
        schema = ComplexData(
            data_type=tuple,
            value=("TCP", 443),
            possible_values=(str, int),
            validation_mode="positional",
        )

        restored = ComplexData.from_json(schema.to_json())

        self.assertEqual(restored.value, ("TCP", 443))
        self.assertTrue(restored.validate())

    def test_document_is_valid_json(self):
        decoded = json.loads(self.schema.to_json())
        self.assertEqual(decoded["VALIDATION_MODE"], "positional")


if __name__ == "__main__":
    unittest.main(verbosity=2)