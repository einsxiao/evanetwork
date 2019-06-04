#!/usr/bin/env python
#coding:utf-8
################################################
## author: Xiao, Hu                           ##
## version: 1.0                               ##
## copyright: ECD                             ##
################################################
# task daemon ,  run in evawiz server         ##
################################################

from evawiz_basic import *
from SocketServer import TCPServer, ForkingMixIn, StreamRequestHandler as SRH

import MySQLdb

import db_auth

#####################
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


SetDBParas(db_auth.dbhost,db_auth.dbport,db_auth.dbuser,db_auth.dbpass,db_auth.dbdb,db_auth.dbserver)


class ActionServer:
    def connect_database(self):
        ###database initialize
        global dbhost,dbuser,dbpasswd,dbdb,dbport
        #dprint('connecting to database',dbhost)
        self.conn = MySQLdb.connect(dbhost,dbuser,dbpasswd,dbdb,dbport)
        self.cursor = self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        #dprint('connected to databse',dbhost)
        pass

    def disconnect_database(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()
        pass

    def mark_state(self,state='failed'):
        self.cursor.execute("update `evawiz_actions` set `state`=%s where `id`=%s",(state,self._id,) );
        self.conn.commit();
        pass

    def del_oper(self):
        self.cursor.execute("delete from `evawiz_actions` where `id` = %s",(self._id,) );
        self.conn.commit();
        pass

    def del_failed_all(self):
        count = self.cursor.execute("select * from `evawiz_actions` where `state` = 'failed'")
        id_list = []
        while ( count > 5 ):
            result =  self.cursor.fetchone();
            id_list.append( result['id'] )
            count -= 1;
            pass
        for _id in id_list:
            self.cursor.execute("delete from `evawiz_actions` where `id` = %s",(_id,) );
            pass
        self.conn.commit();
        pass

    def create_module_filelist(self):
        cmd = "/opt/evawiz/binsev/www_cal_module_filelist %s"%(self._args,)
        (status,output) = commands.getstatusoutput( cmd ); 
        print('status = %s,output = %s'%(status,output))
        if ( status != 0 ):
            self.mark_state( 'failed' )
        else:
            self.del_oper();
            pass
        pass

    def run_forever(self):
        self.operation_pairs = {
            'createfilelist':   		self.create_module_filelist,
        }
        while(True):
            self.connect_database()
            #print('...')
            try:
                count = self.cursor.execute("select * from `evawiz_actions` where `state` = 'pending' limit 1")
                if ( count == 0 ):
                    time.sleep(1);
                    continue
                #otherwize do actions 
                result =  self.cursor.fetchone();
                self._id = result['id']
                self._oper = result['operation']
                self._args = result['arguments']
                print('dealing operation %s with args %s'%(self._oper,self._args))
                if ( self.operation_pairs.has_key( self._oper ) ):
                    response_func = self.operation_pairs[ self._oper ];
                    response_func();
                    continue;
                print('operaton %s not found'%(self._oper))
                
            except  Exception as  e:
                print('error occured:',e)
                dtraceback();
                pass
            self.disconnect_database();
        pass


def run_action_server():
    server = ActionServer();
    server.run_forever();
    pass

def start_action_server():
    server = ActionServer();
    sd = ServerDaemon( server.run_forever,'actionserver.pid','actionserver');
    sd.start();
    pass

