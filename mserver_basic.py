from evawiz_basic import *

connect_aes = AESEncryption('?@*SlN15eJWRbeV@,ZRjSUINk*ELo)Zx')

def mail_by_service( mailto_list, subject, content):
    mname="Evawiz Service"
    mhost="eva.run" 
    muser="service"   
    mpass="3474service@eva.run" 
    mpostfix="eva.run" 
    return send_mail(mname, mhost, muser, mpass, mpostfix, mailto_list, subject, content)
################################
    
################################
## log setting
log_directory = os.path.join( os.getenv('EVAWIZ_ROOT'),'log/' )
def log(log_name,*params):
    log_file = log_directory + log_name
    if not os.path.exists(log_file): os.system('touch '+log_file)
    hfile = open(log_file,'a+')
    hfile.write(">>>")
    for i in params:
        hfile.write(i)
    hfile.write("<<<\n")
    hfile.close()

def get_user_id(account='root'):
    dprint('try get id for account %s'%(account) )
    (status,output) = shell_status_output('id -u '+account)
    if status != 0: return None 
    id = int(output)
    if ( id < 500 ): return None
    return id

def change_passwd(username,oldpasswd,newpasswd):
    dprint('try to change password of %s'%(username) )
    user_id = get_user_id(username)
    user_id = check_user_auth(username,oldpasswd)
    if not user_id:
        raise Exception('old passwd is not right when try to change passwd.')
    cmd_str = "echo %s | sudo passwd %s --stdin"%(newpasswd,username);
    (status,output) = shell_status_output(cmd_str);
    if ( status != 0 ):
        log('change_passwd',"failed to change password for %s"%username)
        return None
    else:
        return user_id

def set_passwd(username,newpasswd):
    dprint('try to set password of %s'%(username) )
    user_id = get_user_id(username)
    if not user_id:
        raise Exception('user %s is not exist when trying set passwd.'%(username))
    cmd_str = "echo '{0}\n{0}\n'| sudo passwd {1}".format(
        newpasswd, username
    );
    dprint("try set passwd with cmd = ",cmd_str)
    (status,output) = shell_status_output(cmd_str);
    dprint("status,output = ",status,output)
    if ( status != 0 ):
        dprint('set_passwd',"failed to set password for %s"%username)
        log('set_passwd',"failed to set password for %s"%username)
        return None
    else:
        return user_id
    
    #cmd_str = "/usr/bin/expect -f /opt/evawiz/binsev/passwd-expect -- -telent -host localhost -output ../log/passwd.out -log ../log/passwd.log"
    #p = subprocess.Popen(cmd_str,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    #p.stdin.write(username+"\n")
    #p.stdin.write(oldpasswd+"\n")
    #p.stdin.write(newpasswd+"\n")
    #ans = p.wait();
    #if  p.wait() == 0: return user_id 
    #log('change_passwd',"failed to change password.")
    #return None

def create_evawiz_user(username='',password='',isadmin=False):
    dprint('step into create_evawiz_user')
    user_id = get_user_id(username)
    if user_id: raise Exception('try to create a user which exist')
    if isadmin:
        homedir = '/data/admins/'+username
        cmd_str = "sudo /usr/sbin/useradd -d "+homedir+ " -c 'evawiz_admin' -g admins "+ username 
    else:
        homedir = '/data/users/'+username
        cmd_str = "sudo /usr/sbin/useradd -d "+homedir+ " -c 'evawiz_user' -g users "+ username 
        pass
    #global bsserver
    (status,output) = shell_status_output(cmd_str)
    dprint('status = ',status, 'output = ',output)
    if not status == 0:
        dprint('failed to create user',username,":",output)
        log('create_evawiz_user','failed to create '+username+":"+output)
        return None
    dprint('succeed to create local user',username)
    dprint('set passwd for local user ',username)
    result = set_passwd(username,password)
    dprint('set passwd result %s'%result);
    return result

def delete_evawiz_user(username=None,userid=None): #host is same as user, info need to erase too
    # need to execute with root previliges
    dprint('step into delete_evawiz_user')
    #if not getpass.getuser() == 'root': raise Exception('delete_evawiz_user should be run as root')
    dprint('username = ',username,' userid = ',userid)
    homedir = os.path.expanduser('~'+username)
    dprint('homedir = ',homedir)
    t_user_id = get_user_id(username)
    if not userid: userid = t_user_id
    if t_user_id != userid: raise Exception("username and userid not match when delete user");
    if not userid: return None
    if userid<500: raise Exception('try to delete a system user')
    cmd_str = 'sudo mv -f '+ homedir+' /data/backup/users/'
    dprint('execute '+cmd_str)
    (status,output) = shell_status_output(cmd_str)
    cmd_str = 'sudo /usr/sbin/userdel -r '+username
    dprint('execute '+cmd_str)
    (status,output) = shell_status_output(cmd_str)
    dprint('status =',status,' output =',output)
    if status == 0: return True
    else: return None

def check_user_auth(username,password):
    #check the user_name and password
    user_id = get_user_id(username)
    if not user_id: return None
    if user_id <500: return None
    (state,output) = shell_status_output("/opt/evawiz/binsev/auth-expect "+username+" "+password)
    dprint('state =',state,'output=',output)
    if state == 0:
        return user_id
    else:
        return None
    pass

