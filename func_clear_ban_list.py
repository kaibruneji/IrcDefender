import sys
import func_send
import time

#------Function shortening of irc.send---- 
def send(mes):
    print(f'>> {mes}')
    return irc.send(bytes(mes,'utf-8'))

#------Variables-----------------    

ip = ""
count = 1

#-------Conect to IRC-server----------------
network = settings.settings('network')
port = settings.settings('port')
irc = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

irc.connect ((network, port))

#-------def for clear all ban list----------

def clear(channel):    
    send(f"MODE {channel} +b\r\n")
    
    #try get the list from derver:
    try:
        #get data with answer from server 
        data = irc.recv(2048).decode("UTF-8")        
           
        #if data no empty:
        if "@" in data:
            while work_loop == 0:
                #get a IP from data
                try:
                    ip = data.split("@")[{count}].split("\r\n")                
                    count += 2
                    #unban the ip
                    send(f"MODE {channel} -b {ip}\r\n")                    
                except:
                    print("***End of ban list!***")
                    break 
                time.sleep(1)
        
    except UnicodeDecodeError:
        print('ERROR: UnicodeDecodeError')
    
    
    