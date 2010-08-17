'''
Contains the exceptions that may be raised by the scipysim library.
'''

class InvalidSimulationInput(TypeError):
    pass

class NoProcessFunctionDefined(NotImplementedError):
    pass
