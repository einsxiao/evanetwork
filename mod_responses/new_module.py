from evawiz_basic import *
from mserver_basic import *

def response(handler):
    (module_name,module_type,lang_type) = handler.recv().split()
    dprint('step into new module with %s %s %s'%(module_name,module_type,lang_type))
    if not module_name or not module_type or not lang_type:
        raise Exception('invalid module info recv, may from attackers')
    if not re.match('[a-z][a-zA-Z0-9]{3,120}',module_name):
        raise Exception('invalid module_name recv, may from attackers')
    if module_type not in ('public','private','secret'):
        raise Exception('invalid module_type recv, may from attackers')
    if lang_type not in ('c++','cuda','fortran','python','matlab','multi','eva'):
        raise Exception('invalid lang_type recv, may from attackers')
    if not module_name == 'test':
        module_info = handler.get_module_info(module_name)
        if module_info:
            dprint('module is not free')
            handler.send('module is not free')
            dprint('module_info = %s'%module_info)
            return
        handler.send('module is free')
        local_info = handler.recv()
        dprint('local_info = %s'%local_info)
    if not local_info == 'local ready':
        raise Exception('user try register new module but local not ready')

    # local ready register
    if not module_name == 'test':
        # database operation
        handler.cursor.execute("""insert into modules(name,user_id,user_name,type,lang_type)
        values(%s,%s,%s,%s,%s) """,(module_name,handler.user_info['id'],handler.user_info['name'],module_type,lang_type,) )
        handler.cursor.execute("""update musers set module_amount=module_amount+1
        where id=%s """,(handler.user_info['id'],))
        handler.conn.commit()
        #new modules dir
        module_dir = os.getenv("EVAWIZ")+'/modules/' + module_name
        dprint('new module dir')
        if os.path.exists(module_dir): # if exists, remove it
            cmd = "rm -rf %s"%module_dir
            dprint(cmd)
            shell_status_output(cmd)
            os.makedirs(module_dir)

    #send the final result
    handler.send('server ready')
    dprint('module %s created successfully'%module_name)
    return
