import constants
import server
import ntpath
import shutil
import random
import bz2
import urllib.request
import string
import os
import subprocess

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def hostfile(filepath, filename=None):
    filepath=os.path.abspath(filepath)
    print("hosting the file %s"%filepath)
    #get a filename. this will be used for saving the file on the download end if no names are provided.
    if not filename:
        filename = path_leaf(filepath)
    #check if this is a directory or file
    if os.path.isfile(filepath):
        isDir = False
    elif os.path.isdir(filepath):
        isDir = True
    else:
        raise Exception("The supplied filepath:'%s' is not a valid file or directory" % filepath)

    #compress and save file to the tmp directory with a random name
    random_name = id_generator()
    if isDir:
        format = 'gztar'
        tmp_name = shutil.make_archive(base_name = os.path.join(constants.TMPDIR, random_name), format='gztar', root_dir=filepath)
        tmp_name = path_leaf(tmp_name)
    else:
        format = 'bz2'
        tmp_name=random_name + '.bz2'
        with open(filepath, 'rb') as input:
            with bz2.BZ2File(os.path.join(constants.TMPDIR, tmp_name), 'wb', compresslevel=9) as output:
                shutil.copyfileobj(input, output)
    #start serving files on tmp directory
    #start the server as a daemon in a separate process
    # Process(target = server.start_if_not_started).start()
    subprocess.Popen(["nohup", "python", os.path.join(constants.ROOTDIR, "server.py")])
    #we ASSUME that the server will have started by the time download peer sends a download request
    #TODO: put some wait here that release on server start so that we can be sure that peers don't hit a non-initiated server
    print("server started?")
    hostinfo={'filename':filename, 'port':constants.OUTPORT, 'uri':tmp_name, 'format':format, 'dir':isDir}
    return hostinfo

def recieve(ip, hostinfo):
    url = "http://" + ip + ":" + str(hostinfo['port']) + "/" + hostinfo['uri']
    print("retrieving from url %s"%url)
    tmp_loc = os.path.join(constants.TMPDIR, "recv_" + hostinfo['uri'])
    urllib.request.urlretrieve(url, tmp_loc)
    if hostinfo['dir']:
        shutil.unpack_archive(tmp_loc, format=hostinfo['format'], extract_dir=os.path.join(constants.DDIR, hostinfo['filename']))
    else:
        with bz2.BZ2File(tmp_loc, 'rb') as input:
            with open(os.path.join(constants.DDIR, hostinfo['filename']), 'wb') as output:
                shutil.copyfileobj(input, output)



