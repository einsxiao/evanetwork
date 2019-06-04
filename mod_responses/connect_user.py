from evawiz_basic import *
from mserver_basic import *
def response(handler):
#def response_connect_user(self):
    creq = handler.recv()
    dprint('first recv %s'%creq)
    if not creq == 'eva! I want to connect':
        raise Exception('rule not followed in response_connect_user') 

    #check whether host local user is recoreded, recored it
    count = handler.cursor.execute("""select * from hostusers
    where host_mac=%s and name=%s limit 1""", (handler.host_mac,handler.host_user,) )
    if count == 0: # record it
        dprint( "hostuser not recorded. Try to record it." )
        if not handler.record_host_user(handler.host_mac,handler.host_user):
            handler.send('not allowed to connect')
            ## some error occured
            return
    else:
        dprint( "hostuser recorded already." )
        handler.host_user_info = handler.cursor.fetchone()
    handler.send('allow to connect')

    #check user name registered or not
    (user_name,password) = handler.encrypt_recv().split() #should recv 'check user '
    #dprint(user_name,password)
    if not re.match('^[A-Za-z][A-Za-z0-9_-]{3,63}',user_name):
        handler.send('failed to connect')
        handler.recv();
        handler.send("nothing to tell");
        raise Exception('invalid username, may request from attackers',handler.mark)
    if not re.match('^.{8,64}$',password) or re.match('^[0-9]+$',password) or re.match('^[a-zA-Z]+$',password):
        handler.send('failed to connect')
        handler.recv();
        handler.send("nothing to tell");
        raise Exception('invalid password, may request from attackers',handler.mark)
    dprint(user_name,password)
    #check the user_name and password
    dprint("auth the pass info")
    user_id = check_user_auth(user_name,password) 
    dprint('user_id = ',user_id)
    if not user_id:
        handler.send('failed to connect')
        handler.recv();
        handler.send("user auth failed");
        return
    #check is a normal user
    dprint("check if a normal user")
    count = handler.cursor.execute(""" select name from musers
    where id=%s""",(user_id,) );
    if ( count == 0 ): #not a normal user
        handler.send('failed to connect')
        handler.recv();
        handler.send("the account connected to is not a normal user account.");
    #construct connect pass and send auth_info
    raw_pass = random_key(20)
    dprint('raw_pass =',raw_pass)
    #store the pass in database
    dprint('host_user_info = ',handler.host_user_info)
    count = handler.cursor.execute(
        """
        update hostusers set
        connected_user_id={0},
        connected_pass="{1}"
        where id={2}
        """.format(user_id,passcrypt(raw_pass.encode() ),handler.host_user_info['id'],) )
    # count = handler.cursor.execute("""update hosts
    # set user_amount=user_amount+1 
    # where id=%s """, (handler.host_info['id'],) )
    handler.conn.commit()
    # host_pass = handler.host_info['password'][0:20]   ## host no longer exist
    #raw_pass is generated lines ahead
    host_pass = random_key(20)
    dprint('host_pass=',host_pass)
    handler.send( connect_aes.encrypt(host_pass+raw_pass) ) 


