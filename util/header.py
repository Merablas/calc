# load information for calc.py

import json

FILENAME = 'header.json'

header = {'name': 'Calc',
          'version': '1.0.3',
          'border': "-=================-",
          'extra' : "Type 'exit' to quit"} 

def save(fp):
    with open(fp, 'w') as f:
        json.dump(header, f)

def getHeader(fp):
    content = ''
    with open(fp, 'r') as f:
        content = json.load(f)

    string = f'{content["name"]} v{content["version"]}\n{content["border"]}\n{content["extra"]}'

    return string
