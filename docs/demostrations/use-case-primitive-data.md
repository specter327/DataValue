# Caso de uso: 1 - Numeros telefonicos

Validacion de numeros telefonicos
Construccion de validador:
```python
phone_number = datavalue.PrimitiveData(
  data_type=str,
  value="+34600111222",
  minimum_length=7, # Minimum character length
  maximum_length=15, # Maximum character length
  minimum_size=None, # Not validate the minimum number
  maximum_size=None, # Not validate the maximum number,
  possible_values=None, # Not specify obligatory possible values
  regular_expression=r"^\+[1-9]\d{6,14}$"
)
```

Resultado:
![[Pasted image 20261029020829.png]]

# Caso de uso: 2 - Validacion de puerto y transporte
Construccion de validador:
```python
connection_port = datavalue.PrimitiveData(
  data_type=int,
  value=45321,
  minimum_length=1, # Maximum digits
  maximum_length=5, # Minimum digits
  minimum_size=1, # Minimum numerical value
  maximum_size=65535, # Maximum numerical value
  possible_values=None, # Possible options
  regular_expression=None # Regular expression applied
)
```

Resultado:

![[Pasted image 20261029021431.png]]

# Caso de uso: 3 - Validacion de protocolo de transporte
Construccion de validador:
```python
transport_protocol = datavalue.PrimitiveData(
  data_type=str,
  value="TCP",
  maximum_length=None,
  minimum_length=None,
  minimum_size=None,
  maximum_size=None,
  possible_values=("TCP", "UDP"),
  regular_expression=None
)
```

Resultado:

![[Pasted image 20261029021545.png]]

# Caso de uso: 4 - Validacion de direccion IPv4
Construccion de validador:
```python
ip_address = datavalue.PrimitiveData(
  data_type=str,
  value="192.168.0.1",
  maximum_length=15,
  minimum_length=7,
  maximum_size=None, minimum_size=None,
  possible_values=None,
  regular_expression=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)
```

Resultado:

![[Pasted image 20261029021739.png]]
