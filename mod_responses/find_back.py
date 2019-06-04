from evawiz_basic import *
from mserver_basic import *

def response(handler):
    dprint('find back operation',handler.mark)
    creq = handler.recv()
    dprint('request = ',creq)
    if not creq == 'eva! I want to find back':
        raise Exception('rule not followed in response_find_back')
    handler.send("allow to find back");
    email = handler.encrypt_recv();
    email.strip()
    if not re.match('^[a-zA-Z0-9_\.\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-\.]+$',email) or len(email)>128 : 
        raise Exception('invalid email, may request from attackers', handler.mark)
    #check email if taken return email is already taken as al_email by sonme abort this register
    count = handler.cursor.execute("""select * from musers where al_email=%s""",(email,) )
    if count == 0:
        handler.send('email not recorded.')
        return
    handler.user_info = handler.cursor.fetchone()
    ## send mail by current service@eva.run
    #create mail which has a verification code to change password
    verify_code = random_simple_key(6)
    verify_time = int( time.time() )
    dprint('verify code = ',verify_code,'try send code via email')
    mail_content = """ <body link="#0066FF" vlink="#666699" style="tab-interval:21.0pt; text-justify-trim:punctuation">
    <div style="width:700px">
    <div> <span> Dear Evawiz Users:</span> </div>
    <p><span><span style="mso-spacerun:yes">&nbsp;
    </span>You are requesting password change from host with <span class="GramE">IP(</span>%s)
    and MAC(%s) for your Evawiz Account <font color="#0000FF">%s</font>. If this is true, you can use the verification code given below to
    continue your operation. Otherwize just ignore this mail.</span></p>
    <p align="center" style="text-align:center"><font color="#0000FF">%s</font></p>
    <p><span>Best</span></p>
    <p><span><a href="mailto:service@eva.run">service@eva.run</a></span></p>
    <p><span>Evawiz Group</span></p>
    </div>
    </body>"""%(handler.host_ip,handler.host_mac,handler.user_info['name'],verify_code,)
    if mail_by_service([email], "Evawiz Password Change Notice",mail_content):
        handler.send("Internal Error {0} while sending verification mail. Please report to service@eva.run".format(line_no(),))
        log("mail_error","Internal Error {0} while sending verification mail. Please report to service@eva.run".format(line_no(),))
        return
    else:
        dprint("verify code sent successfully")
        pass

    dprint("verify code sent. wait for response")
    handler.send('please check your mailbox')
    code_recv = handler.encrypt_recv()
    cur_time = int( time.time() )
    dprint("'%s'--'%s'"%(cur_time,verify_time))
    if ( cur_time - verify_time > 900 ):
        dprint("time out")
        handler.send( "verify time out" )
        return

    dprint("'%s'--'%s'"%(code_recv,verify_code))
    if code_recv != verify_code:
        dprint("code wrong")
        handler.send( "verify code wrong" )
        return
    dprint("verify success")
    handler.send("verify success")

    password = handler.encrypt_recv()
    password.strip()
    if not re.match('^.{8,64}$',password) or re.match('^[0-9]+$',password) or re.match('^[a-zA-Z]+$',password):
        raise Exception('invalid password, may request from attackers',handler.mark)
    #dprint('register with password ',password)
    if not set_passwd( handler.user_info['name'], password ):
        handler.send("Internal Error %s. Please report to service@eva.run"%s(line_no(),))
        return
    handler.send('password changing done')
    return

