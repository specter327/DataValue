# Library import
import re
from typing import Type, Optional, Any, Iterable, Union
from .. import exceptions
import json
import base64

# Classes definition
class PrimitiveData:
    def __init__(self,
        data_type: Type,
        value: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        maximum_length: Optional[int] = None, minimum_length: Optional[int] = None,
        maximum_size: Optional[Union[int, float]] = None, minimum_size: Optional[Union[int, float]] = None,
        possible_values: Optional[Iterable] = None,
        regular_expression: Optional[str] = None,
        
        data_class: Optional[bool] = False
    ) -> None:
        # Instance properties assignment
        self.data_type = data_type
        self.value = value
        self.name = name
        self.description = description
        self.maximum_length = maximum_length; self.minimum_length = minimum_length
        self.maximum_size = maximum_size; self.minimum_size = minimum_size
        self.possible_values = possible_values
        self.regular_expression = regular_expression
        self.data_class = data_class
        
        if not self.data_class:
            self.validate()
    
    # Private methods
    def _is_match(self, element: Any, schema: Any) -> bool:        
        if isinstance(schema, PrimitiveData):
            try:
                # Si el validador hijo no lanza excepción, el match es exitoso
                return schema.validate(element)
            except (exceptions.DataValueException, ValueError, TypeError):
                return False
        
        # 2. Caso: El esquema es un tipo de dato (clase como str, int)
        if isinstance(schema, type):
            return isinstance(element, schema)
    
        # 3. Caso: El esquema es un valor literal
        return element == schema

    def __get_length(self, data: Optional[Any] = None) -> Optional[int]:
        if data is None:
            data_objective = self.value
        else:
            data_objective = data

        if isinstance(data_objective, (str, bytes, bytearray)):
            return len(data_objective)
        elif isinstance(data_objective, (int, float)):
            return len([digit for digit in str(data_objective) if digit.isdigit()])
        else:
            return None
    
    # Public methods
    def to_dict(self) -> dict:
        normalized_possible = None
        if self.possible_values is not None:
            normalized_possible = []
            for item in self.possible_values:
                if isinstance(item, PrimitiveData):
                    normalized_possible.append(item.to_dict())
                elif isinstance(item, type):
                    normalized_possible.append({"__class__": item.__name__})
                else:
                    normalized_possible.append(item)
        
        # Process raw data
        if isinstance(self.value, (bytes, bytearray)):
            raw_value = base64.b64encode(self.value).decode("UTF-8")
        else:
            raw_value = self.value

        data_structure = {
            "DATA_TYPE": self.data_type.__name__ if hasattr(self.data_type, '__name__') else str(self.data_type),
            "VALUE": raw_value,
            "NAME":self.name,
            "DESCRIPTION":self.description,
            "MAXIMUM_LENGTH": self.maximum_length,
            "MINIMUM_LENGTH": self.minimum_length,
            "MAXIMUM_SIZE": self.maximum_size,
            "MINIMUM_SIZE": self.minimum_size,
            "POSSIBLE_VALUES": normalized_possible,
            "REGULAR_EXPRESSION": self.regular_expression,
            "DATA_CLASS": self.data_class,
            "__type__": "PrimitiveData"
        }

        return data_structure
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PrimitiveData':
        expected_keys = {
            "DATA_TYPE", "VALUE", "NAME", "DESCRIPTION", "MAXIMUM_LENGTH", "MINIMUM_LENGTH",
            "MAXIMUM_SIZE", "MINIMUM_SIZE", "POSSIBLE_VALUES",
            "REGULAR_EXPRESSION", "DATA_CLASS", "__type__"
        }
        
        unknown_keys = set(data.keys()) - expected_keys
        if unknown_keys:
            raise ValueError(f"Unknown keys in data structure: {unknown_keys}")

        # Secure type mapping
        type_mapping = {
            "str": str, "int": int, "float": float, "bool": bool,
            "bytes": bytes, "bytearray": bytearray, "NoneType": type(None)
        }

        type_str = data.get("DATA_TYPE")
        real_type = type_mapping.get(type_str)

        if real_type is None and type_str != "None":
             raise TypeError(f"Unsupported or unsafe data type: {type_str}")

        value = data.get("VALUE")
        if real_type in (bytes, bytearray) and isinstance(value, str):
            value = base64.b64decode(value.encode("UTF-8"))

            if real_type is bytearray:
                value = bytearray(value)
        
        # --- NORMALIZACIÓN DE POSSIBLE_VALUES (DESERIALIZACIÓN) ---
        raw_possible = data.get("POSSIBLE_VALUES")
        possible_values = None
        if raw_possible is not None:
            possible_values = []
            for item in raw_possible:
                if isinstance(item, dict):
                    if item.get("__type__") == "PrimitiveData":
                        possible_values.append(cls.from_dict(item))
                    elif "__class__" in item:
                        possible_values.append(type_mapping.get(item["__class__"]))
                    else:
                        possible_values.append(item)
                else:
                    possible_values.append(item)
        # ----------------------------------------------------------

        return cls(
            data_type=real_type,
            value=value,
            name=data.get("NAME"),
            description=data.get("DESCRIPTION"),
            maximum_length=data.get("MAXIMUM_LENGTH"),
            minimum_length=data.get("MINIMUM_LENGTH"),
            maximum_size=data.get("MAXIMUM_SIZE"),
            minimum_size=data.get("MINIMUM_SIZE"),
            possible_values=possible_values,
            regular_expression=data.get("REGULAR_EXPRESSION"),
            data_class=data.get("DATA_CLASS", False)
        )
        
    @classmethod
    def from_json(cls, text_content: str) -> 'PrimitiveData':
        try:
            data_table = json.loads(text_content)
        except json.JSONDecodeError as Error:
            raise ValueError(f"Invalid JSON format: {Error}")
            
        return cls.from_dict(data_table)

    def validate(self, data: Optional[Any] = None) -> bool:
        # Define the data to validate
        if data is None:
            data_objective = self.value
        else:
            data_objective = data

        # Validacion de tipo de dato
        if not isinstance(data_objective, self.data_type):
            raise exceptions.DataTypeException(
                f"Incorrect data type.\nExpected: {self.data_type.__name__} - Received: {type(data_objective).__name__}"
            )
        
        # Validacion de longitud de caracteres (minimo, y maximo)
        if self.minimum_length is not None or self.maximum_length is not None:
            length = self.__get_length(data_objective)
            
            if length is not None:
                if self.minimum_length is not None and length < self.minimum_length:
                    raise exceptions.LengthException(f"Character/digit length below the minimum: {length} < {self.minimum_length}")
                elif self.maximum_length is not None and length > self.maximum_length:
                    raise exceptions.LengthException(f"Character/digit length above the maximum: {length} > {self.maximum_length}")
        
        # Validacion de tamaño (magnitud)
        if self.minimum_size is not None or self.maximum_size is not None:
            if isinstance(data_objective, (int, float)):
                if self.minimum_size is not None and data_objective < self.minimum_size:
                    raise exceptions.SizeException(f"Numerical value below the minimum: {data_objective} < {self.minimum_size}")
                if self.maximum_size is not None and data_objective > self.maximum_size:
                    raise exceptions.SizeException(f"Numerical value above the maximum: {data_objective} > {self.maximum_size}")
        
        # Validacion de posibles valores (conjunto)
        if self.data_type is bool:
            if data_objective not in (True, False):
                raise exceptions.PossibleValueException(
                    f"The boolean value has to be True or False: {data_objective} != True/False"
                )
        
        if self.possible_values is not None:
            # Implementación de any() con _is_match para soportar la composición de tipos
            if not any(self._is_match(data_objective, validator) for validator in self.possible_values):
                raise exceptions.PossibleValueException(
                    f"Value '{data_objective}' is not allowed by any of the provided validators."
                )
        
        # Validacion de expresion regular
        if self.regular_expression is not None:
            if isinstance(data_objective, (str, bytes, bytearray)):
                # Soporte para bytes/bytearray convirtiendo el patrón si es necesario
                pattern = self.regular_expression
                if isinstance(data_objective, (bytes, bytearray)) and isinstance(pattern, str):
                    pattern = pattern.encode()
                
                if not re.fullmatch(pattern, data_objective):
                    raise exceptions.RegularExpressionException(f"The value does not meet the required pattern: {self.regular_expression}")
        
        return True


    def cli_capture(self, prompt_context: str = "") -> Any:
        label = self.name if self.name else f"Data ({self.data_type.__name__})"
        print(f"{prompt_context}[*] Inserting value for: {label}")
        if self.description:
            print(f"{prompt_context}    (Info: {self.description})")

        while True:
            raw_in = input(f"{prompt_context}[>] Value: ").strip()
            try:
                if self.data_type is bool:
                    val_casted = raw_in.lower() in ('true', '1', 't', 'y', 'yes', 's', 'si')
                elif self.data_type in (bytes, bytearray):
                    val_casted = self.data_type(raw_in.encode('utf-8'))
                else:
                    val_casted = self.data_type(raw_in)

                self.validate(val_casted)
                self.value = val_casted
                return val_casted
            except Exception as e:
                print(f"{prompt_context}[!] Invalid: {str(e)}")