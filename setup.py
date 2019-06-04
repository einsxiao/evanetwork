#!/usr/bin/env python3
import os
import compileall
import sys

#debug = False
debug = True
server_address='eva.run'
version='dev'
#change to release mode

if len(sys.argv) > 1:
    debug = False
    print('set to release version')
    version = sys.argv[1];
    server_address = 'eva.run'
    pass

src_dir = '/opt/evawiz/evanetwork'

def deal1(pycodes_dir,files):
    print("deal %s"%pycodes_dir)
    os.chdir(src_dir)
    for f in files:
        os.system("cp -rf {0} {1}/".format(f,pycodes_dir) )
        pass
    os.chdir(pycodes_dir)
    pass

def deal2():
    compileall.compile_dir("./")
    os.system("rm ./*.py")
    for sf in os.listdir("__pycache__"):
        if sf.endswith(".pyc"):
            name = sf[:-15]
            os.system("mv __pycache__/{0} {1}.pyc".format(sf,name) )
            pass
        pass
    pass
    

#basic
deal1('/opt/evawiz/pymods',['evawiz_basic.py'])

os.system("sed -i \"s/__debug =.*$/__debug = {0}/\" evawiz_basic.py".format(debug) )
deal2()


#tsusy server side
deal1('/opt/evawiz/tsusyd',
      ["tsusyrun","tsusyshow","tsusylist","tsusyd","tsusyd.py","mserver_basic.py","mserver.py","cert.pem","key.pem","auth-expect","passwd-expect","actiond","actiond.py","actionserver.py","www_cal_module_filelist","www_cal_module_filelist.py","mod_responses"])
deal2()

os.chdir('/opt/evawiz/tsusyd/mod_responses')
deal2()

#tsusy server side
deal1('/opt/evawiz/auth/tsusyd',['db_auth.py'])
deal2()


#host and user side
deal1('/opt/evawiz/evawizd',["eva","eva.py","muser.py","eva-path.py","mod_requests"])
os.system("cp ~/evanetwork/eva-path ~/bin/")
os.system("""sed -i "s/__VERSION/%s/" eva.py """%(version) )
deal2()

os.chdir('/opt/evawiz/evawizd/mod_requests')
deal2()

#programs list
os.system("ls ~/programs/ >~/programs.list")


