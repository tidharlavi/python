'''
Created on Dec 16, 2017

@author: eliad
'''

import os
from shutil import copyfile

# get exception info
import sys 
import traceback

# Local lib
import common

class Loader(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        
        self.stats = common.Stats()
        
        if "es" in params:
            self.es = params["es"]
        else:
            raise TypeError('\`es\' (elastic search) should be available in input params')
        
        self.ses = params.get("ses")
        if not self.ses:
            raise TypeError('\'ses\' (signature elastic search DB) should be available in input params')
        
        if "dest_folder" in params:
            self.dest_folder = params["dest_folder"]
        else:
            self.dest_folder = "/home/eliad/python/image_crawler/images_sig_db/"
       
        
    def load_image_details_array(self, image_details_arr):
        for img_dtl in image_details_arr:
            self.load_image_details(img_dtl)
                
                
    def load_image_details(self, img_dtl):
        try:
            #print ', '.join("%s: %s" % img_dtl for img_dtl in vars(img_dtl).items())
            
            # Check if img is on DB
            res = self.ses.search_image(img_dtl.path, True)
            
            # check if we have a perfect match
            found_rec = None
            for rec in res:
                #print(rec["dist"])
                if rec["dist"] == 0.0:
                    found_rec = rec
                    break
            
            if found_rec is not None:
                # image already in DB lets add image detail/s
                self.stats.Incr("exist_image")
                
                # Check if we alreay got this image from this url
                found_details = False
                for img_dtl_db in found_rec["metadata"]["details"]:
                    if img_dtl_db["page_src_url"] == img_dtl.page_src_url:
                        img_dtl_db["time_last"] = img_dtl.time
                        img_dtl_db["cnt"] = img_dtl_db["cnt"] + 1
                        found_details = True
                        break
                
                if not found_details:
                    found_rec["metadata"]["details"].append(common.to_dict(img_dtl))
                    found_rec["metadata"]["web_page_info"].append(img_dtl.web_page_info)
                
                rec_id=found_rec["id"]
                index='images'
                doc_type='image'
                doc = { "metadata" : found_rec["metadata"] }
                self.es.update(index=index, doc_type=doc_type, id=rec_id, body={ 'doc': doc })
                
            else:
                self.stats.Incr("new_image")
                
                filename_move = self.dest_folder + img_dtl.id + "." + img_dtl.extension
                
                metadata = dict()
                img_dtl.cnt = 1
                img_dtl.path_sig_db = filename_move
                metadata["details"] = [ common.to_dict(img_dtl) ] 
                metadata["web_page_info"] = [ img_dtl.web_page_info ]
                self.ses.add_image(img_dtl.path, None, False, metadata, False, img_dtl.id)
                
                # WA to get doc id
#                 res = self.ses.search_image(img_dtl.path, True)
#                 found_rec = None
#                 for rec in res:
#                     #print(rec["dist"])
#                     if rec["dist"] == 0.0:
#                         found_rec = rec
#                         break
#                     
#                 if found_rec is None:
#                     self.stats.Incr("error_image_added_not_found")
#                     return
                
                # move (currently copy) file from his folder
                if not os.path.exists(filename_move):
                    #os.rename(img_dtl.path , filename_move)
                    copyfile(img_dtl.path , filename_move)
                    
        except Exception as e: 
            print("Exception in to load  '"+img_dtl.path+"' to DB.")
            print("Exception: type '",sys.exc_info()[0],"', message '",e,"'")
            traceback.print_exc()
            self.stats.Incr("exception_in_loader")
        
