import json
import jsonschema
import argparse
import random

def traverse(parent_name, data, depth):
    #if data == 'type':
        
    strThingToPrint = parent_name
    if isinstance(data, list):
        for child in range(0, len(data)):
            traverse(parent_name + '[' + str(child) + ']', data[child], depth + 1)
        return

    if isinstance(data, dict):
        for child in sorted(data.keys()):
            traverse(parent_name + '.' + child, data[child], depth + 1)
        return
    
    if isinstance(data, str):
        print(strThingToPrint + ': ' + data)
        return

def storeDefinitions(definition, key, definitionStorage):
    definitionStorage[key] = definition
    #print ('Adding ' + json.dumps(definition, indent = 2) + ' to definitions')

def immediateChildren(data, definitionStorage):
    # TODO: Consider modifying data to contain the definition storage.
    strType = ''
    if 'definitions' in data.keys():
        definitions = data['definitions']
        for definitionEntry in definitions.keys():
            key = '#/definitions/' + definitionEntry
            storeDefinitions(data['definitions'][definitionEntry], key, definitionStorage)
            
    if 'oneOf' in data.keys():
        possibleSchemas = data['oneOf']
        index = len(possibleSchemas) - 1
        if "index" in data.keys():
            index = immediateChildren(data['index'], definitionStorage)
            print('choosing schema ' + str(index))
        chosenSchema = possibleSchemas[index]
        return immediateChildren(chosenSchema, definitionStorage)
        
    if 'type' in data.keys():
        if isinstance(data['type'], str):
            strType = data['type']
    
    if 'properties' in data.keys():
        propertyList = data['properties']
    
    strArrRequiredProps = []
    if 'required' in data.keys():
        # TODO: Have this set data generation to "optional" mode. Generate data by default, but if 'required' is present, generate only that.
        strArrRequiredProps = data['required']
    
    ret = None
    if '$ref' in data.keys():
        reference = data['$ref']
        ret = immediateChildren(definitionStorage[reference], definitionStorage)
        return ret;
    
    # TODO: Break this out into a 'generate data by type' method or something.
    if strType == 'array':
        ret = [];
    elif strType == 'object':
        ret = {};
    elif strType == 'string':
        if 'format' in data:
            # FYI: Don't visit that IP at work. ;D
            if data['format'] == 'ipv4':
                ret = '31.192.117.132'
        else:
            ret = 'Lorem ipsum and all that jazz'
    elif strType == 'boolean':
        ret = True
    elif strType == 'integer':
        min = 0
        max = 32
        multOf = 1
        if 'multipleOf' in data:
            multOf = data['multipleOf']
        if 'maximum' in data:
            max = data['maximum']
        if 'minimum' in data:
            min = data['minimum']
        if 'exclusiveMaximum' in data:
            max -= 1
        if 'exclusiveMinimum' in data:
            min += 1
        if max > min:
            ret = random.randint(min, max)
        else:
            ret = random.randint(max, min)
        if (multOf > 0):
            ret = int(ret / multOf)
            ret *= multOf

    if isinstance(ret, dict):
        listProps = []
        if len(strArrRequiredProps) == 0:
            listProps = data['properties']
        else:
            listProps = strArrRequiredProps
        for prop in listProps:
            ret[prop] = immediateChildren(data['properties'][prop], definitionStorage)
    
    if isinstance(ret, list):
        defaultMaxItems = 1
        if 'maxItems' in data.keys():
            defaultMaxItems = data['maxItems']
        for prop in range(0, defaultMaxItems):
            ret.append(immediateChildren(data['items'], definitionStorage))
    
    return ret;

if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument("-f", "--file",
                      dest='infile',
                      help='JSON Schema file to use as a template',
                      type=argparse.FileType('r'))
                      
    args = argp.parse_args()
    sInput = args.infile.read()
    jsonInput = json.loads(sInput)
    print ('=== INPUT SCHEMA ===')
    print (json.dumps(jsonInput, indent = 2))
    
    traverse('', jsonInput, 0)
    ret = immediateChildren(jsonInput, {})
    print ('=== OUTPUT JSON ===')
    jsonRet = json.dumps(ret, indent=2, sort_keys = True);
    
    print ('=== ERRORS ===')
    jsonschema.validate(ret, jsonInput)
    
    print(jsonRet)
