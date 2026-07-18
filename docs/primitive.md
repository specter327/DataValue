# PrimitiveData

Esta clase representa a un dato de tipo simple/primitivo. Entre los tipos de datos soportados, se encuentran: ```int```, ```str```, ```bool```, ```float```, ```None```, ```bytes```, ```bytearray```

Presenta los siguientes parametros:
- **data_type**: especifica el tipo de dato. Posibles valores:
  - ```int```
  - ```str```
  - ```bool```
  - ```float```
  - ```NoneType```
  - ```bytes```
  - ```bytearray```

  Si el valor no es del tipo de dato especificado, genera una excepcion
- **minimum_length**: especifica el tamaño minimo del valor. Se puede ver como la cantidad de caracteres/digitos

  Se comporta de la siguiente manera (segun el tipo de dato):
  - ```str```/```bytes```: especifica la cantidad minima de caracteres
  -  ```bool```/```None```: no aplica
  -  ```int```/```float```: especifica la cantidad de digitos minima (numerico)
    
  Si no cumple con el tamaño minimo, se genera una excepcion.
  > Se puede especificar: ```None```, si no aplica
- **maximum_length**: especifica el tamaño maximo del valor. Se puede ver como la cantidad de caracteres/digitos

  Se comporta de la siguiente manera (segun el tipo de dato):
  - ```str```/```bytes```: especifica la cantidad maxima de caracteres
  - ```bool```/```None```: no aplica
  - ```int```/```float```: especifica la cantidad de digitos maxima (numerico)
    
  Si no cumple con el tamaño maximo, se genera una excepcion. 
  
  > Se puede especificar: ```None```, si no aplica
- **minimum_size**: especifica la cantidad minima de valor. Se puede ver como la magnitud escalar.

  Se comporta de la siguiente manera (segun el tipo de dato):
  - ```str```/```bytes```: no aplica
  - ```bool```/```None```: no aplica
  - ```int```/```float```: especifica el valor numerico minimo
    
  Si no cumple con el valor minimo, se genera una excepcion. 
  > Se puede especificar: ```None```, si no aplica
- **maximum_size**: especifica la cantidad maxima de valor. Se puede ver como la magnitud escalar.

  Se comporta de la siguiente manera (segun el tipo de dato):
  - ```str```/```bytes```: no aplica
  - ```bool```/```None```: no aplica
  - ```int```/```float```: especifica el valor numerico maximo
    
  Si no cumple con el valor maximo, se genera una excepcion.

  > Se puede especificar: ```None```, si no aplica
- **possible_values**: especifica un conjunto de valores posibles para el dato.
  Si el valor no se encuentra entre las opciones, se genera una excepcion.
  
  Para el tipo de dato  ```bool``` (**data_type**), las opciones posibles siempre se aplicaran y seran: ```True```/```False```
  > Se puede especificar ```None``` si no aplica.
  
- **regular_expression**: especifica una expresion regular que sera validada en el valor entregado.

  Se comporta segun el tipo de dato:
  - ```str```/```bytes```: se valida directamente
  - ```bool```/```None```: no aplica
  - ```int```/```float```: no aplica

    > Se puede especificar: ```None```, si no aplica
- **value**: especifica el valor con el que se construira el dato. Sobre el se aplicaran las validaciones anteriormente descriptas
- **data_class**: especifica si la definicion de esta instancia sera utilizada para validar un valor como tipo de dato, o como plantilla para la validacion de valores

> Por defecto es ```False```; se validara el dato con el cual es creada la instancia

## Ejemplos de uso
### Ejemplo 1

Validacion de numero telefonico
> Se valida el numero telefonico bajo el estandar internacional E.164 UIT-T: https://es.wikipedia.org/wiki/E.164
```python

phone_number = PrimitiveData(
  data_type=str,
  value="+34600111222",
  minimum_length=7, # Minimo de 7 caracteres
  maximum_length=15, # Maximo de 15 caracteres
  minimum_size=None, # No se valida el numero minimo
  maximum_size=None, # No se valida el numero maximo,
  possible_values=None, # No se especifica posibles valores obligatorios
  regular_expression=r"^\+[1-9]\d{6,14}$"
)
```
### Ejemplo 2

Validacion de numero de puerto de conexion

```python
connection_port = PrimitiveData(
  data_type=int,
  value=45321,
  minimum_length=1, # Cantidad de digitos minima
  maximum_length=5, # Cantidad de digitos maxima
  minimum_size=1, # Valor numerico minimo
  maximum_size=65535, # Valor numerico maximo
  possible_values=None, # Posibles opciones
  regular_expression=None # Expresion regular aplicada
)
```
### Ejemplo 3

Validacion de protocolo de transporte de datos

```python
transport_protocol = PrimitiveData(
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

### Ejemplo 4

Validacion de direccion IPv4

> Se valida la direccion IP bajo el estandar definido en el RFC 791 de la IETF: https://datatracker.ietf.org/doc/html/rfc791

```python
ip_address = PrimitiveData(
  data_type=str,
  value="192.168.0.1",
  maximum_length=15,
  minimum_length=7,
  maximum_size=None, minimum_size=None,
  possible_values=None,
  regular_expression=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)
```