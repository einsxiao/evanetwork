from evawiz_basic import *
from mserver_basic import *
def response(handler):
    dprint('register_user operation ',handler.mark)
    creq = handler.recv()
    dprint('request = ',creq)
    if not creq == 'eva! I want to register': raise Exception('rule not followed in response_register_user')

    handler.send('allow to register')
    #register process
    #recieve info to compete the process

    #check user name registered or not
    while True:
        user_name = handler.recv() #should recv 'check user '
        #check validity
        status = handler.check_username(user_name)
        if status == 'valid name': break
        if status == 'invalid format':
            raise Exception('invalid username, may request from attackers',handler.mark)
        if status == 'name reserved' :
            handler.send('user name is reserved')
            continue
        if status == 'name taken':
            handler.send('user name already taken')
            continue
        handler.send('invlid username')
    handler.send('user name valid')

    #password
    password = handler.encrypt_recv()
    password.strip()
    if not re.match('^.{8,64}$',password) or re.match('^[0-9]+$',password) or re.match('^[a-zA-Z]+$',password):
        raise Exception('invalid password, may request from attackers',handler.mark)
    #dprint('register with password ',password)
    handler.send('password ok')

    #email
    email = handler.recv()        
    email.strip()
    if not re.match('^[a-zA-Z0-9_\.\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-\.]+$',email) or len(email)>128 : 
        raise Exception('invalid email, may request from attackers', handler.mark)
    #check email if taken return email is already taken as al_email by sonme abort this register
    count = handler.cursor.execute("""select `id` from musers where al_email=%s""",(email,) )
    if count > 0:
        handler.send('email taken')
        return 
    handler.send('email ok')
    #dprint('register with email = ',email,handler.mark)

    ## check email address
    verify_code = random_simple_key(6)
    dprint('verify_code = ',verify_code)
    verify_time = int( time.time() )
    mail_content = """ <body link="#0066FF" vlink="#666699" style="tab-interval:21.0pt; text-justify-trim:punctuation">
    <div style="width:700px">
    <div> <span> Dear %s:</span> </div>
    <p><span><span style="mso-spacerun:yes">&nbsp;
    </span>You are trying to register an EVAWIZ account from host with <span class="GramE">IP(</span>%s)
    and MAC(%s). If this is true, you can use the verification code given below to
    continue your operation. Otherwize just ignore this mail.</span></p>
    <p align="center" style="text-align:center"><font color="#0000FF">%s</font></p>
    <p><span>Best</span></p>
    <p><span><a href="mailto:service@eva.run">service@eva.run</a></span></p>
    <p><span>Evawiz Group</span></p>
    </div>
    </body>"""%(user_name,handler.host_ip,handler.host_mac,verify_code,)
    dprint("mail content = ",mail_content)
    if mail_by_service([email], "Evawiz Account Register",mail_content):
        log("error","when sending verification mail, error occur {0} {1}".format(file_name(),line_no(),) )
        handler.send("Internal Error {0} when sending verification mail. Please report to service@eva.run".format(line_no(),))
        return
    else:
        handler.send("check mail")
        pass

    code_recv = handler.recv()
    cur_time = int( time.time() )
    dprint("'%s'--'%s'"%(cur_time,verify_time))
    if ( cur_time - verify_time > 900 ):
        handler.send( "verify time out" )
        return

    dprint("'%s'--'%s'"%(code_recv,verify_code))
    if code_recv != verify_code:
        handler.send( "verify code wrong" )
        return

    #info ready, try to create the user and send result
    #add system users and set the password
    #user_id = '10000'

    #record the host local user
    count = handler.cursor.execute("""select * from hostusers
    where host_mac=%s and name=%s limit 1""", (handler.host_mac,handler.host_user,) )
    if count == 0: # record it
        if not handler.record_host_user(handler.host_mac,handler.host_user):
            handler.send("failed to register")
            log("record_local_user","failed to record local user")
            dprint("Failed to record host user")
            ## some error occured
            raise Exception("failed to record local user")
    else:
        handler.host_user_info = handler.cursor.fetchone()
        pass

    #create server account of the linux system
    user_id = create_evawiz_user(user_name,password)
    if not user_id:
        handler.send("failed to register")
        dprint("Failed to create system user")
        log("create_system_user","failed to create system user")
        raise Exception("fail to create system user")
    try:
        #add information to database users and al_email or any other related tables
        dprint('user_name =',user_name,type(user_name))
        dprint('user_id =',user_id,type(user_id) )
        dprint("%s,%s,%s"%(user_id,user_name,ctimestr()))
        #add the two users group
        dprint("clean users and musers old info")
        dprint("clean users")
        handler.cursor.execute("""delete from users where user_id=%s""",(user_id,))
        dprint("insert into users")
        handler.cursor.execute("""insert into users(user_id,username,mail_host,created)
        values(%s,%s,%s,%s)""", (user_id,user_name,'eva.run',time.strftime('%Y-%m-%d %H:%M:%S'),) )
        dprint("insert into musers")
        dprint(user_id,user_name,email,handler.host_mac,handler.host_ip)
        handler.cursor.execute("""insert into musers(id,name,nickname,al_email,register_mac,register_ip)
        values(%s,%s,%s,%s,%s,%s)""", (user_id,user_name,user_name,email,handler.host_mac,handler.host_ip) )
        #update table of host and hostusers 

        #construct and send connection information
        #produce a pass for connected_pass of host_user
        raw_pass = random_key(20)
        dprint('raw_pass =',raw_pass," then update the hostusers connection info")
        dprint("id = ",user_id)
        dprint('host_id = ',handler.host_user_info['id'])
        #store the pass in database
        count = handler.cursor.execute(
            """
            update hostusers set
            connected_user_id={0},
            connected_pass="{1}"
            where id={2}
            """.format(
                user_id,
                passcrypt(raw_pass.encode() ),
                handler.host_user_info['id'],
            )
        )
        dprint('count = ',count)
    except Exception as e:
        dprint(e)
        #roll back -- delete user added
        log("register","failed to register:"+str(e))
        dprint("register","failed to register:"+str(e))
        dprint("Error raised, roll back")
        handler.send("failed to register")
        handler.recv()
        handler.send("Internel error %s when try register. Please report to service@eva.run"%(line_no(),))
        delete_evawiz_user(user_name);
        dprint("Failed to create user cause database error")
        log("create_system_user","failed to create system user cause database error")
        raise Exception(e)


    handler.conn.commit()
    # host_pass = handler.host_info['password'][0:20]
    host_pass = random_key(20)
    #dprint('host_pass=',host_pass)
    handler.send( connect_aes.encrypt(host_pass+raw_pass) ) 

    pass

