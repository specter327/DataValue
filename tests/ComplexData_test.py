# Library import
from datavalue import ComplexData, PrimitiveData

# Execute validations
print("="*5)
print("Validating list of allowed values...")
values_validation = ComplexData(
  data_type=list,
  value=["A", "B", "D"],
  possible_values=["A", "B", "D", "C"]
)
print("Values:", values_validation.value)
values_validation.validate()
print("Validation completed successfully")

print("="*5)
print("Validating list of IPv4 and IPv6 addresses...")
# IPv4 schema definition
ipv4_schema = PrimitiveData(
  data_type=str,
  value=None,
  maximum_length=15, minimum_length=7,
  maximum_size=None, minimum_size=None,
  possible_values=None,
  regular_expression=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",

  data_class=True
)

# IPv6 schema definition
ipv6_schema = PrimitiveData(
  data_type=str,
  value=None,
  maximum_length=39, minimum_length=2,
  maximum_size=None, minimum_size=None,
  possible_values=None,
  regular_expression=r'^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:))$',

  data_class=True
)

ip_address_set = ComplexData(
  data_type=list,
  value=["192.168.0.1", "::1"],
  maximum_length=None, minimum_length=None,
  possible_values=(ipv4_schema, ipv6_schema)
)

print("Values:", ip_address_set.value)
print("Allowed values:")
for schema in ip_address_set.possible_values:
    print(schema.to_json())
ip_address_set.validate()
print("Validation completed successfully")

print("="*5)
print("Validating user profile table...")
user_profile_validator = ComplexData(
  data_type=dict,
  value={
    "USERNAME":"Specter",
    "PASSWORD":"Password123",
    "AGE":19,
  },
  maximum_length=None, minimum_length=None,
  possible_values=([str], [str, int])
)

print("Values:", user_profile_validator.value)

print("Allowed values:")
for schema in user_profile_validator.possible_values:
    print(schema)

user_profile_validator.validate()
print("Validation completed successfully")

print("="*5)
print("Validating phone numbers set...")
# Phone number schema definition
phone_number_schema = PrimitiveData(
  data_type=str,
  value=None,
  minimum_length=7, maximum_length=15,
  minimum_size=None, maximum_size=None,
  possible_values=None,
  regular_expression=r"^\+[1-9]\d{6,14}$",
  
  data_class=True
)

# Set of phone numbers definition
phone_numbers_set = ComplexData(
  data_type=list,
  value=["+521240769928", "+79273463798", "+499896239706"],
  maximum_length=None, minimum_length=None,
  possible_values=(phone_number_schema, )
)

print("Values:", phone_numbers_set.value)
print("Allowed values:")
for schema in phone_numbers_set.possible_values:
    print(schema.to_json())

phone_numbers_set.validate()

print("Validation completed successfully")

def test_mapping_architecture():
    print("--- [TEST] INICIANDO VALIDACIÓN DE ARQUITECTURA DE COMUNICACIONES ---")

    # ============================================================================
    # 1. DEFINICIÓN DE ESQUEMAS (DATA CLASSES)
    # ============================================================================
    
    # Primitivos con Regex para Networking
    IPv4 = PrimitiveData(data_type=str, value=None, name="IPv4", regular_expression=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", data_class=True)
    Port = PrimitiveData(data_type=int, value=None, name="Port", minimum_size=1, maximum_size=65535, data_class=True)
    MAC  = PrimitiveData(data_type=str, value=None, name="MAC", regular_expression=r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", data_class=True)
    Path = PrimitiveData(data_type=str, value=None, name="SerialPath", regular_expression=r"^/dev/tty[A-Z0-9]+$", data_class=True)

    # Esquemas de Endpoint (Mapping Schema)
    # Aquí la clave es un literal 'string' y el valor es una lista de validadores permitidos
    InternetAddr = ComplexData(data_type=dict, value=None, name="IP_Endpoint", possible_values={
        "ADDRESS": [IPv4], 
        "PORT": [Port]
    }, data_class=True)

    BluetoothAddr = ComplexData(data_type=dict, value=None, name="BT_Endpoint", possible_values={
        "ADDRESS": [MAC], 
        "PORT": [PrimitiveData(data_type=int, value=None, minimum_size=1, maximum_size=30, data_class=True)]
    }, data_class=True)

    # Esquema de Perfil (Anidamiento Complejo)
    # Nota: Usamos una lista de validadores para 'ADDRESSES'
    ProfileSchema = ComplexData(data_type=dict, value=None, name="Profile", possible_values={
        "TRANSPORT": ["INTERNET", "BLUETOOTH", "SERIAL"],
        "ADDRESSES": ComplexData(data_type=list, value=None, possible_values=[InternetAddr, BluetoothAddr], data_class=True)
    }, data_class=True)

    # ============================================================================
    # 2. CASO DE PRUEBA: PAYLOAD VÁLIDO
    # ============================================================================
    valid_payload = {
        "TRANSPORT": "INTERNET",
        "ADDRESSES": [
            {"ADDRESS": "192.168.1.50", "PORT": 8080},
            {"ADDRESS": "10.0.0.1", "PORT": 443}
        ]
    }

    print("[*] Probando payload válido...")
    try:
        ProfileSchema.validate(valid_payload)
        print("[OK] Payload validado exitosamente.")
    except Exception as e:
        print(f"[FAIL] Error inesperado en validación: {e}")
        return

    # ============================================================================
    # 3. PRUEBA DE SERIALIZACIÓN (ROUND-TRIP)
    # ============================================================================
    print("[*] Probando ciclo de serialización/deserialización del esquema...")
    try:
        # Serializamos el validador completo (la estructura del esquema)
        schema_json = ProfileSchema.to_json()
        
        # Reconstruimos el validador desde el JSON
        reconstructed_schema = ComplexData.from_json(schema_json)
        
        # Validamos el payload original con el esquema reconstruido
        reconstructed_schema.validate(valid_payload)
        print("[OK] Ciclo de vida del esquema (JSON) completado.")
    except Exception as e:
        print(f"[FAIL] Error en persistencia: {e}")
        return

    # ============================================================================
    # 4. CASO DE PRUEBA: PAYLOAD INVÁLIDO (VIOLACIÓN DE SEGURIDAD)
    # ============================================================================
    invalid_payload = {
        "TRANSPORT": "INTERNET",
        "ADDRESSES": [
            {"ADDRESS": "999.999.999.999", "PORT": 80}, # IP Inválida
            {"KEY_INTRUSION": "DANGER"}                 # Clave no permitida por Mapping
        ]
    }

    print("[*] Probando detección de payload inválido...")
    try:
        ProfileSchema.validate(invalid_payload)
        print("[FAIL] El validador permitió un payload corrupto.")
    except ValueError as e:
        print(f"[OK] Detección correcta: {e}")

    print("\n--- [RESULTADO] TODAS LAS PRUEBAS DE MAPEO PASARON ---")

test_mapping_architecture()