from evawiz_basic import *
from mserver_basic import *
def response(handler):
#def response_list_module(self):
    (req_user,req_group) = handler.recv().split()
    dprint(req_user,req_group);
    user_id = handler.user_info['id'];
    dprint('user_id first %s'%user_id)
    if ( req_user != '#none' ):
        user_id = get_user_id(req_user);
        dprint('user_id second %s'%user_id)
        if ( not user_id ):
            handler.send("no user exist")
            return;
    #get all modules
    count = handler.cursor.execute("""select * from modules where user_id=%s""",(user_id,));
    if ( count == 0 ):
        handler.send("no modules");
        return;
    result_str = "";
    results = handler.cursor.fetchmany(count);
    dprint('try get result from fetchmany with N = %s'%count)
    for result in results:
        dprint(result)
        dprint(result['name'])
        if result['type'] == 'secret': pass
        result_str += "%s:%s.%s.%s;"%(result['name'],
                                     result['major_version'],
                                     result['minor_version'],
                                     result['revision_version'])
    dprint('result str = %s'%result_str)
    handler.send(result_str);
    return;

