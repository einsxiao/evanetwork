from evawiz_basic import *
from mserver_basic import *
def response(handler):
#def response_download_module_to_user(self):
    #user side will check the module info first
    #handler.response_check_module()
    handler.response_operation('mod_check_module')
    if not handler.module_info: return None
    module_name = handler.module_info['name']
    dprint('module_info=',handler.module_info)
    dprint('user_info = ',handler.user_info)
    if handler.module_info['user_id'] == 0:
        handler.send('System integrated modules no need to download.')

    if handler.module_info['user_id'] ==  handler.user_info['id']: #user own module download
        dprint('%s download own module %s'%(handler.user_info['name'],module_name))
        version_str = handler.recv()
        if version_str == 'do nothing': return
        dprint('version string = %s'%version_str)
        module_dir = os.getenv("EVAWIZ")+'/modules/' + module_name
        ev = EvaVersion(module_dir,'eva','eva')
        if ( version_str == 'newest' ):
            version = ev.get_actual_version_from_string(version_str)
        elif ( str_start_with(version_str,"update") ):
            version_exist = get_version_from_string( version_str.split()[1] )
            version = ev.get_current_version();
            dprint("version check local:%s server:%s"%(version_exist,version))
            if (version_exist == version):
                handler.send("module is newest already")
                return
            elif ( version_exist > version ):
                handler.send("local module is newer than server version")
                return
        elif str_start_with(version_str,"download"):
            version_exist = get_version_from_string( version_str.split()[1] )
            version = ev.get_current_version();
            dprint("version check local:%s server:%s"%(version_exist,version))
            if (version_exist == version):
                handler.send("module is newest already")
                return
            elif ( version_exist > version ):
                handler.send("local module is newer than server version")
                return
        else:
            dprint("try get actual version from string")
            version = ev.get_actual_version_from_string(version_str)
        dprint('download version is',version)
        if not version:
            handler.send('module of required version is not available')
            return
        handler.send('ready_to_download %s.%s.%s'%(version[0],version[1],version[2]))
        file_tree = ev.get_file_tree_of_version(version)
        #send the version
        reply_info = handler.recv()
        if reply_info != 'start to download': raise Exception('download rule not followed')
        ev.send_module(ev.branch_dir,file_tree,'eva2normal',handler.send,handler.recv,handler.send_eof)
        handler.send('download complete')
        return

    else: #check perm to decide what to do
        dprint('download request but not own module')
        if handler.module_info['perm_src'] == 'enable':
            dprint('%s download src of %s'%(handler.user_info['name'],module_name))
            version_str = handler.recv()
            if version_str == 'do nothing': return
            dprint('version string = %s'%version_str)
            module_dir = os.getenv("EVAWIZ")+'/modules/' + module_name
            ev = EvaVersion(module_dir,'eva','eva')
            if ( version_str == 'newest' ):
                version = ev.get_actual_version_from_string(version_str)
            elif ( str_start_with(version_str,"update") ):
                version_exist = get_version_from_string( version_str.split()[1] )
                version = ev.get_current_version();
                dprint("version check local:%s server:%s"%(version_exist,version))
                if (version_exist == version):
                    handler.send("module is newest already")
                    return
                elif ( version_exist > version ):
                    handler.send("local module is newer than server version")
                    return
            elif str_start_with(version_str,"download"):
                version_exist = get_version_from_string( version_str.split()[1] )
                version = ev.get_current_version();
                dprint("version check local:%s server:%s"%(version_exist,version))
                if (version_exist == version):
                    handler.send("module is newest already")
                    return
                elif ( version_exist > version ):
                    handler.send("local module is newer than server version")
                    return
            else:
                version = ev.get_actual_version_from_string(version_str)

            dprint('download version is',version)
            if not version:
                handler.send('module of required version is not available')
                return
            if version[0] == 0:
                handler.send('module has no available code.')
                return
            handler.send('ready_to_download %s.%s.%s'%(version[0],version[1],version[2]))
            file_tree = ev.get_file_tree_of_version(version)
            dprint("file_tree:",file_tree);
            #send the version
            reply_info = handler.recv()
            if reply_info != 'start to download': raise Exception('download rule not followed')
            ev.send_module(ev.branch_dir,file_tree,'eva2normal',handler.send,handler.recv,handler.send_eof)
            handler.send('download complete')
            return

        elif handler.module_info['perm_run'] == 'enable':
            dprint('%s download runfile of module %s'%(handler.user_info['name'],module_name))
            version_str = handler.recv()
            if version_str == 'do nothing': return
            dprint('version string = %s'%version_str)
            module_dir = os.getenv("EVAWIZ")+'/modules/' + module_name
            ev = EvaVersion(module_dir,'eva','eva')
            if ( version_str == 'newest' ):
                version = ev.get_actual_version_from_string(version_str)
            elif ( str_start_with(version_str,"update") ):
                version_exist = get_version_from_string( version_str.split()[1] )
                version = ev.get_current_version();
                dprint("version check local:%s server:%s"%(version_exist,version))
                if (version_exist == version):
                    handler.send("module is newest already")
                    return
                elif ( version_exist > version ):
                    handler.send("local module is newer than server version")
                    return
            elif str_start_with(version_str,"download"):
                version_exist = get_version_from_string( version_str.split()[1] )
                version = ev.get_current_version();
                dprint("version check local:%s server:%s"%(version_exist,version))
                if (version_exist == version):
                    handler.send("module is newest already")
                    return
                elif ( version_exist > version ):
                    handler.send("local module is newer than server version")
                    return
            else:
                version = ev.get_actual_version_from_string(version_str)
            dprint('download version is',version)
            if not version:
                handler.send('module of required version is not available')
                return
            if version[0] == 0:
                handler.send('module has no available code.')
                return
            handler.send('ready_to_download %s.%s.%s'%(version[0],version[1],version[2]))
            file_tree = ev.get_runfile_of_version(version)
            dprint("runfile_list:",file_tree);
            #send the version
            reply_info = handler.recv()
            if reply_info != 'start to download': raise Exception('download rule not followed')
            ev.send_module(ev.branch_dir,file_tree,'eva2normal',handler.send,handler.recv,handler.send_eof)
            handler.send('download complete')
            return
        else: #no permission to download anything
            #handler.recv()
            #handler.send("not permit to download")
            return
        pass
    pass


