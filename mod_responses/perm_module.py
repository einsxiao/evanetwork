from evawiz_basic import *
from mserver_basic import *
def response(handler):
#def response_perm_module(self):
    ##################################################
    #### response the check module and get module info
    #handler.response_check_module()
    handler.response_operation('mod_check_module')

    if not handler.module_info: return # cut directly
    module_name = handler.module_info['name']
    if handler.module_info['user_id'] != handler.user_info['id']:
        dprint('no permission to permit module %s.'%module_name)
        return # cut directly
    ##################################################
    (to_user,to_group,perm_str,version) = handler.recv().split()

    ###check perm_str
    for ch in perm_str:
        if not ch in ('i','r','s','d'):
            raise Exception("perm_module operation rule not followed.");
    ###########
    d_perm = "disable"
    i_perm = "disable"
    r_perm = "disable"
    s_perm = "disable"
    if  'i' in perm_str:
        i_perm = "enable"

    if  'r' in perm_str:
        i_perm = "enable" 
        r_perm = "enable"

    if  's' in perm_str:
        i_perm = "enable"
        r_perm = "enable"
        s_perm = "enable"

    if  'd' in perm_str:
        i_perm = "enable"
        r_perm = "enable"
        s_perm = "enable"
        d_perm = "enable"
    ############################
    if i_perm == 'disable':
        handler.send("perm string false");
        return

    if (to_user == handler.user_info['name']) or (to_user == 'All') or (to_user == 'all'):
        m_type = 'secret'
        if ( i_perm == "enable"  ): m_type = 'private'
        if ( r_perm == "enable"  ): m_type = 'public'
        handler.cursor.execute(""" update modules
        set type=%s, perm_run=%s, perm_src=%s, perm_deve=%s 
        where id=%s """,(m_type, r_perm, s_perm, d_perm,handler.module_info['id'],))
        handler.conn.commit()
        handler.send("perm ok")
        return

    ####check version
    module_dir = os.getenv("EVAWIZ")+'/modules/' + module_name
    ev = EvaVersion(module_dir,'eva','eva')
    versions = ev.get_actual_version_from_string(version)
    if not versions:
        handler.send("version not ok");
        return 
    else:
        if version == '0' or version == 'newest':
            v_perm =  '0';
        else:
            v_perm = versions[0]
    ###############################
    ####check to_user
    if (to_user == "#none" and to_group == "#none"):
        raise Exception("rule not followed while perm_module")
    print(to_user,to_group,handler.user_info['name'])
    user_id = None
    if ( to_user != "#none" ):
        user_id = get_user_id( to_user );
        if not user_id:
            handler.send("user not exist");
            return
    ###check to_group
    group_id = None
    if to_group != "#none":
        count = handler.cursor.execute("""select * from mgroups where name=%s  """,(to_group,) )
        if count == 0:
            handler.send("group not exist");
            return;
        result = handler.cursor.fetchone()
        group_id = result['id']
        pass

    ##################################
    if not user_id and not group_id:
        handler.send("no user or group exist");
        return

    if user_id:
        dprint(handler.module_info['id'],user_id,r_perm,s_perm,d_perm,v_perm,)
        handler.cursor.execute("""
        insert into mperm_user
        (module_id,user_id,perm_run,perm_src,perm_deve,perm_version)
        values (%s,%s,%s,%s,%s,%s)
        on duplicate key update
        perm_run=values(perm_run),
        perm_src=values(perm_src),
        perm_deve=values(perm_deve),
        perm_version=values(perm_version)
        """,(handler.module_info['id'],user_id,r_perm,s_perm,d_perm,v_perm,) );
        pass
    if group_id:
        handler.cursor.execute("""
        insert into mperm_group
        (module_id,group_id,perm_intro,perm_run,perm_src,perm_deve,perm_version)
        values
        (%s,%s,%s,%s,%s,%s,%s)
        on duplicate key update
        perm_intro=values(perm_intro),
        perm_run=values(perm_run),
        perm_src=values(perm_src),
        perm_deve=values(perm_deve),
        perm_version=values(perm_version)
        """,(handler.module_info['id'],group_id,i_perm,r_perm,s_perm,d_perm,v_perm,) );
        pass
    handler.conn.commit();
    handler.send("perm ok");
    return

