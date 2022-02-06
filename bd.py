import sqlite3
import fnmatch

where_db = "users.db"
#where_db = "/root/git/irc_voice_bot/users.db"

# Check is name or ident of user is in the DB:
def get_role(name, ident):        
    conn = sqlite3.connect(where_db)
    cur = conn.cursor()        
    # Try find user in DB by name:
    user_role = "guest"
    try:
        cur.execute(f"SELECT role from users WHERE name = '{name}'")
        data_cur = cur.fetchall()
        if data_cur:
            user_role = data_cur[0][0]
        else:
            # Try find user in DB by ident:
            try:
                cur.execute(f"SELECT role from users WHERE ident = '{ident}'")
                data_cur = cur.fetchall()
                if data_cur:
                    user_role = data_cur[0][0]
            except IndexError:
                print(f"***user: {name} is not in DB***")
    except IndexError:
        print(f"***user: {ident} is not in DB***")
        
    print(f"user_role: {user_role}")

    # Close the DB:
    conn.close
    
    return user_role
    
# Chek in ban list:
# Ident in ban list like a: "*@888.888.888.*"
def check_ban(ident):
    ident = f'*!{ident}'
    conn = sqlite3.connect(where_db)
    cur = conn.cursor()    
    cur.execute("SELECT ident from bans")
    data_cur = cur.fetchall()
    
    for i in data_cur:
        i = i[0]
        if fnmatch.fnmatch(ident, i):
            return i      
    return 0
    
# Command for add user in db:
def add_user(message, channel, command_put_user_in_bd):   
    
    #default name and ident are NULL:
    name = "NULL"
    ident = "NULL"  
    #if get name and ident:
    list_data = message.split(' ')    
    for i in list_data:
        # if the ident (that '@' in string)
        if '@' in i:
            ident = i.strip()
        elif '@' not in i and i != '':
            name = i.strip()
    # If amdin inter empty command send him instuction       
    if name == "NULL" and ident == "NULL":
        return f"PRIVMSG {channel} :Inter like this: '{command_put_user_in_bd} name_user (and/or) ident_user'"
        
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        if name != "NULL" and ident != "NULL":
            c.execute(f"INSERT INTO users (name, ident) VALUES \
            ('{name}', '{ident}')")
            conn.commit()
            
        elif name != "NULL" and ident == "NULL":
            c.execute(f"INSERT INTO users (name) VALUES \
            ('{name}')")
            conn.commit() 

        elif name == "NULL" and ident != "NULL":
            c.execute(f"INSERT INTO users (ident) VALUES \
            ('{ident}')")
            conn.commit()    
            
    except sqlite3.IntegrityError:
        print('***Error: sqlite3.IntegrityError***\n')
     
    conn.close
    return f"PRIVMSG {channel} :{name} {ident} is added in data base!\r\n"     
    
# Add a ident in ban list:
def add_ban(ident, cause, name):    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute(f"INSERT INTO bans (date, ident, comment, name) VALUES \
                 (datetime('now'), '{ident}', '{cause}', '{name}')")
    except sqlite3.IntegrityError: 
        return "UNIQUE ERROR"
    conn.commit()
    conn.close
    print(f"***ban cause: {cause}***\n")
   
# Delete a ban from Data Base:
def del_ban(ident):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute(f"SELECT id from bans WHERE ident = '{ident}'")
    data_cur = cur.fetchall()    
    cur.execute(f"DELETE FROM bans WHERE ident = '{ident}'")
    conn.commit()
    conn.close
    if data_cur:
        return True