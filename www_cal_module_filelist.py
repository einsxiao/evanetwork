#!/usr/bin/env python
from evawiz_basic import *

#args: module_name version
if ( len( sys.argv ) <= 1 ):
    print("Usage: "+sys.argv[0]+" module_name [module_version]\n\n")
    exit(1)
    pass

module = sys.argv[1];
type_str = "all";
version = "";

if ( len(sys.argv) > 2 ):
    version = sys.argv[2];
    pass

print("version_str = "+version)
print("module name = ",module)
module_root = "modules/"+module;
full_module_root = "/opt/evawiz/evawiz/"+module_root;
branch = 'eva';
ev = EvaVersion( full_module_root, branch, branch );
print(ev)

os.chdir( ev.branch_dir );

in_ver = get_version_from_string( version )
print("in_ver = ", in_ver)

if ( in_ver != None ):
    version =in_ver 
else:
    version = ev.get_current_version()
    pass

print('current ver = ',ev.get_current_version())
filelist_path = full_module_root+"/"+branch+"/__filelist.%s.%s.%s"%(version[0],version[1],version[2])
if ( os.path.exists( filelist_path ) ):
    print(filelist_path)
    exit(0);

file_tree = "";
filelist = "";
def make_file_tree_html(tree,ind=0,depth=0,enable_wrap = True):
    global filelist
    root_dir =  tree[ind];
    parent = root_dir[0];
    if ( parent != "" ): parent += '/';
    cur_dir = module_root+"/"+parent;
    out = "";
    #out+= """<div style ='margin-left:"""+str(20)+"""px;'>""";

    for dirname in root_dir[1]:
        for i in range(0,len(tree)):
            if ( tree[i][0] ==  parent + dirname ):
                out+="""<div class='dirtree_catogery_div_inner'> <div class='dirtree_catogery_head' style='padding-left:"""+str((depth+1)*20)+"""px'>"""+dirname+"""<button class ='dirtree_catogery_button' href='#' onclick=\"openShutManager(this,'"""+cur_dir+""".__dirtree_box"""+str(i)+"""',true,'-','+')\">+</button> </div><div id='"""+cur_dir+""".__dirtree_box"""+str(i)+"""' style='display:none' class='dirtree_box'> """
                out += make_file_tree_html( tree, i, depth+1 );
                out +="""</div></div>""";
            pass
        pass
    count = 2;
    for filename in root_dir[2]:
        if ( filename[0] != '%' ): continue
        filename = filename.split('%')[1];
        filelist += cur_dir+filename + "\n";
        if ( str_end_with(filename,'.so') ): continue
        if ( str_end_with(filename,'.o') ): continue
        if ( str_end_with(filename,'.tmp') ): continue
        if ( str_end_with(filename,'~') ): continue
        if ( parent == 'doc/' and not str_end_with(filename,'.art' ) ): continue
        count = 3-count;
        out += """<div class='filelist_item%s' style='padding-left:%spx'><ui id='%s_ui_item' ><a href = '#' class='filelist_ui_item_href' onclick="navilist_to_cate('','%s'); return false;" >%s</a></ui></div>"""%(count,(depth+1)*20,cur_dir + filename,cur_dir + filename, filename );
        pass

    #out+="""</div>""";
    return out;

#we can directly output html code here
filelist="";
file_tree = ev.get_file_tree_of_version( version )
#print(file_tree)
html="""<ul id='module_filelist_box' class='module_filelist_ui_box'>"""
html+=make_file_tree_html(file_tree)
html+="""</ul>"""
html+="!!!!!!!!!!\n"+filelist+"!!!!!!!!!!"

filelist="";
file_tree = ev.get_runfile_of_version( version,'runfile' )
#print(file_tree)
html+="""<ul id='module_filelist_box' class='module_filelist_ui_box'>"""
html+=make_file_tree_html(file_tree)
html+="""</ul>"""
html+="!!!!!!!!!!\n"+filelist+"!!!!!!!!!!"


filelist="";
file_tree = ev.get_runfile_of_version( version,'introfile' )
#print(file_tree)
html+="""<ul id='module_filelist_box' class='module_filelist_ui_box'>"""
html+=make_file_tree_html(file_tree)
html+="""</ul>"""
html+="!!!!!!!!!!\n"+filelist;

file_content_set( filelist_path, html );
print(filelist_path)
exit(0)
