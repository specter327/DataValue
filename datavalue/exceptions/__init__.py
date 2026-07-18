# Classes definition
# Base exception
class DataValueException(Exception): pass

# Specific exceptions
class DataTypeException(DataValueException): pass
class LengthException(DataValueException): pass
class SizeException(DataValueException): pass
class PossibleValueException(DataValueException): pass
class RegularExpressionException(DataValueException): pass
