# Library import
from typing import Type, Optional, Any, Iterable, Dict, Union
from .. import exceptions
from .primitive_data import PrimitiveData
import json

# Classes definition
class ComplexData:
    def __init__(self,
        data_type: Type[list] | Type[tuple] | Type[set] | Type[frozenset] | Type[dict],
        value: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        maximum_length: Optional[int] = None, minimum_length: Optional[int] = None,
        possible_values: Optional[Union[Iterable, Dict[Any, Any]]] = None,
        
        data_class: Optional[bool] = False
    ) -> None:
        # Instance properties assignment
        self.data_type = data_type
        self.value = value
        self.name = name
        self.description = description
        self.maximum_length = maximum_length; self.minimum_length = minimum_length
        self.possible_values = possible_values
        self.data_class = data_class

        # Validate constructor parameters
        if self.possible_values:
            # 1. Caso Diccionario (Mapping Schema)
            if self.data_type is dict and isinstance(self.possible_values, dict):
                pass # Es un esquema de mapeo válido

            # 2. Caso Colecciones (list/tuple)
            elif isinstance(self.possible_values, (list, tuple)):
                if self.data_type is dict:
                    if len(self.possible_values) not in (1, 2):
                        raise ValueError("Possible values for dict must be 1 (keys) or 2 (keys, values) list/tuples.")
                    if not isinstance(self.possible_values[0], (list, tuple)):
                        raise ValueError("The first element of possible_values for dict must be a list/tuple of keys.")
            else:
                raise ValueError(f"Possible values must be list/tuple or dict. Received: {type(self.possible_values).__name__}")
        

        # Execute instance data validation
        if not self.data_class:
            self.validate()
    
    # Private methods
    def _is_match(self, element: Any, schema: Any) -> bool:
        # Validate data types
        if isinstance(schema, (PrimitiveData, ComplexData)):
            try:
                return schema.validate(element)
            except:
                return False
        
        # Validate class data types
        if isinstance(schema, type):
            return isinstance(element, schema)
    
        # Validate literal values
        return element == schema
            
    def _validate_collection(self, data: Any) -> bool:
        element_index: int = 0
        for element in data:
            if not any(self._is_match(element, validator) for validator in self.possible_values):
                raise ValueError(f"[ComplexData] Element: {element}, on index: {element_index} is not allowed.")
            element_index += 1
        
        # Return results
        return True

    def _validate_dictionary(self, data: Any) -> bool:
        # ESCENARIO A: Schema Mapping (possible_values es un dict)
        if isinstance(self.possible_values, dict):
            for input_key, input_value in data.items():
                matched_rule = False
                for schema_key, value_validators in self.possible_values.items():
                    # Validamos si la clave de entrada coincide con la regla (soporta Regex o Tipos)
                    if self._is_match(input_key, schema_key):
                        matched_rule = True
                        
                        # Normalizamos validadores a lista para permitir múltiples opciones por clave
                        if not isinstance(value_validators, (list, tuple, set, frozenset)):
                            validators = [value_validators]
                        else:
                            validators = value_validators
                        
                        if not any(self._is_match(input_value, v) for v in validators):
                            raise ValueError(f"[ComplexData] Invalid value '{input_value}' for key '{input_key}'")
                        break # Match encontrado para esta clave, pasar a la siguiente
                
                if not matched_rule:
                    raise ValueError(f"[ComplexData] Key '{input_key}' is not allowed by schema mapping.")
            return True

        # ESCENARIO B: Validación Posicional/Tradicional
        if not isinstance(self.possible_values, (list, tuple)) or len(self.possible_values) != 2:
            keys_schema = self.possible_values
            values_schema = None
        else:
            keys_schema, values_schema = self.possible_values
        
        for key, value in data.items():
            if keys_schema:
                if not any(self._is_match(key, validator) for validator in keys_schema):
                    raise ValueError(f"[ComplexData] Invalid key: {key}")
            
            if values_schema:
                if not any(self._is_match(value, validator) for validator in values_schema):
                    raise ValueError(f"[ComplexData] Invalid value '{value}' for key '{key}'")

        return True

    @classmethod
    def _serialize_recursive(cls, element: Any) -> Any:
        # 1. Caso: Instancias de validadores propios
        if isinstance(element, (PrimitiveData, ComplexData)):
            return {
                "__type__": element.__class__.__name__,
                "content": element.to_dict()
            }
        
        # 2. Caso: Referencias a tipos de clase (int, str, etc.)
        if isinstance(element, type):
            return {"__class__": element.__name__}
        
        # 3. Caso: Colecciones estándar
        if isinstance(element, (list, tuple, set, frozenset)):
            return [cls._serialize_recursive(i) for i in element]
        
        if isinstance(element, dict):
            new_dict = {}
            for k, v in element.items():
                # Serialización de clave: si es compleja, se convierte a JSON string
                # para mantener la validez del formato JSON.
                serialized_key = cls._serialize_recursive(k)
                if isinstance(serialized_key, (dict, list)):
                    import json
                    key_repr = json.dumps(serialized_key)
                else:
                    key_repr = str(serialized_key)
                
                new_dict[key_repr] = cls._serialize_recursive(v)
            return new_dict
        
        # 4. Caso: Literales
        return element

    @classmethod
    def _deserialize_recursive(cls, element: Any) -> Any:
        SAFE_TYPES = {
            "list": list, "tuple": tuple, "set": set, "frozenset": frozenset, 
            "dict": dict, "str": str, "int": int, "float": float, "bool": bool,
            "bytes": bytes, "bytearray": bytearray, "NoneType": type(None)
        }

        if isinstance(element, dict):
            # CASO A: Es un objeto serializado (PrimitiveData o ComplexData)
            if "__type__" in element:
                obj_type = element["__type__"]
                content = element["content"]
                if obj_type == "PrimitiveData":
                    return PrimitiveData.from_dict(content)
                elif obj_type == "ComplexData":
                    return cls.from_dict(content)
                raise ValueError(f"Unknown serialized object type: {obj_type}")

            # CASO B: Es una referencia a un tipo (__class__)
            if "__class__" in element:
                type_name = element["__class__"]
                if type_name in SAFE_TYPES:
                    return SAFE_TYPES[type_name]
                raise ValueError(f"Type '{type_name}' is not allowed or unknown.")

            # CASO C: Diccionario de datos (Reconstrucción de claves y valores)
            decoded_dict = {}
            for k, v in element.items():
                processed_key = k
                # Detectar si la clave es un objeto empaquetado en string
                if isinstance(k, str) and (k.startswith('{') or k.startswith('[')):
                    try:
                        import json
                        potential_obj = json.loads(k)
                        if isinstance(potential_obj, (dict, list)):
                            processed_key = cls._deserialize_recursive(potential_obj)
                    except:
                        pass # Si falla, se queda como string literal
                
                decoded_dict[processed_key] = cls._deserialize_recursive(v)
            return decoded_dict

        if isinstance(element, list):
            return [cls._deserialize_recursive(item) for item in element]
        
        return element

    # Public methods
    def to_dict(self) -> dict:
        return {
            "DATA_TYPE":self.data_type.__name__ if hasattr(self.data_type, '__name__') else str(self.data_type),
            "NAME":self.name,
            "DESCRIPTION":self.description,
            "VALUE":self._serialize_recursive(self.value),
            "MAXIMUM_LENGTH":self.maximum_length,
            "MINIMUM_LENGTH":self.minimum_length,
            "POSSIBLE_VALUES":self._serialize_recursive(self.possible_values) if self.possible_values is not None else None,
            "DATA_CLASS":self.data_class,
            "__type__":"ComplexData"
        }

    
    @classmethod
    def from_dict(cls, data: dict) -> 'ComplexData':
        # 1. Secure types mapping
        SAFE_TYPES = {
            "list": list, "tuple": tuple, "set": set, "frozenset": frozenset, 
            "dict": dict, "str": str, "int": int, "float": float, "bool": bool,
            "bytes": bytes, "bytearray": bytearray
        }

        # 3. Validación y Reconstrucción del Root
        # Recuperamos el tipo de dato principal
        raw_type = data.get("DATA_TYPE")
        data_type = SAFE_TYPES.get(raw_type)
        if not data_type:
            raise TypeError(f"Invalid root data type: {raw_type}")

        # Procesamos los possible_values con el motor recursivo
        raw_possible = data.get("POSSIBLE_VALUES")
        possible_values = cls._deserialize_recursive(raw_possible) if raw_possible is not None else None
        
        # Corrección de tipo para tuplas (JSON no tiene tuplas, devuelve listas)
        # Si su __init__ es estricto y requiere tupla para possible_values, convertimos aquí:
        if isinstance(possible_values, list) and data_type != dict:
             possible_values = tuple(possible_values)
        
        # Para dicts, mantenemos la lista de listas o convertimos según su preferencia estricta
        if isinstance(possible_values, list) and data_type == dict:
             # Opcional: convertir sub-listas a tuplas si su validador lo prefiere, 
             # aunque su validación actual acepta listas.
             pass

        return cls(
            data_type=data_type,
            name=data.get("NAME"),
            description=data.get("DESCRIPTION"),
            value=data.get("VALUE"), # Asumimos valor literal o serializable simple
            maximum_length=data.get("MAXIMUM_LENGTH"),
            minimum_length=data.get("MINIMUM_LENGTH"),
            possible_values=possible_values,
            data_class=data.get("DATA_CLASS", False)
        )

    
    @classmethod
    def from_json(cls, text_content: str) -> 'ComplexData':
        try:
            data = json.loads(text_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        return cls.from_dict(data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)
    
    def validate(self, data: Any = None) -> bool:
        # Determine objective data
        if data is None:
            objective_data = self.value
        else:
            objective_data = data

        # Data type validation
        if not isinstance(objective_data, self.data_type):
            raise exceptions.DataTypeException(
                f"Incorrect data type.\nExpected: {self.data_type.__name__} - Received: {type(objective_data).__name__}"
            )
    
        # Length validation
        current_length = len(objective_data)
        
        if self.minimum_length is not None and current_length < self.minimum_length:
            raise ValueError(f"Minimum length not reached: {current_length} < {self.minimum_length}")
    
        if self.maximum_length is not None and current_length > self.maximum_length:
            raise ValueError(f"Maximum length reached: {current_length} > {self.maximum_length}")
    
        # Content validation and recurse
        if self.possible_values:
            # Validate dictionaries
            if isinstance(objective_data, dict):
                self._validate_dictionary(objective_data)
            else:
                self._validate_collection(objective_data)
        
        # Return results
        return True

    def cli_capture(self, prompt_context: str = "") -> Any:
        """Punto de entrada para la hidratación de datos desde CLI."""
        if self.data_type is dict:
            return self._cli_capture_mapping(prompt_context)
        return self._cli_capture_collection(prompt_context)

    def _get_user_selection(self, options: list, prompt_context: str, label: str = "Selección") -> Any:
        """
        Garantiza una selección válida de índice. 
        Maneja entradas vacías, no numéricas y fuera de rango.
        """
        while True:
            raw_input = input(f"{prompt_context}        > {label}: ").strip()
            
            if not raw_input:
                print(f"{prompt_context}        [!] Error: La entrada no puede estar vacía.")
                continue
            
            if not raw_input.isdigit():
                print(f"{prompt_context}        [!] Error: Ingrese un número entero válido.")
                continue
            
            idx = int(raw_input)
            if 0 <= idx < len(options):
                return options[idx]
            
            print(f"{prompt_context}        [!] Error: Índice fuera de rango (0-{len(options)-1}).")

    def _cli_capture_collection(self, prompt_context: str) -> list:
        results = []
        print(f"\n{prompt_context}[*] Iniciando colección: {self.name or 'Lista'}")
        
        while True:
            # Control de cardinalidad mínima
            if self.minimum_length is None or len(results) >= self.minimum_length:
                op = input(f"{prompt_context}    [?] ¿Añadir elemento a {self.name}? [s/N]: ").strip().lower()
                if op != 's':
                    break

            # Selección de esquema para el nuevo elemento
            options = list(self.possible_values)
            if len(options) == 1:
                selected_schema = options[0]
            else:
                print(f"{prompt_context}    [+] Tipos disponibles:")
                for i, schema in enumerate(options):
                    name = getattr(schema, 'name', f"Opción {i}")
                    print(f"{prompt_context}        {i}) {name}")
                selected_schema = self._get_user_selection(options, prompt_context)

            # Captura recursiva
            if hasattr(selected_schema, 'cli_capture'):
                results.append(selected_schema.cli_capture(prompt_context + "    "))
            else:
                val = input(f"{prompt_context}    [>] Valor: ")
                results.append(val)
        
        self.value = self.data_type(results)
        return results

    def _cli_capture_mapping(self, prompt_context: str) -> dict:
        """Captura para esquemas de tipo diccionario (Mapping Schema)."""
        captured_dict = {}
        print(f"\n{prompt_context}[*] Configurando: {self.name or 'Objeto'}")
        
        # Iteramos sobre las claves definidas en possible_values (dict)
        for key, schemas in self.possible_values.items():
            # Si solo hay una opción, se captura o auto-asigna
            if isinstance(schemas, (list, tuple)) and len(schemas) > 1:
                print(f"{prompt_context}    [+] Opciones para '{key}':")
                for i, s in enumerate(schemas):
                    name = getattr(s, 'name', str(s))
                    print(f"{prompt_context}        {i}) {name}")
                selected = self._get_user_selection(list(schemas), prompt_context)
            else:
                selected = schemas[0] if isinstance(schemas, (list, tuple)) else schemas

            # Manejo de literales auto-asignados (ej: "INTERNET")
            if isinstance(selected, str) and not hasattr(selected, 'cli_capture'):
                print(f"{prompt_context}    [=] {key}: {selected} (Auto-asignado)")
                captured_dict[key] = selected
            else:
                captured_dict[key] = selected.cli_capture(prompt_context + "    ")

        self.value = captured_dict
        return captured_dict