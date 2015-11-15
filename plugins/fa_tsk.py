"""
Parses image using Sleuth Kit
"""

from yapsy.IPlugin import IPlugin
import pytsk3
import os
from PIL import Image

class FaTsk(IPlugin):

    def __init__(self):
        IPlugin.__init__(self)

    def activate(self):
        IPlugin.activate(self)
        return

    def deactivate(self):
        IPlugin.deactivate(self)
        return

    def display_name(self):
        """Returns the name displayed in the webview"""
        return "Sleuth Kit"

    def check(self, curr_file, path_on_disk, mimetype, size):
        """Checks if the file is compatable with this plugin"""
        return True

    def mimetype(self, mimetype):
        """Returns the mimetype of this plugins get command"""
        return "text/plain"

    def popularity(self):
        """Returns the popularity which is used to order the apps from 1 (low) to 10 (high), default is 5"""
        return 5

    def get(self, curr_file, db_util, path_on_disk, mimetype, size, address, port, request_query):
        offset = request_query['offset']
        path = request_query['path']
        image_id = request_query['image_id']
        self.add_image(image_Id, offset, path, db_util)
        return '<xmp style="white-space: pre-wrap;">DONE</xmp>'
    
    def add_image(self, image_id, offset, image_path, db_util):
        """Creates a file listing of the partition at the provided image and offset in the database"""
        image_path = "/" + image_path

        #TODO ADD Error Handling
        #if database._image_id[image_id] and database._image_id[image_id][0]["path"] != str(image_path):
        #    logging.error("Image ID '" + image_id + "' already in use")
        #    abort(400, "That Image ID is already in use by an image with a different path")
        #if database._id[image_id + "/" + offset]:
        #    logging.error("Image '" + image_id + "' with offset '" + offset + "' already exists")
        #    abort(400, "Database already contains an image with that ID and offset")
        if not os.path.isfile(image_path):
            logging.error("Could not find file at path '" + str(image_path) + "'")
            abort(400, "Could not find file at specified path '" + str(image_path) + "'")
            
        logging.info("Adding image to databse")
        
        try:
            image = pytsk3.Img_Info(url=image_path)
            file_system = pytsk3.FS_Info(image, offset=(int(offset)*512))
            index_name = 'efetch_timeline_' + image_id
            db_util.create_index(index_name)
            db_util.bulk(load_database(file_system, image_id, offset, image_path, index_name, "/"))
        except Exception as error:
            logging.error(error.message)
            logging.error("Failed to parse image '" + image_path + "' at offset '" + offset + "'")
            abort(500, "Failed to parse image, please check your sector offset")

    def icat(curr_file, output_file_path):
        """Returns the specified file using image file, meta or inode address, and outputfile"""
        out = open(output_file_path, 'wb')
        img = pytsk3.Img_Info(curr_file['image_path'])
        fs = pytsk3.FS_Info(img, offset=(int(curr_file['offset'])*512))
        try:
            f = fs.open_meta(inode = int(curr_file['inode'].split('-')[0]))
        except:
            logging.warn("Failed to cache file, most likey file is reallocated " + output_file_path)
            return
        file_offset = 0
        size = f.info.meta.size
        BUFF_SIZE = 1024 * 1024
        while file_offset < size:
            available_to_read = min(BUFF_SIZE, size - file_offset)
            data = f.read_random(file_offset, available_to_read)
            if not data: break
            file_offset += len(data)
            out.write(data)
            out.close()

    def cache_file(curr_file, create_thumbnail=True):
        """Caches the provided file and returns the files cached directory"""
        if curr_file['file_type'] == 'directory':
            return

        #TODO: Not everything will have an iid... so need to figure that out
        file_cache_path = output_dir + 'files/' + curr_file['iid'] + '/' + curr_file['name']
        file_cache_dir = output_dir + 'files/' + curr_file['iid'] + '/'
        thumbnail_cache_path = output_dir + 'thumbnails/' + curr_file['iid'] + '/' + curr_file['name']
        thumbnail_cache_dir = output_dir + 'thumbnails/' + curr_file['iid'] + '/'

        #Makesure cache directories exist 
        if not os.path.isdir(thumbnail_cache_dir):
            os.makedirs(thumbnail_cache_dir)
        if not os.path.isdir(file_cache_dir):
            os.makedirs(file_cache_dir)

        #If file does not exist cat it to directory
        if not os.path.isfile(file_cache_path):
            icat(curr_file['offset'], curr_file['image_path'], curr_file['inode'], file_cache_path)

        #Uses extension to determine if it should create a thumbnail
        assumed_mimetype = helper.guess_mimetype(str(curr_file['ext']).lower())

        #If the file is an image create a thumbnail
        if assumed_mimetype.startswith('image') and create_thumbnail and not os.path.isfile(thumbnail_cache_path):
            try:
                image = Image.open(file_cache_path)
                image.thumbnail("42x42")
                image.save(thumbnail_cache_path)
            except IOError:
                logging.warn("Failed to create thumbnail for " + curr_file['name'] + " at cached path " + file_cache_path)

        return file_cache_path

    def load_database(fs, image_id, offset, image_path, index_name, directory):
        json = []

        for directory_entry in fs.open_dir(directory):
            name =  directory_entry.info.name.name.decode("utf8")
            if directory_entry.info.meta == None:
                file_type = ''
                inode = ''
                mod = ''
                acc = ''
                chg = ''
                cre = ''
                size = ''
                uid = ''
                gid = ''
            else:
                file_type = directory_entry.info.meta.type
                inode = str(directory_entry.info.meta.addr)
                mod = str(directory_entry.info.meta.mtime)
                acc = str(directory_entry.info.meta.atime)
                chg = str(directory_entry.info.meta.ctime)
                cre = str(directory_entry.info.meta.crtime)
                size = str(directory_entry.info.meta.size)
                uid = str(directory_entry.info.meta.uid)
                gid = str(directory_entry.info.meta.gid)

            dir_ref = image_id + "/" + offset + directory + name
            inode_ref = image_id + "/" + offset + "/" + inode
            ext = os.path.splitext(name)[1][1:] or ""

            if file_type == pytsk3.TSK_FS_META_TYPE_REG:
                file_type_str = 'regular'
            elif file_type == pytsk3.TSK_FS_META_TYPE_DIR:
                file_type_str = 'directory'
            elif file_type == pytsk3.TSK_FS_META_TYPE_LNK:
                file_type_str = 'link'
            else:
                file_type_str = str(file_type)

            modtime = long(mod) if mod else 0
            acctime = long(acc) if acc else 0
            chgtime = long(chg) if chg else 0
            cretime = long(cre) if cre else 0

            meta_event = {
                    '_index': index_name,
                    '_type' : 'event',
                    '_id' : dir_ref,
                    '_source' : {
                        'id' : image_id + "/" + offset,
                        'pid' : dir_ref,
                        'iid' : inode_ref,
                        'image_id': image_id,
                        'offset' : offset,
                        'image_path' : image_path,
                        'name' : name,
                        'path' : directory + name,
                        'ext' : ext,
                        'dir' : directory,
                        'file_type' : file_type_str,
                        'inode' : inode,
                        'mod' : modtime,
                        'acc' : acctime,
                        'chg' : chgtime,
                        'cre' : cretime,
                        'size' : size,
                        'uid' : uid,
                        'gid' : gid,
                        'thumbnail' : "http://" + address + ":" + port + "/thumbnail/" + image_id + "/" + offset + "/p" + directory + name,
                        'analyze' : "http://" + address + ":" + port + "/analyze/" + image_id + "/" + offset + "/p" + directory + name,
                        'parser' : "fa_tsk"
                    }
            }

            json.append(meta_event)

            if file_type == pytsk3.TSK_FS_META_TYPE_DIR and name != "." and name != "..":
                try:
                    json.append(load_database(fs, image_id, offset, image_path, db, directory + name + "/"))
                except Exception as error:
                    logging.warn("[WARNING] - Failed to parse directory " + directory + name + "/")

            return json
