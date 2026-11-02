# Caso de uso: 1 - Validacion de lista de valores aceptados
Construccion de validador:
```python
values_validation = datavalue.ComplexData(
  data_type=list,
  value=["A", "B", "D"],
  possible_values=["A", "B", "D", "C"]
)
```

Resultado:
![[Pasted image 20261029022230.png]]

# Caso de uso: 2 - Validacion de perfil de usuario
Construccion de validador:
```python
user_profile_validator = datavalue.ComplexData(
  data_type=dict,
  value={
    "USERNAME":"Specter",
    "PASSWORD":"Password123",
    "AGE":19,
  },
  maximum_length=None, minimum_length=None,
  possible_values=([str], [str, int])
)
```

Resultado:

![[Pasted image 20261029022425.png]]

# Caso de uso: 3 - Validacion de red
Construccion de validadores:
```python
IPv4 = PrimitiveData(data_type=str, value=None, name="IPv4", regular_expression=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", data_class=True)

Port = PrimitiveData(data_type=int, value=None, name="Port", minimum_size=1, maximum_size=65535, data_class=True)

MAC  = PrimitiveData(data_type=str, value=None, name="MAC", regular_expression=r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", data_class=True)

Path = PrimitiveData(data_type=str, value=None, name="SerialPath", regular_expression=r"^/dev/tty[A-Z0-9]+$", data_class=True)

# Validacion estructural
InternetAddr = ComplexData(data_type=dict, value=None, name="IP_Endpoint", possible_values={
    "ADDRESS": [IPv4], 
    "PORT": [Port]
}, data_class=True)

BluetoothAddr = ComplexData(data_type=dict, value=None, name="BT_Endpoint", possible_values={
    "ADDRESS": [MAC], 
    "PORT": [PrimitiveData(data_type=int, value=None, minimum_size=1, maximum_size=30, data_class=True)]
}, data_class=True)

# Perfil de direccion
ProfileSchema = ComplexData(data_type=dict, value=None, name="Profile", possible_values={
    "TRANSPORT": ["INTERNET", "BLUETOOTH", "SERIAL"],
    "ADDRESSES": ComplexData(data_type=list, value=None, possible_values=[InternetAddr, BluetoothAddr], data_class=True)
}, data_class=True)
```

Resultado:

![[Pasted image 20261029023721.png]]

Validacion de datos erroneos:
![[Pasted image 20261029023836.png]]