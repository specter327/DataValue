# Presentacion

**DataValue** es una libreria de Python ligera pero potente para la especificacion de datos estrictos usando valores simples.


# Instalacion

Para instalar la libreria unicamente ejecuta en un terminal:

```bash
$ pip install datavalue
```

## Objetivos

El objetivo de esta libreria es implementar una forma basica y especifica para la descripcion de datos, y su validacion estricta. Ya que en mas de una ocasion, se validan criterios como:

- Tipo de dato:
  - Simple (primitivo): ```int```, ```str```, ```bool```, ```float```, ```None```, ```bytes```
  - Compuesto (complejo): ```list```, ```dict```, ```tuple```, ```range```
- Tamaño:
  - Minimo: ```int``` / ```float```
  - Maximo: ```int``` / ```float```
- Posibles valores: ```None``` / ```list``` / ```tuple```
- Patron: ```regex```

Implementando interfaces de serializacion, y deserializacion para la presentacion, y transporte.

## Uso

Para utilizar la libreria, se deben importar las clases definidas:
```
python

from datavalue import *
```
> Lease mas en la documentacion de cada clase.

## Utilidades

Permite especificar el dato deseado, describiendo las caracteristicas que el valor proporcionado debe cumplir, para:
- Funciones/metodos
- Objetos
- Parametros/Retorno
- Entrada de datos
- Transporte de datos: serializacion/deserializacion

Para la validacion de datos de ingreso, y normalizacion de datos de egreso.

## Dependencias

La libreria no cuenta con ninguna dependencia. Es 100% instalable y utilizable de forma directa.
