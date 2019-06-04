from evawiz_basic import *
from mserver_basic import *

def response(handler):
    #evawiz operations
#    def response_check_module(self):
    module_name = handler.recv()
    #mode  state:owner:version:perm
    #check state, me coworker others free
    handler.module_info = handler.get_module_info(module_name)
    if not handler.module_info: #not exist yet
        handler.send('type:notexist;')
        return
    module_type = handler.module_info['type']
    stat = {};
    stat["type"] = module_type;
    stat['owner'] = '#system';
    stat["major_version"] = handler.module_info["major_version"];
    stat["minor_version"] = handler.module_info["minor_version"];
    stat["revision_version"] = handler.module_info["revision_version"];
    stat["history_version_list"] = handler.module_info["version_list"];
    stat["perm_run"] = handler.module_info["perm_run"]
    stat["perm_src"] = handler.module_info["perm_src"]
    stat["perm_deve"] = handler.module_info["perm_deve"]
    module_owner_id = handler.module_info['user_id']
    #reserved modules
    if (module_type in ('reserve','system','lost')) or module_owner_id == 0: #return
        handler.send(packdict(stat))
        return
    if handler.module_info['user_id'] == handler.user_info['id']:
        stat['owner']='#self'
        handler.send( packdict(stat) )
        return
    #public private check perm_run and perm_deve
    count = handler.cursor.execute("""select * from musers
    where id=%s limit 1""",(module_owner_id,) )
    #owned by user itself
    if count == 0: #user_name invalid lost module
        #update modules
        count = handler.cursor.execute("""update modules
        set type='lost', user_id=0, user_name='System' type=public, perm_run=enable, perm_src=enable, perm_deve=disable
        where id=%s""",(handler.module_info['id'],) )
        handler.conn.commit()
        handler.module_info['type'] = stat['type'] = 'lost'
        handler.module_info['type'] = stat['perm_run'] = 'enable'
        handler.module_info['type'] = stat['perm_src'] = 'enable'
        handler.module_info['type'] = stat['perm_deve'] = 'disable'
        handler.send( packdict(stat) )
        return
    if module_type == 'secret':
        handler.send('type:secret;')
        return
    handler.owner_info = handler.cursor.fetchone()
    stat['owner'] = handler.owner_info['name']
    if module_type == 'public':
        handler.send( packdict(stat) )
        ###need check more info
        return
    if module_type == 'private':
        #check if module to user permision
        #mperm_user owner's module to current user
        count = handler.cursor.execute("""select * from mperm_user where module_id=%s and user_id=%s
        """,(handler.module_info['id'],handler.user_info['id'],) )
        if count > 0: # If has a perm rule, let's see
            perm_u = handler.cursor.fetchone()
            handler.module_info['perm_run'] = stat['perm_run'] = perm_u['perm_run']
            handler.module_info['perm_src'] = stat['perm_src'] = perm_u['perm_src']
            handler.module_info['perm_deve']= stat['perm_deve']= perm_u['perm_deve']
            handler.send( packdict(stat) )
            return
        else: #private and no perm info return default perm intro
            handler.send( packdict(stat) )
            return 
        #mperm_group

    #module_type_not_right
    handler.send('type:error;')
    raise Exception('Module '+module_name+' has an unknown type '+module_type)

