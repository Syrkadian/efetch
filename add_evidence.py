from bottle import abort
from efetch import EfetchHelper
from efetch import DfvfsUtil
import os
import logging
import sys
import getopt

def main(argv):
    global all_settings
    all_settings = False

    try: 
        opts, args = getopt.getopt(argv, "hAi:n:d", ["help", "ALL", "image=", "name=", "debug"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    #MOVE DIRS TO HELPER (NOT CURR & OUTPUT)
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = curr_dir + "/cache/"
    upload_dir = curr_dir + "/uploads/"
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    image_path = ''
    image_id = ''
    max_download_size = 500

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-A", "--ALL"):
            all_settings = True        
        elif opt in ("-i", "--image"):
            image_path = str(arg)
        elif opt in ("-n", "--name"):
            image_id = str(arg).lower()
        elif opt in ('-d', "--debug"):
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.error("Unknown argument " + opt)
            usage()
            sys.exit(2)
    
    if not image_path:
        logging.error('Image and Image ID (name) are required')
        usage()
        sys.exit(2)
    if not image_id:
        logging.error('Image and Image ID (name) are required')
        usage()
        sys.exit(2)

    if not output_dir.endswith("/"):
        output_dir = output_dir + "/"
    if not os.path.isdir(output_dir):
        logging.error("Could not find output directory " + output_dir)
        sys.exit(2)

    #Initialize utils
    helper = EfetchHelper(curr_dir, output_dir, upload_dir, max_download_size * 1000000)
    test = helper.db_util
    manager = helper.plugin_manager

    settings = []

    while not add_image(image_id, image_path, helper.db_util, settings):
        new_setting = raw_input('Option: ')
        if str(new_setting).strip().lower() in options:
            settings.append(str(new_setting).strip())
        else:
            print("ERROR: Must be option in " + str(options))

def add_image(image_id, image_path, db_util, settings):
    """Creates a file listing of the partition at the provided image in the database"""
    global all_settings

    if not str(image_path).startswith("/"):
        image_path = "/" + image_path

    if not os.path.isfile(image_path):
        logging.error("Could not find file at path '" + str(image_path) + "'")
        abort(400, "Could not find file at specified path '" + str(image_path) + "'")

    logging.info("Adding " + str(image_id) + " to Elastic Search using dfVFS driver")

    if settings:
        new_settings = list(settings)
    else:
        new_settings = []

    dfvfs_util = DfvfsUtil(image_path, new_settings, False)

    if dfvfs_util.initialized < 1 and all_settings:
        for option in dfvfs_util.options:
            add_image(image_id, image_path, db_util, settings + [ option ])
        return True
    elif dfvfs_util.initialized < 1:
        print(dfvfs_util.display)
        global options 
        options = dfvfs_util.options
        return False

    index_name = 'efetch-evidence_' + image_id
    db_util.create_index(index_name)
    root = {
                '_index': index_name,
                '_type' : 'event',
                '_id' : image_id,
                '_source' : {
                    'parser': 'efetch',
                    'pid' : image_id,
                    'iid' : image_id + '/',
                    'image_id': image_id,
                    'image_path' : image_path,
                    'name' : image_id,
                    'path' : image_id,
                    'ext' : '',
                    'dir' : '/',
                    'meta_type' : 'Directory',
                    'inode' : '',
                    'mtime' : '',
                    'atime' : '',
                    'ctime' : '',
                    'crtime' : '',
                    'file_size' : [0],
                    'uid' : '',
                    'gid' : '',
                    'driver' : "fa_dfvfs"
                }
        }

    json = []
    json.append(root)
    
    curr_id = image_id
    prev_id = image_id
    curr_path = '/'

    for setting in settings:
        print("Setting found: " + setting)
        if setting.lower() != 'none':
            curr_id += '/' + setting
            json.append({
                    '_index': index_name,
                    '_type' : 'event',
                    '_id' : curr_id,
                    '_source' : {
                        'parser': 'efetch',
                        'pid' : curr_id,
                        'iid' : curr_id + '/',
                        'image_id': image_id,
                        'image_path' : image_path,
                        'name' : setting,
                        'path' : curr_id,
                        'ext' : '',
                        'dir' : prev_id + '/',
                        'meta_type' : 'Directory',
                        'inode' : '',
                        'mtime' : '',
                        'atime' : '',
                        'ctime' : '',
                        'crtime' : '',
                        'file_size' : [0],
                        'uid' : '',
                        'gid' : '',
                        'driver' : "fa_dfvfs"
                    }
            })
            prev_id = curr_id

    json += dfvfs_util.GetJson(image_id, curr_id + "/TSK", image_path)
    db_util.bulk(json)

    return True

def usage():
    print("usage: add_evidence.py [-h] [-d] [-i IMAGE] [-n NAME]")
    print("optional arguments:")
    print("  -h, --help         shows this help message and exits")
    print("  -i, --image        required path to the image to use")
    print("  -n, --name         required image id")
    print("  -d, --debug        displays debug output")
    print("")

if __name__=="__main__":
    main(sys.argv[1:])