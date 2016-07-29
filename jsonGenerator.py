import json
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

def immediateChildren(data):
    strType = ''
    if 'type' in data.keys():
        if isinstance(data['type'], str):
            strType = data['type']
    
    if 'properties' in data.keys():
        propertyList = data['properties']
    
    strArrRequiredProps = []
    if 'required' in data.keys():
        strArrRequiredProps = data['required']
    
    ret = None
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
    elif strType == 'integer':
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
    else:
        ret = 'test'
        
    if isinstance(ret, dict):
        for prop in strArrRequiredProps:
            ret[prop] = immediateChildren(data['properties'][prop])
    
    if isinstance(ret, list):
        defaultMaxItems = 1
        if 'maxItems' in data.keys():
            defaultMaxItems = data[defaultMaxItems]
        for prop in range(0, defaultMaxItems):
            ret.append(immediateChildren(data['items']))
    
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
    
    traverse('testSchema',jsonInput, 0)
    ret = immediateChildren(jsonInput)
    print ();
    jsonRet = json.dumps(ret, indent=2);
    
    print(jsonRet)
