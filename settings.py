import json

#----input_password-----
with open('code.json', 'r') as code_json:
    code=code_json.read()

obj = json.loads(code)

password = str(obj['password'])
botName = str(obj['bot_name'])
channel = str(obj['channel'])
network = str(obj['network'])
port = int(obj['port'])

masterName = 'Кай'

def settings(x):
    if x == 'network':
        return network
    elif x == 'port':
        return port
    elif x == 'botName':
        return botName
    elif x == 'masterName':
        return masterName
    elif x == 'password':
        return password   
    elif x == 'channel':
        return channel