"""ComplexData with optional positional collection validation."""

from __future__ import annotations

import json

from enum import Enum
from typing import Any, Dict, Iterable, Optional, Type, Union

from .. import exceptions
from .primitive_data import PrimitiveData


class ValidationMode(str, Enum):
    """How collection elements are matched against ``possible_values``."""

    ANY = "any"
    POSITIONAL = "positional"


class ComplexData:
    """Description and strict validation of compound Python values.

    ``validation_mode='any'`` preserves the historical behavior: every
    collection element may match any validator from ``possible_values``.

    ``validation_mode='positional'`` is available for ``list`` and ``tuple``:
    every value must match the validator located at the same index and the
    collection length must exactly match the schema length.
    """

    def __init__(
        self,
        data_type: (
            Type[list]
            | Type[tuple]
            | Type[set]
            | Type[frozenset]
            | Type[dict]
        ),
        value: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        maximum_length: Optional[int] = None,
        minimum_length: Optional[int] = None,
        possible_values: Optional[
            Union[Iterable, Dict[Any, Any]]
        ] = None,
        data_class: Optional[bool] = False,
        validation_mode: ValidationMode | str = ValidationMode.ANY,
    ) -> None:
        # Keep every historical constructor argument in its original position.
        # validation_mode is appended so positional callers remain compatible.
        self.data_type = data_type
        self.value = value
        self.name = name
        self.description = description
        self.maximum_length = maximum_length
        self.minimum_length = minimum_length
        self.possible_values = possible_values
        self.data_class = data_class

        try:
            self.validation_mode = ValidationMode(validation_mode)
        except ValueError as error:
            allowed = ", ".join(mode.value for mode in ValidationMode)
            raise exceptions.ValidationModeException(
                f"Unknown validation mode: {validation_mode!r}. "
                f"Allowed modes: {allowed}."
            ) from error

        self._validate_constructor()

        if not self.data_class:
            self.validate()

    # =========================================================
    # CONSTRUCTOR VALIDATION
    # =========================================================

    def _validate_constructor(self) -> None:
        supported_types = (list, tuple, set, frozenset, dict)

        if self.data_type not in supported_types:
            raise TypeError(
                "ComplexData data_type must be list, tuple, set, "
                f"frozenset or dict. Received: {self.data_type!r}."
            )

        if (
            self.validation_mode is ValidationMode.POSITIONAL
            and self.data_type not in (list, tuple)
        ):
            raise exceptions.ValidationModeException(
                "Positional validation is only supported for list and tuple."
            )

        if self.validation_mode is ValidationMode.POSITIONAL:
            if self.possible_values is None:
                raise ValueError(
                    "Positional validation requires possible_values. "
                    "Use an empty tuple for a zero-length contract."
                )

            if not isinstance(self.possible_values, (list, tuple)):
                raise ValueError(
                    "Positional possible_values must be list or tuple. "
                    f"Received: {type(self.possible_values).__name__}."
                )

            return

        # Historical constructor validation for mode="any".
        if self.possible_values:
            if self.data_type is dict and isinstance(
                self.possible_values,
                dict,
            ):
                return

            if isinstance(self.possible_values, (list, tuple)):
                if self.data_type is dict:
                    if len(self.possible_values) not in (1, 2):
                        raise ValueError(
                            "Possible values for dict must be 1 (keys) "
                            "or 2 (keys, values) list/tuples."
                        )

                    if not isinstance(
                        self.possible_values[0],
                        (list, tuple),
                    ):
                        raise ValueError(
                            "The first element of possible_values for dict "
                            "must be a list/tuple of keys."
                        )

                return

            raise ValueError(
                "Possible values must be list/tuple or dict. "
                f"Received: {type(self.possible_values).__name__}."
            )

    # =========================================================
    # MATCHING
    # =========================================================

    def _is_match(self, element: Any, schema: Any) -> bool:
        if isinstance(schema, (PrimitiveData, ComplexData)):
            try:
                return schema.validate(element)
            except (
                exceptions.DataValueException,
                ValueError,
                TypeError,
            ):
                return False

        if isinstance(schema, type):
            return isinstance(element, schema)

        return element == schema

    def _validate_collection(self, data: Any) -> bool:
        """Historical unordered/alternative matching behavior."""

        for index, element in enumerate(data):
            if not any(
                self._is_match(element, validator)
                for validator in self.possible_values
            ):
                raise ValueError(
                    f"[ComplexData] Element: {element}, on index: "
                    f"{index} is not allowed."
                )

        return True

    def _validate_positional_collection(self, data: Any) -> bool:
        schemas = self.possible_values

        if len(data) != len(schemas):
            raise exceptions.PositionalLengthException(
                expected=len(schemas),
                received=len(data),
            )

        for index, (element, schema) in enumerate(zip(data, schemas)):
            if not self._is_match(element, schema):
                raise exceptions.PositionalValueException(
                    index=index,
                    value=element,
                    schema=schema,
                )

        return True

    def _validate_dictionary(self, data: Any) -> bool:
        # Scenario A: mapping schema.
        if isinstance(self.possible_values, dict):
            for input_key, input_value in data.items():
                matched_rule = False

                for schema_key, value_validators in (
                    self.possible_values.items()
                ):
                    if self._is_match(input_key, schema_key):
                        matched_rule = True

                        if not isinstance(
                            value_validators,
                            (list, tuple, set, frozenset),
                        ):
                            validators = [value_validators]
                        else:
                            validators = value_validators

                        if not any(
                            self._is_match(input_value, validator)
                            for validator in validators
                        ):
                            raise ValueError(
                                "[ComplexData] Invalid value "
                                f"'{input_value}' for key '{input_key}'"
                            )

                        break

                if not matched_rule:
                    raise ValueError(
                        f"[ComplexData] Key '{input_key}' is not allowed "
                        "by schema mapping."
                    )

            return True

        # Scenario B: historical key/value schema.
        if (
            not isinstance(self.possible_values, (list, tuple))
            or len(self.possible_values) != 2
        ):
            keys_schema = self.possible_values
            values_schema = None
        else:
            keys_schema, values_schema = self.possible_values

        for key, value in data.items():
            if keys_schema:
                if not any(
                    self._is_match(key, validator)
                    for validator in keys_schema
                ):
                    raise ValueError(f"[ComplexData] Invalid key: {key}")

            if values_schema:
                if not any(
                    self._is_match(value, validator)
                    for validator in values_schema
                ):
                    raise ValueError(
                        f"[ComplexData] Invalid value '{value}' "
                        f"for key '{key}'"
                    )

        return True

    # =========================================================
    # SERIALIZATION
    # =========================================================

    @classmethod
    def _serialize_recursive(cls, element: Any) -> Any:
        if isinstance(element, (PrimitiveData, ComplexData)):
            return {
                "__type__": element.__class__.__name__,
                "content": element.to_dict(),
            }

        if isinstance(element, type):
            return {"__class__": element.__name__}

        if isinstance(element, (list, tuple, set, frozenset)):
            return [cls._serialize_recursive(item) for item in element]

        if isinstance(element, dict):
            serialized_dictionary = {}

            for key, value in element.items():
                serialized_key = cls._serialize_recursive(key)

                if isinstance(serialized_key, (dict, list)):
                    key_representation = json.dumps(serialized_key)
                else:
                    key_representation = str(serialized_key)

                serialized_dictionary[key_representation] = (
                    cls._serialize_recursive(value)
                )

            return serialized_dictionary

        return element

    @classmethod
    def _deserialize_recursive(cls, element: Any) -> Any:
        safe_types = {
            "list": list,
            "tuple": tuple,
            "set": set,
            "frozenset": frozenset,
            "dict": dict,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "bytes": bytes,
            "bytearray": bytearray,
            "NoneType": type(None),
        }

        if isinstance(element, dict):
            if "__type__" in element:
                object_type = element["__type__"]
                content = element["content"]

                if object_type == "PrimitiveData":
                    return PrimitiveData.from_dict(content)

                if object_type == "ComplexData":
                    return cls.from_dict(content)

                raise ValueError(
                    f"Unknown serialized object type: {object_type}"
                )

            if "__class__" in element:
                type_name = element["__class__"]

                if type_name in safe_types:
                    return safe_types[type_name]

                raise ValueError(
                    f"Type '{type_name}' is not allowed or unknown."
                )

            decoded_dictionary = {}

            for key, value in element.items():
                processed_key = key

                if isinstance(key, str) and (
                    key.startswith("{") or key.startswith("[")
                ):
                    try:
                        possible_object = json.loads(key)

                        if isinstance(possible_object, (dict, list)):
                            processed_key = cls._deserialize_recursive(
                                possible_object
                            )
                    except (
                        json.JSONDecodeError,
                        TypeError,
                        ValueError,
                    ):
                        pass

                decoded_dictionary[processed_key] = (
                    cls._deserialize_recursive(value)
                )

            return decoded_dictionary

        if isinstance(element, list):
            return [cls._deserialize_recursive(item) for item in element]

        return element

    def to_dict(self) -> dict:
        return {
            "DATA_TYPE": (
                self.data_type.__name__
                if hasattr(self.data_type, "__name__")
                else str(self.data_type)
            ),
            "NAME": self.name,
            "DESCRIPTION": self.description,
            "VALUE": self._serialize_recursive(self.value),
            "MAXIMUM_LENGTH": self.maximum_length,
            "MINIMUM_LENGTH": self.minimum_length,
            "POSSIBLE_VALUES": (
                self._serialize_recursive(self.possible_values)
                if self.possible_values is not None
                else None
            ),
            "DATA_CLASS": self.data_class,
            "VALIDATION_MODE": self.validation_mode.value,
            "__type__": "ComplexData",
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ComplexData":
        safe_types = {
            "list": list,
            "tuple": tuple,
            "set": set,
            "frozenset": frozenset,
            "dict": dict,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "bytes": bytes,
            "bytearray": bytearray,
        }

        raw_type = data.get("DATA_TYPE")
        data_type = safe_types.get(raw_type)

        if data_type is None:
            raise TypeError(f"Invalid root data type: {raw_type}")

        raw_possible = data.get("POSSIBLE_VALUES")
        possible_values = (
            cls._deserialize_recursive(raw_possible)
            if raw_possible is not None
            else None
        )

        # JSON has no tuple. Preserve the historical reconstruction behavior.
        if isinstance(possible_values, list) and data_type is not dict:
            possible_values = tuple(possible_values)

        value = cls._deserialize_recursive(data.get("VALUE"))

        # Restore the declared root collection after JSON decoding when safe.
        if value is not None and data_type in (
            tuple,
            set,
            frozenset,
        ):
            value = data_type(value)

        return cls(
            data_type=data_type,
            name=data.get("NAME"),
            description=data.get("DESCRIPTION"),
            value=value,
            maximum_length=data.get("MAXIMUM_LENGTH"),
            minimum_length=data.get("MINIMUM_LENGTH"),
            possible_values=possible_values,
            data_class=data.get("DATA_CLASS", False),
            validation_mode=data.get(
                "VALIDATION_MODE",
                ValidationMode.ANY.value,
            ),
        )

    @classmethod
    def from_json(cls, text_content: str) -> "ComplexData":
        try:
            data = json.loads(text_content)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON: {error}") from error

        return cls.from_dict(data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    # =========================================================
    # VALIDATION
    # =========================================================

    def validate(self, data: Any = None) -> bool:
        # None retains the original meaning: validate the stored value.
        objective_data = self.value if data is None else data

        if not isinstance(objective_data, self.data_type):
            raise exceptions.DataTypeException(
                "Incorrect data type.\n"
                f"Expected: {self.data_type.__name__} - "
                f"Received: {type(objective_data).__name__}"
            )

        current_length = len(objective_data)

        if (
            self.minimum_length is not None
            and current_length < self.minimum_length
        ):
            raise exceptions.LengthException(
                "Minimum length not reached: "
                f"{current_length} < {self.minimum_length}"
            )

        if (
            self.maximum_length is not None
            and current_length > self.maximum_length
        ):
            raise exceptions.LengthException(
                "Maximum length exceeded: "
                f"{current_length} > {self.maximum_length}"
            )

        if self.validation_mode is ValidationMode.POSITIONAL:
            self._validate_positional_collection(objective_data)
        elif self.possible_values:
            if isinstance(objective_data, dict):
                self._validate_dictionary(objective_data)
            else:
                self._validate_collection(objective_data)

        return True

    # =========================================================
    # CLI CAPTURE
    # =========================================================

    def cli_capture(self, prompt_context: str = "") -> Any:
        if self.validation_mode is ValidationMode.POSITIONAL:
            return self._cli_capture_positional(prompt_context)

        if self.data_type is dict:
            return self._cli_capture_mapping(prompt_context)

        return self._cli_capture_collection(prompt_context)

    def _get_user_selection(
        self,
        options: list,
        prompt_context: str,
        label: str = "Selection",
    ) -> Any:
        while True:
            raw_input = input(
                f"{prompt_context}        > {label}: "
            ).strip()

            if not raw_input:
                print(
                    f"{prompt_context}        [!] Error: "
                    "input cannot be empty."
                )
                continue

            if not raw_input.isdigit():
                print(
                    f"{prompt_context}        [!] Error: "
                    "enter a valid integer."
                )
                continue

            index = int(raw_input)

            if 0 <= index < len(options):
                return options[index]

            print(
                f"{prompt_context}        [!] Error: index outside "
                f"range (0-{len(options) - 1})."
            )

    @staticmethod
    def _capture_type(data_type: type, raw_value: str) -> Any:
        if data_type is bool:
            normalized = raw_value.strip().lower()

            if normalized in ("true", "1", "t", "y", "yes", "s", "si"):
                return True

            if normalized in ("false", "0", "f", "n", "no"):
                return False

            raise ValueError(f"Invalid boolean: {raw_value!r}")

        if data_type in (bytes, bytearray):
            return data_type(raw_value.encode("utf-8"))

        return data_type(raw_value)

    def _cli_capture_positional(self, prompt_context: str) -> Any:
        results = []

        print(
            f"\n{prompt_context}[*] Configuring positional collection: "
            f"{self.name or 'Collection'}"
        )

        for index, schema in enumerate(self.possible_values):
            schema_name = getattr(schema, "name", None)

            print(
                f"{prompt_context}    [{index}] "
                f"{schema_name or 'Unnamed position'}"
            )

            if hasattr(schema, "cli_capture"):
                value = schema.cli_capture(prompt_context + "    ")
            elif isinstance(schema, type):
                raw_value = input(
                    f"{prompt_context}    [>] Value ({schema.__name__}): "
                )
                value = self._capture_type(schema, raw_value)
            else:
                print(
                    f"{prompt_context}    [=] Fixed value: {schema!r}"
                )
                value = schema

            results.append(value)

        self.value = self.data_type(results)
        self.validate(self.value)
        return self.value

    def _cli_capture_collection(self, prompt_context: str) -> list:
        results = []

        print(
            f"\n{prompt_context}[*] Starting collection: "
            f"{self.name or 'List'}"
        )

        while True:
            if self.minimum_length is None or len(results) >= (
                self.minimum_length
            ):
                operation = input(
                    f"{prompt_context}    [?] Add element to "
                    f"{self.name}? [y/N]: "
                ).strip().lower()

                if operation not in ("y", "yes", "s", "si"):
                    break

            options = list(self.possible_values)

            if len(options) == 1:
                selected_schema = options[0]
            else:
                print(f"{prompt_context}    [+] Available types:")

                for index, schema in enumerate(options):
                    name = getattr(schema, "name", f"Option {index}")
                    print(f"{prompt_context}        {index}) {name}")

                selected_schema = self._get_user_selection(
                    options,
                    prompt_context,
                )

            if hasattr(selected_schema, "cli_capture"):
                results.append(
                    selected_schema.cli_capture(prompt_context + "    ")
                )
            elif isinstance(selected_schema, type):
                raw_value = input(f"{prompt_context}    [>] Value: ")
                results.append(
                    self._capture_type(selected_schema, raw_value)
                )
            else:
                results.append(selected_schema)

        self.value = self.data_type(results)
        return self.value

    def _cli_capture_mapping(self, prompt_context: str) -> dict:
        captured_dictionary = {}

        print(
            f"\n{prompt_context}[*] Configuring: "
            f"{self.name or 'Object'}"
        )

        for key, schemas in self.possible_values.items():
            if isinstance(schemas, (list, tuple)) and len(schemas) > 1:
                print(f"{prompt_context}    [+] Options for '{key}':")

                for index, schema in enumerate(schemas):
                    name = getattr(schema, "name", str(schema))
                    print(f"{prompt_context}        {index}) {name}")

                selected = self._get_user_selection(
                    list(schemas),
                    prompt_context,
                )
            else:
                selected = (
                    schemas[0]
                    if isinstance(schemas, (list, tuple))
                    else schemas
                )

            if isinstance(selected, str) and not hasattr(
                selected,
                "cli_capture",
            ):
                print(
                    f"{prompt_context}    [=] {key}: "
                    f"{selected} (Auto-assigned)"
                )
                captured_dictionary[key] = selected
            elif hasattr(selected, "cli_capture"):
                captured_dictionary[key] = selected.cli_capture(
                    prompt_context + "    "
                )
            elif isinstance(selected, type):
                raw_value = input(
                    f"{prompt_context}    [>] {key} ({selected.__name__}): "
                )
                captured_dictionary[key] = self._capture_type(
                    selected,
                    raw_value,
                )
            else:
                captured_dictionary[key] = selected

        self.value = captured_dictionary
        return captured_dictionary