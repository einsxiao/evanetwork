from evawiz_basic import *
from mserver_basic import *
def response(handler):
#def response_upload_module(self):
    (module_name)=handler.recv()
    #dprint('step into upload_module with module %s'%module_name)
    if module_name == 'test':
        raise Exception('upload module test, may from attackers')
    module_info = handler.get_module_info(module_name)
    if not module_info or module_info['user_id'] != handler.user_info['id']: 
        handler.send('not permit to upload')
        #dprint('not permited to upload %s'%module_name)
        return
    #dprint('module_id = %s, module_name = %s'%(module_info['id'],module_info['name']) )
    #permit to upload
    #detemine the new version
    #send recent version
    version = [int(module_info['major_version']),int(module_info['minor_version']), int(module_info['revision_version']) ]
    handler.send('%s %s %s'%(version[0],version[1],version[2]) )

    module_dir = os.getenv("EVAWIZ")+'/modules/' + module_name
    recv_info = handler.recv()
    if recv_info == 'local repos not ready':
        handler.send_eof()
        raise Exception('user not ready to do upload module operation')
    new_version = list(map(int,recv_info.split()))
    if len(new_version) != 3: raise Exception('uploadmodule local rule not followed')
    dprint('local want version:',new_version) 
    dprint('current version:',version) 
    if new_version <= version: raise Exception('uploadmodule local new version wrong')
    handler.send('server ready')
    #dprint('updating to new_version',new_version)

    old_suffix =".%s.%s.%s"%(version[0],version[1],version[2])
    full_suffix=".%s.%s.%s"%(new_version[0],new_version[1],new_version[2])
    ev = EvaVersion(module_dir,'eva','eva')
    cwd = os.getcwd()
    os.chdir(ev.branch_dir)

    #recv files
    #dprint('recv the branch')
    if not ev.recv_module(ev.branch_dir,'normal2eva',full_suffix,old_suffix,handler.send,handler.recv):
        handler.send_eof();
        return 
    #update database info and version file info
    handler.cursor.execute(""" update modules
    set major_version=%s, minor_version=%s, revision_version=%s
    where id=%s """,(new_version[0],new_version[1],new_version[2],module_info['id'],))
    handler.conn.commit()
    ver_str = '%s %s %s'%(new_version[0],new_version[1],new_version[2])
    dprint("renew version %s to version_file in dir %s"%(ver_str,ev.version_file) );
    file_content_append(ev.version_file,'%s\n'%ver_str)
    dprint('upload over. send final info to user')
    reply_info = handler.recv()
    handler.send(ver_str)
    #update web filelist part
    cmd = "/opt/evawiz/binsev/www_cal_module_filelist %s"%(module_name,)
    (status,output) = shell_status_output( cmd ); 
    if ( status != 0 ):
        log('module_filelist',"Create file list for %s %s failed"%(module_name,full_suffix,))
        pass
    pass

