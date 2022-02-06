#----func for kick and ban-------    
def kick_ban(channel, ident, name_user, cause):
    send_kick = f"KICK {channel} {name_user}\r\n"
    send_ban = f"MODE {channel} +b {ident}\r\n"
    
    print(f"*** kick ban for: {cause}! ***\r\n")            
                
    return [send_ban, send_kick]