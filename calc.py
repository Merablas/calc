# calc-lang

# built-in modules
import math
import re

# modules in the /util/ package
from util import *

def matchOperation(string):
    'Match the string of an operation to the actual operation'
    # this is for matching things like '+' to the plus operation
    try:
        # first matching operations
        return list(filter(lambda x:x.name==string[:len(x.name)], util.flatten(ops.operations) + ops.brackets))[0]
    except IndexError:
        # if no matching operations found, throw syntax error
        raise SyntaxError('Unknown operation: ' + str(string))
    
def parseExpr(item):
    'Parse a single expression'
    item = util.removeSpaces(item)
    if (match := number.match(item)):
        # if it matches the number regular expression, classify as number
        num = match.string[match.start():match.end()]
        return {'type':'num', 'data':float(num)}, item[match.end():]
    if (match := matchOperation(item)):
        # if it matches an operation, clisify as operation
        return {'type':'op', 'data':match}, util.removeFromStart(item, match.name)

    raise SyntaxError('Invalid syntax: ' + str(item))

def parse(line):
    'Parse a whole line of code'
    data = []
    while len(line) > 0:
        datum, line = parseExpr(line)
        data.append(datum)

    return data
    
def nest(parsedData):
    'Change brackets into a list of operations and numbers'
    data = parsedData
    nestedData = []

    i = 0
    while i < len(data): #for i, expr in enumerate(data):
        subExpr = data[i]
        if subExpr['type'] == 'op' and subExpr['data'] == ops.openbracket:
            # this variable is for counting the bracket pair    
            bracketPairs = 1

            end = i # position of the endbracket that closes the original openbracket
            while bracketPairs > 0:
                end += 1
                if data[end]['type'] == 'op' and data[end]['data'] == ops.openbracket:
                    # add 1 to bracketPairs if it's antoher openbracket
                    bracketPairs += 1 
                elif data[end]['type'] == 'op' and data[end]['data'] == ops.closebracket:
                    # subtract 1 if it's a closebracket
                    bracketPairs -= 1

            # find the data in the brackets
            subExpr = data[i+1: end]
            # nest that data, to support brackets inside brackets
            subExpr = nest(subExpr)

            # remove the whole bracket pair from the original data
            del data[i: end + 1]
            
            # move order back by 1, since the expression after needs to be processed
            i -= 1
            
        elif subExpr['type'] == 'op' and subExpr['data'] == ops.closebracket:
            # all closebrackets are supposed to be deleted, if this one is found, that means there are extras
            raise SyntaxError("Unmatched ')'")

        nestedData.append(subExpr)
        i += 1

    return nestedData

def bidmas(nestedData):
    'Apply the order of operation (BIDMAS) and convert into Parsed OPerations'
    data = nestedData[:]
    orderedData = data[0]
    
    for opList in ops.operations:
        # the ops.operations are  stuctured in the way that powers go first, then mul/div, etc.
        i = 0
        while i < len(data):
            expr = data[i]

            if type(expr['data']) == Var: # variable handling
                try:
                    if data[i+1]['type'] != 'num':
                        data.insert(i+1, {'type':'num', 'data':expr['data'].default2})
                except IndexError:
                    data.insert(i+1, {'type':'num', 'data':expr['data'].default2})

            if type(expr) == list:
                # if it's nested, set the brackets to the (bidmas of itself)
                data[i] = bidmas(expr)
                orderedData = data[i]
                i += 1
                continue
            
            if expr['data'] in opList:
                # get the arguments (before and after) of the operation
                defaultUsed = False                            
                j = 1
                
                try:
                    if i == 0: # python supports iterable[-1] so if that happens, use default
                        raise IndexError

                    j = 1 # continue until a number is found
                    while data[i + j]['type'] not in ['num', 'pop']:
                        j += 1
                    args = data[i - 1], bidmas(data[i + 1: i + j + 1]) # then the data would be re-bidmas-ed
                    
                    if args[0]['type'] not in ['num', 'pop']: # in order to use defaults
                        raise IndexError
                    pop = {'type':'pop', 'data':ParsedOperation(expr['data'], *args)}
                except IndexError:
                    defaultUsed = True
                    
                    j = 1 # continue until a number is found
                    while data[i + j]['type'] not in ['num', 'pop']:
                        j += 1
                    args = {'type':'num', 'data':data[i]['data'].default}, bidmas(data[i + 1: i + j + 1]) # then the data would be re-bidmas-ed
                    pop = {'type':'pop', 'data':ParsedOperation(expr['data'], *args)}


                # replace the arguents and operation with the 'ParsedOperation' object
                if defaultUsed:
                    del data[i:i+j+1]
                else:
                    del data[i-1 : i+j+1]
                if defaultUsed:
                    data.insert(i, pop)
                else:
                    data.insert(i-1, pop) 
                i -= 1

                # set orderedData to the ParsedOPeration (POP)
                orderedData = pop

            i += 1

    print(data)
    return orderedData

def evaluate(orderedData):
    'Get an answer from the expression made with the bidmas function'
    if type(orderedData) == list:
        # if it's a list, evaluate the list
        return evaluate(orderedData[0])
    if orderedData['type'] == 'num':
        # if it's a single number, return the number's value
        return orderedData['data']

    # otherwise.get the ParsedOperation object
    orderedData = orderedData['data']

    newArgs = []
    for arg in orderedData.args:
        # evaluate each of the arguments
        newArgs.append(evaluate(arg))

    # return the action of each of the argumets e.g. +(1, 1)
    return orderedData.operation.action(*newArgs)


def run(line):
    'Return the whole proess of parsing, nesting, applying bidmas, and evaluation'
    parsed = parse(line)
    try:
        nested = nest(parsed)
    except IndexError:
        # an extra '(' raises an IndexError
        raise SyntaxError("Unmatched '('")

    try:
        ordered = bidmas(nested)
    except IndexError:
        ordered = {'type':'num', 'data':None}

    result = evaluate(ordered)
        
    return result


def main():
    try:
        print('\n' + getHeader(FILENAME))
    except FileNotFoundError:
        save(FILENAME)
        print('\n' + getHeader(FILENAME))
    print()
        
    while True:
        line = input('> ')
        if line.startswith('exit'):
            print('Goodbye')
            break
        try:
            result = run(line)
            if not type(result) in [int, float, complex]:
                continue
            if result % 1 == 0:
                result = int(result)
            
            print(result)
        except Exception as e:
            print('Error:', e)
            #raise e

if __name__ == '__main__':
    main()


