from evawiz_basic import *
from mserver_basic import *
def response(handler):
#def response_load_program(self):
    program_name = handler.recv();
    dprint("try load program ",program_name," from ");
    program_list = file_content_get("/opt/evawiz/programs.list").split();
    dprint(program_list);
    if ( not program_name in program_list ):
        dprint("program not exist");
        handler.send("program not exist");
        return
    dprint("program exist");
    handler.send("program exist");
    return;

