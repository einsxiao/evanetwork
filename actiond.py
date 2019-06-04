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
import actionserver



def help_info():
    print("""Usage: actionserver [operation] [operants]
    run action server or do operation on server
Operations:
    run
        run eva server directly

    start
        start eva server daemon

    restart
        restart eva server daemon

    status
        check the status of the eva server daemon

    help
        show this help information
    """)
    pass

    #check the argument to decide what to do
if len(sys.argv) == 1:
    print("use -h|--help|help for more information\n")
    exit(0)
else: #server operation
    # daemon server
    try:
        operation = sys.argv[1]
        if operation == 'help' or operation == '-h' or operation == '--help':
            help_info()
            exit(0)
        if operation == 'run':
            actionserver.run_action_server()
            exit(0)
        if operation == 'start':
            actionserver.start_action_server()
            print('operation finished.')
            exit(0)
        if operation == 'stop':
            sd = ServerDaemon(None,"actionserver.pid","actionserver")
            sd.stop()
            print('operation finished.')
            exit(0)
        if operation == 'restart':
            sd = ServerDaemon(None,"actionserver.pid","actionserver")
            sd.stop()
            actionserver.start_action_server()
            exit(0)
        if operation == 'status':
            sd = ServerDaemon(None,"actionserver.pid","actionserver")
            sd.status()
            exit(0)
        print("Error: unknown operation '"+sys.argv[1]+"'")
        
    except Exception as e:
        print("server operation exist with error:",e)
        dtraceback()
