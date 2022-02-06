#! /usr/bin/env python
# -*- coding: utf-8 -*-

#------Function shortening of irc.send----
 
def send(mes):
    print(f'>> {mes}')
    return irc.send(bytes(mes,'utf-8'))     

#-------Import modules---------------------

import socket
import sys
import time
import requests
import settings
import sqlite3
import random
import time
from datetime import datetime
import os

import dict_quest
import func_ban
import bd
  
#-------Connect server----------------------

network = settings.settings('network')
port = settings.settings('port')
irc = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
channel = settings.settings('channel')
botName = settings.settings('botName')
masterName = settings.settings('masterName')

#-------Connect to IRC-server----------------

irc.connect ((network, port))
send('NICK '+botName+'\r\n')
send('USER '+botName+' '+botName+' '+botName+' :Python IRC\r\n')
send('JOIN '+channel+' \r\n')
send('NickServ IDENTIFY '+settings.settings('password')+'\r\n')
send('MODE '+botName+' +x')

#------Commands-----------

command_for_ban = "!b"
#command for clear all ban list channel
command_for_clear_ban_list = "!cb"
command_for_unban = "!ub"
command_put_user_in_bd = "!au"
command_get_voice = "!voice"
command_flood_on_off = "!flood"
command_joinflood_on_off = "!join"
command_get_help = f"!{botName} help"
command_renameflood_on_off = f'rename'

command_all_defenses_off = f"!{botName} off"
command_all_defenses_on = f"!{botName} on"

#86400 sec = 1 day
time_for_clear_ban_list = 86400

time_for_join_flood = 15
time_for_rename_flood = 15

time_sleep_unban_list = 2

#------Flood variables---------------------
time_plus_flood_vlo_char = 5
vol_char_flood = 170
dict_flood_ident_time = {}

list_messages = []
vol_of_mess_repeate = 10
dictflood_ident_countmess = {}
dictflood_ident_countrepeat = {}
max_of_dictflood_ident_countrepeat = 30
countfloodrepeat = 3

dictflood_ident_countmess = {}
max_of_dictflood_ident_countmess = 30
dictflood_ident_timemess = {}
max_of_dictflood_ident_timemess = 30
vol_max_mess_freq_flood = 5
sec_in_flood_freq = 10

#-------Global_variables--------------------   
name = ''
message = ''
num_users = 0
is_bot_on = True

dict_name_question = {}
dict_quest = dict_quest.dict_quest()

tup_user_roles = {'superadmin','user','admin'}
tup_admins_roles = {'superadmin','admin'}
user_role = ""
user_role_join = ""
#where_db = "/root/git/irc_voice_bot/users.db"
where_db = "users.db"

#-------dates fot Bun bots!-----------------
ip_user_join = ""
name_user_join = ""
dict_ip_time = {}
dict_ip_name = {}      

dict_ip_time_rename = {}
ip_for_command_ban = ""
name_for_command_ban = 0
ip_in_file = ""

start_alarm_clear_ban_list = 0

start_alarm_clear_ban_list = time.time()

ip = ""

send_ban_kick = []
tuple_data_ban = []

is_send_list_ban = False
ip_del = ""
is_ip_in_bl = False

is_flood_on = True
is_joinflood_on = True
is_rename_on = True

#-------------Major_while-------------------------

while True:
    
    try:
        data = irc.recv(2048).decode("UTF-8")
    except UnicodeDecodeError:
        print('ERROR: UnicodeDecodeError')
        
    # Ping-pong.
    if 'PING' in data:
        print('PONG: '+'PONG '+data.split()[1]+'\r\n')
        send('PONG '+data.split()[1]+'\r\n')
    
    # Make variables Name, Message, IP from user message.
    # that look a server message: ":Кай!uid230437@helmsley.irccloud.com PRIVMSG #bt :text message"
    if ' PRIVMSG ' in data:
        name = data.split('!',1)[0][1:]
        ident_user = data.split('!',1)[1].split(' ',1)[0]
        message = data.split('PRIVMSG',1)[1].split(':',1)[1].strip().lower()
        
        # Check is name or ident of user is in the DB:        
        user_role = bd.get_role(name, ident_user)
        
        #-----------------Anti Flood!-----------------
        
        if is_flood_on == True and user_role not in tup_user_roles:
            # Flood check if more (170) chars once in 1 min: 
            if len(message) > vol_char_flood:
                if ident_user in dict_flood_ident_time and \
                dict_flood_ident_time[ident_user] < time.time() + time_plus_flood_vlo_char:
                    cause = f"FLOOD MORE {vol_char_flood} CHARE"
                    if bd.add_ban(f"*!{ident_user}", cause, name) == "UNIQUE ERROR":
                        print('***Такой бан уже есть!***\r\n')
                    else:
                        send_ban_kick = func_ban.kick_ban(channel, f"*!{ident_user}", name, cause)
                        send(send_ban_kick[0])
                        send(send_ban_kick[1])
                else:
                    dict_flood_ident_time[ident_user] = time.time()
                    
            #--------------------------------------------------------------        
                    
            # Flood check repeat one of (5) last messages:            
            if message in list_messages:
                if ident_user not in dictflood_ident_countrepeat:
                    dictflood_ident_countrepeat[ident_user] = 0
                if ident_user in dictflood_ident_countrepeat:
                    dictflood_ident_countrepeat[ident_user] += 1
                    
                if dictflood_ident_countrepeat[ident_user] > countfloodrepeat:
                    del dictflood_ident_countrepeat[ident_user] 
                    cause = f"FLOOD REPEATE MESSAGE"
                    if bd.add_ban(f"*!{ident_user}", cause, name) == "UNIQUE ERROR":
                        print('***Такой бан уже есть!***\r\n')
                    else:
                        send_ban_kick = func_ban.kick_ban(channel, f"*!{ident_user}", name, cause)
                        send(send_ban_kick[0])
                        send(send_ban_kick[1])    
                    
            # if dict very large clear them 
            if len(dictflood_ident_countrepeat) > max_of_dictflood_ident_countrepeat:
                dictflood_ident_countrepeat.clear()
                
                    
            # add any message of guest in list:
            list_messages.append(message)
            
            if len(list_messages) > vol_of_mess_repeate:
                list_messages.clear()
                
            #---------------------------------------------------------------
            
            # Flood high frequency of messages
            
            if ident_user not in dictflood_ident_countmess:
                dictflood_ident_countmess[ident_user] = 1
                dictflood_ident_timemess[ident_user] = time.time()
            
            if ident_user in dictflood_ident_countmess:
                dictflood_ident_countmess[ident_user] += 1                
                if dictflood_ident_countmess[ident_user] > vol_max_mess_freq_flood:
                    if sec_in_flood_freq < (time.time() - dictflood_ident_timemess[ident_user]):                         
                        dictflood_ident_countmess[ident_user] = 1
                        dictflood_ident_timemess[ident_user] = time.time()
                    else:
                       cause = f"FLOOD high frequency of messages"
                       if bd.add_ban(f"*!{ident_user}", cause, name) == "UNIQUE ERROR":
                           print('***Такой бан уже есть!***\r\n')
                       else:
                           send_ban_kick = func_ban.kick_ban(channel, f"*!{ident_user}", name, cause)
                           send(send_ban_kick[0])
                           send(send_ban_kick[1])
                       # deletes dates of the guest homs bans from dicts    
                       del dictflood_ident_countmess[ident_user]
                       del dictflood_ident_timemess[ident_user]
                
                #clear dicts if they are very large
                if len(dictflood_ident_countmess) > max_of_dictflood_ident_countmess:
                    dictflood_ident_countmess.clear()
                if len(dictflood_ident_timemess) > max_of_dictflood_ident_timemess:
                    dictflood_ident_timemess.clear()
                    
    #-----------------On or Off defense of the bot-----------
    
    # On Off all defanses!
    if "PRIVMSG " in data and f":{command_all_defenses_on}" in data and user_role in tup_admins_roles:
        is_bot_on = True
        is_flood_on = True
        is_joinflood_on = True
        is_rename_on = True            
        send(f'PRIVMSG {channel} :All defenses On!\r\n')

    if "PRIVMSG " in data and f":{command_all_defenses_off}" in data and user_role in tup_admins_roles:
        is_bot_on = False
        is_flood_on = False
        is_joinflood_on = False
        is_rename_on = False            
        send(f'PRIVMSG {channel} :All defenses Off!\r\n')         

    # Get voice
    if "PRIVMSG " in data and f":{command_get_voice}" in data and user_role in tup_admins_roles:
        if is_bot_on == False:
            is_bot_on = True       
            send('MODE '+channel+' +m\r\n')
            send(f'PRIVMSG {channel} :voice mode on!\r\n')
        else:
            is_bot_on = False       
            send('MODE '+channel+' -m\r\n')
            send(f'PRIVMSG {channel} :voice mode off!\r\n')
    
    # On or Off Anti-Flood functions    
    if "PRIVMSG " in data and f":{command_flood_on_off}" in data and user_role in tup_admins_roles:
        if is_flood_on == False:
            is_flood_on = True
            send(f'PRIVMSG {channel} :anti-flood on!\r\n')
        else:
            is_flood_on = False
            send(f'PRIVMSG {channel} :anti-flood off!\r\n')
            
    # On or Off Anti-Join flood functions
    if "PRIVMSG " in data and f":{command_joinflood_on_off}" in data and user_role in tup_admins_roles:
        if is_joinflood_on == False:
            is_joinflood_on = True
            send(f'PRIVMSG {channel} :anti-Join-flood on!\r\n')
        else:
            is_joinflood_on = False
            send(f'PRIVMSG {channel} :anti-Join-flood off!\r\n')
            
    # On or Off Anti Rename flood functions
    if "PRIVMSG " in data and f":{command_renameflood_on_off}" in data and user_role in tup_admins_roles:
        if is_rename_on == False:
            is_rename_on = True
            send(f'PRIVMSG {channel} :anti-Rename-flood on!\r\n')
        else:
            is_rename_on = False
            send(f'PRIVMSG {channel} :anti-Rename-flood off!\r\n')
            
    
    # If admin send help command get him hepl instriction off commands        
    if "PRIVMSG " in data and f":{command_get_help}" in data and user_role in tup_admins_roles:
        send(f"NOTICE {name} :!b *!*@888.888.888* - example for permban a user to the data base\n")        
        send(f"NOTICE {name} :!ub *!*@888.888.888* - example command for unban thg ident from the data base and ban list channel\n")
        send(f"NOTICE {name} :!au nick_name *!*@888.888.888* - (you can write only nick_name, or only ident) example command for add the guest in data base as a 'user' (he will auto get voice and anti-flood will do not worl to him!)\n")
        send(f"NOTICE {name} :!{command_get_voice} - command for on/off function bot for get to a guest a question and voice after true answer\n")
        send(f"NOTICE {name} :!{command_joinflood_on_off} - command for on/off anti-Join-flood functions of the bot\n")
        send(f"NOTICE {name} :!{command_flood_on_off} - command for on/off anti-flood functions of the bot\n")
    
    #--------Anti-JOIN Flood----------    
    if ' JOIN :'+channel in data in data and ' PRIVMSG ' not in data:
        
        #------Bun bots!-------
        #get name & ident of user         
        name_user_join = data.split('!',1)[0][1:]
        ident_user_join = data.split('!',1)[1].split(' ',1)[0]        
        
        # Get a role of the user:
        user_role_join = bd.get_role(name_user_join, ident_user_join)
        if user_role_join in tup_user_roles:
           send('MODE '+channel+' +v '+name_user_join+'\r\n') 
           print(f"***Join {user_role_join}***\r")
            
        #------Ban & kick if the IP in PERMBAN list-----------
        elif user_role_join not in tup_user_roles:
            # 1 is ident is in ban list, 0 is ident not in ban list            
            cause = "find_in_ban_list"
            return_check_ban = bd.check_ban(ident_user_join)            
            if return_check_ban != 0:
                send_ban_kick = func_ban.kick_ban(channel, return_check_ban, name_user_join, cause)                
                send(send_ban_kick[0])
                send(send_ban_kick[1])
                
            else:                         
                #------join flood------- 
                #check join ip for time
                if is_joinflood_on == True:
                    cause = "JOIN FLOOD"
                    for ip in dict_ip_time:
                        if ident_user_join == ip and time.time() - dict_ip_time[ip] < time_for_join_flood:                        
                            if bd.add_ban(f"*!{ident_user_join}", cause, name_user_join) == "UNIQUE ERROR":
                                print('***Такой бан уже есть!***\r\n')
                            else:
                                send_ban_kick = func_ban.kick_ban(channel, f"*!{ident_user_join}", name_user_join, cause)
                                send(send_ban_kick[0])
                                send(send_ban_kick[1])
                            
                #add new [name:ip] in dict
                dict_ip_name[ident_user_join] = name_user_join
                #add new ip & time in dict        
                dict_ip_time[ident_user_join] = time.time()
                
                #--------If name not in bd_voice get him a captcha------
                    
                if is_bot_on == True:                            
                    question_voice = random.choice(list(dict_quest))
                    send(f"PRIVMSG {name_user_join} :***Что бы получить войс на {channel} ответьте на \
вопрос: {question_voice}\r\n")                           
                    dict_name_question[name_user_join] = dict_quest[question_voice]  
    
    # Get a voice if guest get true answer for question captcha                
    if is_bot_on == True:
        if 'PRIVMSG '+botName+' :' and name in dict_name_question and \
           message == dict_name_question[name]:                      
            send('MODE '+channel+' +v '+name+'\r\n')
            send(f'PRIVMSG {name} :Ответ правильный! Вы получили +v (голос) на {channel}\r\n')                
            del dict_name_question[name]
            
    #-----------Rename flood---------- 
         
    if " NICK :" in data and "PRIVMSG" not in data and is_rename_on == True:
        #add old & new nick in dict
        ip_rename = data.split('!',1)[1].split(' ',1)[0]
        new_name = data.split("NICK :")[1].strip()
        nick_rename_role = bd.get_role(new_name, ip_rename)
        if nick_rename_role not in tup_user_roles:
            #rewrite name in dict with ident (ip)
            dict_ip_name
            #if this ip rename again with a little time
            if ip_rename in dict_ip_time_rename and time.time() - dict_ip_time_rename[ip_rename] < time_for_rename_flood: 
                cause = "NICK FLOOD"
                if bd.add_ban(f"*!{ip_rename}", cause, new_name) == "UNIQUE ERROR":
                    print('***Такой бан уже есть!***\r\n')
                else:
                    send_ban_kick = func_ban.kick_ban(channel, f"*!{ip_rename}", new_name, cause)
                    send(send_ban_kick[0])
                    send(send_ban_kick[1])
                    
            dict_ip_time_rename[ip_rename] = time.time()
            
    #---------Command for put user into Data Base -----------
    
    if f"PRIVMSG {channel} :{command_put_user_in_bd} " in data and user_role in tup_admins_roles:
        #send to def a message with the command:       
        send(bd.add_user(data.split(f"{command_put_user_in_bd}")[1], channel, command_put_user_in_bd))          
            
    #------------Quit command----------  
    if user_role == 'superadmin' and data.find('PRIVMSG '+channel+' :!'+botName+' quit') != -1:
        send('PRIVMSG '+channel+' :Хорошо, всем счастливо оставаться!\r\n')
        send('QUIT\r\n')
        sys.exit()
        
    #------------Ban command------------
    
    if user_role in tup_admins_roles and f"PRIVMSG {channel} :{command_for_ban} " in data:
        print("***ban command work!***")
        ip_for_command_ban = data.split(f"{command_for_ban}")[1].strip()
        
        #try get name from dict by ip_for_command_ban
        try:
            name_for_command_ban = dict_ip_name[ip_for_command_ban]
        except:
            name_for_command_ban = "NULL"
        
        cause = "COMMAND"        
        if bd.add_ban(ip_for_command_ban, cause, name_for_command_ban) == "UNIQUE ERROR":
            send('PRIVMSG '+channel+' :Такой бан уже есть!\r\n')
        else:
            send_ban_kick = func_ban.kick_ban(channel, ip_for_command_ban, name_for_command_ban, cause)
            send(send_ban_kick[0])
            send(send_ban_kick[1])

    #------------clear ban list channel--------------    
    
    #If alarm time now or more - send me to server for get ban list channel!
    if (time.time() > start_alarm_clear_ban_list + time_for_clear_ban_list 
    or f"PRIVMSG {channel} :{command_for_clear_ban_list}" in data and user_role in tup_admins_roles):
        print("***clear ban list channel work!***\n")
        is_send_list_ban = True
        send(f"MODE {channel} +b\r\n")
    
    #If get ban list channel - get list ban channel from server
    if "PRIVMSG " not in data and f" {botName} {channel} *" in data and is_send_list_ban == True:        
        #get a IP from data
        tuple_data_ban = data.split(f"{channel} ")        
            
        for i in tuple_data_ban:
            try:
                ip = i.split("*",1)[1].strip()                
                #unban the ip
                send(f"MODE {channel} -b *{ip}\r\n")            
                time.sleep(time_sleep_unban_list)                
            except IndexError:
                print("***IndexError in for i in clear list***\n")               
        
        #Start alarm time for clear ban list
        start_alarm_clear_ban_list = time.time()
        is_send_list_ban = False
        
    #------------Delete Ban in Data Base command----------
    
    if f"PRIVMSG {channel} :{command_for_unban} " in data and user_role in tup_admins_roles:
    
        # get IP for delete the line in file:
        ip_del = data.split(f"{command_for_unban} ")[1].strip() 
                    
        # If ip find in the ban list:
        if bd.del_ban(ip_del) == True:            
            send(f"PRIVMSG {channel} :{ip_del} deleted from permban list!\r\n")
            send(f"MODE {channel} -b {ip_del}\r\n")        
        else:   
            send(f"PRIVMSG {channel} :Error! {command_for_unban} - this IP not in ban list!\r\n")
        
    #------------Printing---------------       

    print(f"<<<<{data}")
