from evawiz_basic import *
from mserver_basic import *
def response(handler):
#def response_delete_module(self):
    module_name = handler.recv()
    #dprint('step into delete module with module name = %s'%module_name)
    if not module_name or not re.match('[a-z][a-zA-Z0-9]{3,120}',module_name):
        raise Exception('invalid module_name recv, may from attackers')
    #dprint('step into delete module with module name = %s'%module_name)
    if module_name != 'test':
        module_info = handler.get_module_info(module_name)
        if not module_info or module_info['user_id'] != handler.user_info['id']: 
            handler.send('not permit to delete')
            #dprint('not permited to delete %s'%module_name)
            return
        #dprint('module_id = %s, module_name = %s'%(module_info['id'],module_info['name']) )

        #have perm to do delete
        #dprint('has perm to delete %s'%module_name)
        handler.cursor.execute("""select * from `modules` where id=%s """,(module_info['id'],))
        module_info = handler.cursor.fetchone()
        #dprint('module_info = %s'%module_info)
        #delete from  database
        handler.cursor.execute("""delete from `modules`
        where `modules`.`id`=%s """, (module_info['id'],) )
        handler.cursor.execute("""update musers set module_amount=module_amount-1
        where id=%s """,(handler.user_info['id'],))
        handler.conn.commit()
        #delete module dir
        module_dir = os.getenv("EVAWIZ")+'/modules/' + module_name
        #dprint('delete module dir')
        if os.path.exists(module_dir): # if exists, remove it
            cmd = "trash %s"%module_dir
            #dprint(cmd)
            shell_status_output(cmd)

    #send info of success
    handler.send('module deleted')
    #dprint('module %s deleted successfullyy'%module_name)

