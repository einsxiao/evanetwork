from evawiz_basic import *
from mserver_basic import *
    
def response(handler):
    dprint('step into response_check_user_info')
    #dprint('aes_key = ',handler.pass_aes_key)
    #check user information
    info = handler.recv()
    if info == 'do nothing':
        handler.send('nothing do')
        return
    #info raw state should be length of 96, decrypt state should be 40
    #first 20 chars are host_pass[0:20], rest 20 chars are host_user_pass
    dprint('raw_info = ',info,len(info))
    if ( not len(info) == 96 ):
        dprint('raw info not in the correct form')
        handler.send('user is not connected to server')
        raise Exception('check_user raw auth_info not in correct form, may from attackers')
    info = connect_aes.decrypt( info )
    dprint('info =',info,len(info))
    if not len(info) == 40:
        #dprint('info not in the correct form')
        handler.send('user is not connected to server')
        raise Exception("check_user auth_info not in correct form, may from attackers")
    #check pass
    rhost_pass = info[0:20]
    rconn_pass = info[20:40]
    count = handler.cursor.execute("""select * from hostusers
    where host_mac=%s and name=%s limit 1""",(handler.host_mac,handler.host_user,) )
    if count == 0:
        dprint('not connected or registered user check')
        handler.send('user is not connected')
        return
    ## since host no longer recorded, ignore it.
    dprint("check hostuser_info");
    handler.host_user_info = handler.cursor.fetchone()
    #no any relationship with host itself
    # if not rhost_pass == handler.host_info['password'][0:20] or not passcrypt(rconn_pass) == handler.host_user_info['connected_pass']:
    dprint( rconn_pass )
    dprint( passcrypt(rconn_pass ) )
    dprint( handler.host_user_info['connected_pass'] )
    if not passcrypt(rconn_pass) == handler.host_user_info['connected_pass']:
        dprint('connect info not right')
        handler.send('user connect info not right')
        return
    dprint("get connected user");
    #get connect user name
    count = handler.cursor.execute(""" select name from musers
    where id=%s""",(handler.host_user_info['connected_user_id'],) );

    if count == 0:
        handler.send("connected user not exist");
        return

    result = handler.cursor.fetchone();
    user_name =  result['name']

    handler.send('connected to server user %s'%user_name)
