# built-in operations for calculator

import re
import math

# the regular expression of a number
number = re.compile('^(\d+\.?\d*|\d*\.\d+)(e[+-]?\d+)?',re.IGNORECASE)

class State:
    degrees = False

    @classmethod
    def switchMode(cls, _, y):
        if y == 0:
            cls.degrees = False
        elif y == 1:
            cls.degrees = True

class Operation:
    'Basic class for arithmetic'
    def __init__(self, name, action, default=None):
        self.name = name
        self.default = default

        self.action = action

        if action == None:
            action = lambda val: val

        # string and representation are for debugging purposes

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

class ParsedOperation:
    'Class for operations, with arguments'
    def __init__(self, operation, *args):
        self.operation = operation
        self.args = [*args]

        # string and representation are for debugging purposes

    def __str__(self):
        return self.operation.name + f'{[*self.args]}'

    def __repr__(self):
        return str(self)

class Var(Operation):
    def __init__(self, name, value):
        self.value = value
        self.default2 = 1
        super().__init__(name, lambda x, y: x * value * y, 1)

class ops:
    plus     = Operation('+', lambda x, y:x+y,0)
    minus    = Operation('-', lambda x, y:x-y,0)
    multiply = Operation('*', lambda x, y:x*y,1)
    divide   = Operation('/', lambda x, y:x/y,1)
    power    = Operation('^', lambda x, y:pow(x,y))

    sin = Operation('sin', lambda x, y: x * trig(y, math.sin), 1)
    cos = Operation('cos', lambda x, y: x * trig(y, math.cos), 1)
    tan = Operation('tan', lambda x, y: x * trig(y, math.tan), 1)

    asin = Operation('asin', lambda x, y: x * atrig(y, math.asin), 1)
    acos = Operation('acos', lambda x, y: x * atrig(y, math.acos), 1)
    atan = Operation('atan', lambda x, y: x * atrig(y, math.atan), 1)

    mode = Operation('mode', State.switchMode)

    pi = Var('pi', math.pi)

    openbracket  = Operation('(', None)
    closebracket = Operation(')', None)

    brackets = [openbracket, closebracket]
    operations = [[mode], [power], [pi], [sin, cos, tan, asin, acos, atan], [multiply, divide], [plus, minus]] # in bidmas form

def trig(x, func):
    if State.degrees:
        return func(math.radians(x))
    return func(x)

def atrig(x, func):
    if State.degrees:
        return math.degrees(func(x))
    return func(x)


class util:
    @staticmethod
    def removeSpaces(string):
        return re.sub(re.compile('\s+'), '', string)

    @staticmethod
    def removeFromStart(string, toRemove):
        length = len(toRemove)
        if string[:length] == toRemove:
            return string[length:]
        return string

    @staticmethod
    def flatten(lst):
        newList = []
        for e in lst:
            if type(e) == list:
                newList += util.flatten(e)
            else:
                newList.append(e)
        return newList
