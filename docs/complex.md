# ComplexData

Esta clase representa a un dato de tipo complejo/compuesto. Entre los tipos de datos soportados, se encuentran: ```list```, ```tuple```, ```set```, ```frozenset```, ```dict```

Presenta los siguientes parametros:
- **data_type**: especifica el tipo de dato. Posibles valores:
  - ```list```
  - ```tuple```
  - ```set```
  - ```frozenset```
  - ```dict```

  Si el valor no es del tipo de dato especificado, genera una excepcion
- **minimum_length**: especifica la cantidad minima de elementos dentro del conjunto

  Se comporta de la siguiente manera (segun el tipo de dato):
  - ```list```/```tuple```/```set```/```frozenset```: especifica la cantidad minima de elementos 
  - ```dict```: especifica la cantidad minima de claves

  Si no cumple con el tamaño minimo, se genera una excepcion.
  > Se puede especificar: ```None```, si no aplica
- **maximum_length**: especifica la cantidad maxima de elementos dentro del conjunto

  Se comporta de la siguiente manera (segun el tipo de dato):
  - ```list```/```tuple```/```set```/```frozenset```: especifica la cantidad maxima de elementos 
  - ```dict```: especifica la cantidad maxima de claves
- **possible_values**: especifica un conjunto de valores posibles para el conjunto de datos
  Si el valor no se encuentra entre las opciones, se genera una excepcion

  Se comporta de la siguiente manera (segun el tipo de dato):
  - ```list```/```tuple```/```set```/```frozenset```: especifica los valores posibles dentro del conjunto
  - ```dict```: puede ser una lista de valores posibles; en cuyo caso se aplicara la validacion **unicamente** a las claves. O, se puede especificar una lista con dos sublistas "[[], []]"; en cuyo caso la primera lista (izquierda) se usara para validar las claves, y la segunda lista (derecha) se usara para validar los valores de cada clave

  > Se pueden especificar otras instancias (configuradas) de objetos PrimitiveData o ComplexData, en cuyo caso cada valor tratara de ser validado tambien con dichas clases. Esto permite validacion recursiva
- **value**: especifica el valor con el que se construira el dato. Sobre el se aplicaran las validaciones anteriormente descriptas
- **data_class**: especifica si la definicion de esta instancia sera utilizada para validar un valor como tipo de dato, o como plantilla para la validacion de valores

  > Por defecto es ```False```; se validara el dato con el cual es creada la instancia

## Ejemplos de uso
### Ejemplo 1

Validacion de lista de valores permitidos (validacion de entrada de datos)

```python
values_validation = ComplexData(
  data_type=list,
  value=["A", "B", "D"],
  possible_values=["A", "B", "D", "C"]
)
```

### Ejemplo 2

Validacion de lista de direcciones IPv4 e IPv6

> Se valida la direccion IPv4 bajo el estandar definido en el RFC 791 de la IETF: https://datatracker.ietf.org/doc/html/rfc791. Se valida la direccion IPv6 bajo el estandar definido en el RFC 4291 de la IETF: https://datatracker.ietf.org/doc/html/rfc4291

```python
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
```

### Ejemplo 3

Validacion de perfil de usuario

```python
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
```

### Ejemplo 4

Validacion de numeros telefonicos

> Se valida el numero telefonico bajo el estandar internacional E.164 UIT-T: https://es.wikipedia.org/wiki/E.164

```python
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
```