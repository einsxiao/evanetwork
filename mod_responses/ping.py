from evawiz_basic import *

def response(handler):
    dprint("ping response",handler.mark)
    req = handler.recv()
    dprint("req = ",req)
    handler.send("I'm here!")
    pass
