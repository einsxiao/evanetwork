#!/usr/bin/env python
#coding:utf-8
################################################
## author: Xiao, Hu                           ##
## version: 1.0                               ##
## copyright: ECD                             ##
################################################
# class mserver, run in evawiz server         ##
################################################

from evawiz_basic import *
from mserver_basic import *
#import ssl
from socketserver import TCPServer, ThreadingMixIn, ForkingMixIn, StreamRequestHandler

import MySQLdb #heavy weight database

from importlib import  import_module
mod_operation_pairs = {
    'mod_ping':                 import_module("mod_responses.ping").response,
    'mod_register_user':        import_module("mod_responses.register_user").response,
    'mod_connect_user':         import_module("mod_responses.connect_user").response,
    'mod_find_back':            import_module("mod_responses.find_back").response,
    'mod_check_user_info':      import_module("mod_responses.check_user_info").response,
    'mod_check_module':         import_module("mod_responses.check_module").response,
    'mod_new_module':           import_module("mod_responses.new_module").response,
    'mod_delete_module':        import_module("mod_responses.delete_module").response,
    'mod_upload_module':        import_module("mod_responses.upload_module").response,
    'mod_download_module':      import_module("mod_responses.download_module").response,
    'mod_list_module':          import_module("mod_responses.list_module").response,
    'mod_perm_module':          import_module("mod_responses.perm_module").response,
    'mod_load_program':         import_module("mod_responses.load_program").response,
}

CONSTANTS.RUNNING_SIDE = "server"
######################
## database settings

def SetDBParas(database_host = None, database_port = None, database_user = None, database_passwd = None, database_database = None,baseserver='localhost'):
    global dbhost,dbport,dbuser,dbpasswd,dbdb,bsserver
    dbhost = database_host
    dbport = database_port
    dbuser = database_user
    dbpasswd = database_passwd
    dbdb = database_database
    bsserver = baseserver
    pass

#server local operation
class ServerOperation:

    def connect_database(self):
        ###database initialize
        global dbhost,dbuser,dbpasswd,dbdb,dbport
        dprint('connecting to database',dbhost)
        self.conn = MySQLdb.connect(dbhost,dbuser,dbpasswd,dbdb,dbport)
        self.cursor = self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        dprint('connected to database',dbhost)

    def disconnect_database(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()

    def generate_code(self,amount = 1):
        amount = int(amount)
        self.connect_database()
        if amount <1: raise Exception('amount give should be larger than 1')
        if amount > 100: raise Exception('too many code to generate') 
        dprint(amount)
        for i in range(0,amount):
            code = ''.join( random.sample(string.digits,10) )
            count = self.cursor.execute("""insert into register_codes(code) values(%s)""",(code,))
        self.conn.commit()
        self.disconnect_database()
        return code

    def create_evawiz_user(self,username = '',password='',isadmin=False):
        if not username: return None
        if not password: return None
        if not create_evawiz_user(username,password,isadmin):
            return None
        self.update_user_info(username)
        return True

    def update_user_info(self,username):
        if not username: return none
        user_id = get_user_id(username)
        if not user_id: return none
        self.connect_database();
        count = self.cursor.execute("select user_id from users where user_id=%s limit 1",(user_id,))
        if ( count == 0 ):
            self.cursor.execute("""insert into users(user_id,username,mail_host,created)
            values(%s,%s,%s,%s)""", (user_id,username,'eva.run',time.strftime('%Y-%m-%d %H:%M:%S'),) )
        count = self.cursor.execute("select id from musers where id=%s limit 1",(user_id,))
        if ( count == 0 ):
            self.cursor.execute("""insert into musers(id,name,nickname,al_email)
            values(%s,%s,%s,%s)""", (user_id,username,username,"",) )
        self.conn.commit()

    def delete_evawiz_user(self,user_name = None):
        self.connect_database()

        #clean database info
        dprint("clear user infomation")
        count = self.cursor.execute("select user_id from users where username=%s limit 1",(user_name,))
        if count > 0 : 
            result = self.cursor.fetchone()
            user_id = result['user_id']
            #dprint('user_id = ',user_id)
            #unconnect hostusers who connected to this user
            self.cursor.execute('''update hostusers
            set connected_user_id=NULL, connected_pass=NULL
            where connected_user_id=%s''',(user_id,) )

            # self.cursor.execute("""update hostusers
            # set registered_user_id=NULL
            # where registered_user_id=%s""",(user_id,) )

            self.cursor.execute("""update modules
            set user_id = 0, type = 'lost', perm_run = 'enable', perm_src = 'enable', perm_deve = 'disable'
            where user_id=%s """,(user_id,) )

            ###############delete infos
            self.cursor.execute("""delete from mperm_user where user_id=%s""",(user_id,) )
            self.cursor.execute("""delete from mgroup_members where user_id=%s""",(user_id,) )

            #delete users info,,#releated musers will auto deleted cause the foreign key restriction
            self.cursor.execute("""delete from users where user_id=%s""",(user_id,) ) 
            self.conn.commit()
            print('delete database info succeed')
        else:
            print('no user info in database')

        ####
        self.disconnect_database()

        # ##########delete groups connected by this user
        # self.delete_evawiz_host(user_name);

        ##########clean system_user
        print('try to delete system info of user %s'%(user_name))
        user_id = get_user_id(user_name)
        dprint('user_id = ',user_id)
        if user_id:
            delete_evawiz_user(user_name,user_id)
            print('delete system info processed')
        else:
            print('no system user exist')
            pass
        pass

    def get_register_code(self):
        self.connect_database()
        count = self.cursor.execute("""select code from register_codes limit 1""")
        if count == 0:
            return self.generate_code()
        result = self.cursor.fetchone()
        code = result['code']
        return code

    def deal_system_and_reserved_module(self):
        
        return True

    def create_module_filelist(self,module=''):
        if ( module == '' ): return False
        self.connect_database()

        pass

            
################################
## EvaTcpServer 


TCPServer.allow_resue_address = True
#class EvaTcpServer(ThreadingMixIn, TCPServer):
class EvaTcpServer(ForkingMixIn, TCPServer):
    # def get_request(self):
    #     (sock, addr) = TCPServer.get_request(self)
    #     return (context.wrap_socket(sock, server_side=True), addr)

    pass

class EvaHandler(StreamRequestHandler ):
    bufsize = 1024
    mark = None
    conn = None
    cursor = None
    aes = None

    #request host information
    user_info = None
    host_user_info = None
    host_mac = None
    host_user = None
    #request = None
    closed = False

    def connect_database(self):
        ###database initialize
        global dbhost,dbuser,dbpasswd,dbdb,dbport
        dprint('connecting to database',dbhost)
        self.conn = MySQLdb.connect(dbhost,dbuser,dbpasswd,dbdb,dbport)
        self.cursor = self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        dprint('connected to database',dbhost)

    def disconnect_database(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()
        pass

    def send_eof(self):
        self.request.close()
        self.closed = True
        pass

    def dbexecute(args):
        pass

    def dbfetchone(args):
        pass

    def dbfetchmany(args):
        pass

    def response_connection(self):
        ####get connection established
        self.mark =self.request.getpeername()
        print(self.mark)
        self.host_ip = self.mark[0]
        dprint('host_ip=',self.host_ip )
       
        dprint("wait for hello")
        res = self.recv()
        dprint("server first response = ",res)
        if ( res != 'Hello EVAWIZ! You are great!' ): raise Exception("connection request rule not followed");
        self.send( 'Connection to evawiz server at %s succeed!'%time.ctime() ) #send 1

        #rev aes key
        self.rsa = RSAEncryption('host')
        pubkeystr = self.rsa.get_pub_key_str()
        dprint("self.rsa_pub_key = ",self.rsa)
        self.send( pubkeystr )
        self.aes_key = self.rsa.decrypt( self.recv() )
        self.aes = AESEncryption( self.aes_key )

        dprint("aes key = ",self.aes_key)

        dprint("recv infos")
        #recv operation, mac, host_user
        self.operation = self.recv()
        dprint("operation = ", self.operation)
        self.host_mac = self.encrypt_recv()
        dprint("host_mac= ", self.host_mac)
        self.request_type = self.recv()
        dprint("type = ",self.request_type)
        self.host_user = self.recv()
        dprint("host_user = ",self.host_user)

        dprint("recved info %s %s %s %s"%(self.operation, self.host_mac, self.host_user, self.request_type) )
        dprint("try connect to database")
        self.connect_database()
        dprint("database connected")
        #register_host

        #no need to auth do nothing return
        #if not self.operation in ('register_user','check_user_info','connect_user','find_back', 'mod_register_user','mod_check_user_info','mod_connect_user','mod_find_back','mod_ping'):
        if not self.operation in operation_auth_free:
            #need to auth
            #dprint('try to auth user info')
            self.host_user_auth_info = self.encrypt_recv()
            self.host_user_connected = self.check_local_user_auth_info()
            if self.host_user_connected:
                self.send('auth passed')
                #dprint('auth passed')
            else:
                self.send('auth not passed')
                #dprint('auth not pass')
                raise Exception('user auth not passed')
            pass
        print('%s oper:%s mac:%s localuser:%s  %s'%(self.mark[0],self.operation,self.host_mac,self.host_user,time.ctime() ))
        pass

    def record_host_user(self,host_mac,host_user):
        #dprint('record local user into database')
        #record the local_user
        dprint( host_mac, host_user)
        count = self.cursor.execute("""insert into hostusers(host_mac,name) values
        (%s,%s)""",(host_mac,host_user,))
        host_local_user_id = self.conn.insert_id()
        self.conn.commit()
        count = self.cursor.execute("""select * from hostusers
        where id=%s """, (host_local_user_id,) )
        self.host_user_info = self.cursor.fetchone()
        return True

    def check_clean_name_pattern(self,name):
        if name in ('root','admin','evawiz','eva',): return False
        if re.match('\<shit',name):return False
        if re.match('\<piss',name):return False
        if re.match('\<crap',name):return False
        if re.match('\<fuck',name):return False
        if re.match('\<cunt',name):return False
        if re.match('\<cock',name):return False
        if re.match('\<mother.+fuck',name):return False
        if re.match('\<tits',name):return False

        return True

    def check_username(self,username): #return invalid format, name reserved, name taken, valid name
        if not re.match('^[a-z][a-z0-9_-]{3,63}',username):
            dprint('invalid format');
            return 'invalid format'
        if not self.check_clean_name_pattern(username):
            dprint('name forbidden');
            return 'name forbidden'
        #check if reserved
        count = self.cursor.execute("""select name from reserved_username
        where name=%s limit 1""",(username,) )
        if count > 0:
            dprint('name reserved');
            return 'name reserved'
        #check whether exist
        result = get_user_id(username)
        if result: #normal result a user already exist
            dprint('name taken');
            return 'name taken'
        dprint('valid name');
        return 'valid name'

    def check_local_user_auth_info(self):
        info = self.host_user_auth_info
        if not info: return None
        #info raw state should be length of 96, decrypt state should be 40
        #first 20 chars are host_pass[0:20], rest 20 chars are host_user_pass
        #dprint('raw_info = ',info,len(info))
        if ( not len(info) == 96 ):
            #dprint('raw info not in the correct form')
            return None
        info = connect_aes.decrypt( info )
        #dprint(info,len(info))
        if not len(info) == 40:
            #dprint('info not in the correct form')
            return None
        #check pass
        rhost_pass = info[0:20]
        rconn_pass = info[20:40]
        #dprint(info,len(info),rhost_pass,rconn_pass)
        count = self.cursor.execute("""select * from hostusers
        where host_mac=%s and name=%s  limit 1""",(self.host_mac,self.host_user,) )
        if count == 0:
            dprint('no host user exist')
            return None
        self.host_user_info = self.cursor.fetchone()
        ### since host info is not recored any more, just ignore it
        if not passcrypt( rconn_pass ) == self.host_user_info['connected_pass']:
            dprint('connect info not right')
            return None
        #get user_info
        count = self.cursor.execute("""select * from musers where id=%s limit 1""",(self.host_user_info['connected_user_id'],))
        if count == 0:
            raise Exception('host_user %s-%s connected to an unknown evawiz account with id = %s'%(self.host_mac,self.host_user,self.host_user_info['connected_user_id']) )
        self.user_info = self.cursor.fetchone()

        return True

    #check module owner
    def get_module_info(self,module_name):
        count = self.cursor.execute("""select * from modules where name=%s  limit 1""",( module_name ,) )
        if count == 0: return None #free module
        module_info = self.cursor.fetchone()
        version_file = "/opt/evawiz/evawiz/modules/%s/eva/__eva_version_list"%(module_name,)
        ver_list = file_content_get( version_file ).replace('\n',',').replace(' ','.')
        dprint( "version_list=",ver_list )
        module_info['version_list'] = ver_list
    
        return module_info

    def send_bytes(self,arg):
        try:
            self.request.send(b"%4d"%len(arg))
            return self.request.send(arg)
        except Exception as e:
            raise Exception("Send error occured"+str(e) )
        pass

    def recv_bytes(self,):
        try:
            mes_size = self.request.recv(4)
            while len(mes_size)<4:
                mes_size += self.request.recv( 4 - len(mes_size) )
            #print('recv bytes size=',mes_size)
            size = int( mes_size )
            res = b""
            while size > 0:
                res += self.request.recv(size)
                size -= len(res)
            return res
        except Exception as e:
            raise Exception("Send error occured:"+str(e) )
        pass

    def send(self,arg):
        if isinstance(arg,str): arg = arg.encode()
        return self.send_bytes( arg )

    def recv(self,is_bytes=False):
        res = self.recv_bytes()
        if not is_bytes: res = res.decode()
        return res
       
    def encrypt_send(self,arg):
        arg = self.aes.encrypt(arg)
        return self.send_bytes(arg)

    def encrypt_recv(self,is_bytes=False):
        res = self.recv_bytes()
        res = self.aes.decrypt( res )
        if not is_bytes: res = res.decode()
        return res
 
    def response_operation(self,oper):
        dprint("dealing operation ",oper)
        response_func = None
        if oper[0:4] == 'mod_':
            response_func = mod_operation_pairs.get( oper )
            if response_func: response_func( self )
        else:
            # response_func = self.operation_pairs.get(oper)
            # if response_func: response_func()
            pass
        if not response_func:
            print('Operation',self.operation,'is not allowed',self.mark)
            raise Exception('not allowed operation',self.mark)
        #response_func()
        pass
        
    def handle(self):
        # if not self.operation_pairs:
        #     self.operation_pairs = {
        #     }
        #     pass
        try:
            
            dprint('------------------------------------------------------------------')
            self.response_connection() #get con mac oper mark and do auth if operation is not register_user

            self.response_operation(self.operation)

            print('operation',self.operation,'from',self.mark,'done successfully')
            self.disconnect_database()
            try:
                #dprint('wait to host to cut the connection down')
                self.recv() #wait for the last terminate signal
                dprint('host connection is closed--------with last mes-------')
            except Exception as e:
                dprint('host connection is closed----------------------------')
                pass
            #time.sleep(2)
        except MySQLdb.Error as e:
            self.request.send(encoding("Internal Error %s .Please report to service@eva.run"%(line_no(),)))
            print("Finish with MySQLdb Error %d: %s" % (e.args[0], e.args[1]),self.mark)
            dtraceback()
            self.disconnect_database()
        except Exception as e:
            self.request.send(encoding("Internal Error %s .Please report to service@eva.run"%(line_no(),)))
            print('Finish with error:',e,self.mark)
            dtraceback()
            self.disconnect_database()

