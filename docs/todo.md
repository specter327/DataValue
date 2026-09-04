1. Agregar campo: required_fields, para la validacion de diccionarios en ComplexData
2. Agregar validaciones de tipos de datos. Para proteger ante casos como:
```python
isinstance(True, int) == True # ERROR
type(value) is int == False # PROTECCION
```
3. Robustecer la serializacion para asegurar que todo tipo de dato: byte, o semejante, sera codificado a Base64 por convenio de la libreria
4. ELIMINAR captura de datos por cualquier interfaz: Actualmente incluye una contaminacion de captura por CLI
5. Agregar scripts de prueba completos sobre conjuntos de datos exigentes
6. Adjuntar resultados textuales completos de validaciones
7. Adjuntar el enlace a la libreria PyPi actual publicada
8. Adjuntar instrucciones de instalacion, actualizacion, y desinstalacion simples y automatizadas mediante scripts
9. Mejorar navegacion de documentacion y presentacion
