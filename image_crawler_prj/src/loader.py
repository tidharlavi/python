'''
Created on Dec 16, 2017

@author: eliad
'''

import os
from shutil import copyfile
import json 

# get exception info
import sys 
import traceback

# Local lib
import common

# Image match
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES


class Loader(object):
    '''
    classdocs
    '''
    
    # Class varibels 
    es = None
    ses = None
        
    # Constat
    ES_INDEX = 'images'
    ES_DOC_TYPE = 'image'


    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        
        self.stats = common.Stats()
        
        if self.es is None:
            self.es = Elasticsearch()
            
        if self.ses is None:
            self.ses = SignatureES(self.es)
            
        # Check if index exist, if not create it 
        if not self.es.indices.exists(index=self.ES_INDEX):
            self.es.indices.create(index=self.ES_INDEX)
            
        if "dest_folder" in kwargs:
            self.dest_folder = kwargs["dest_folder"]
        else:
            self.dest_folder = "/home/eliad/python/image_crawler/images_sig_db/"
       
        
    def load_image_details_array(self, image_details_arr):
        for img_dtl in image_details_arr:
            self.load_image_details(img_dtl)
                
    def load_image_details(self, img_dtl):
        try:
            #print ', '.join("%s: %s" % img_dtl for img_dtl in vars(img_dtl).items())
            
            # Check if img is on DB
            res = self.ses.search_image(img_dtl.path, all_orientations=True)
            
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
                
                # Check if we already got this image from this url
                found_details = False
                for img_dtl_db in found_rec["metadata"]["details"]:
                    if img_dtl_db["website_src_url"] == img_dtl.website_src_url:
                        img_dtl_db["time_last"] = img_dtl.time
                        
                        if "cnt" in img_dtl_db:
                            img_dtl_db["cnt"] = img_dtl_db["cnt"] + 1
                        else:
                            img_dtl_db["cnt"] = 1
                            self.stats.Incr("no_cnt_in_img_dtl_db")
                            
                        found_details = True
                        break
                
                if not found_details:
                    img_dtl.id = found_rec["metadata"]["details"][0]["id"] # use old id for all img_dtl
                    found_rec["metadata"]["details"].append(common.to_dict(img_dtl))
                    found_rec["metadata"]["details_cnt"] = found_rec["metadata"]["details_cnt"] + 1
                    found_rec["metadata"]["website_info"].append(img_dtl.website_info)
                
                rec_id = found_rec["id"]
                doc = { "metadata" : found_rec["metadata"] }
                self.es.update(index=self.ES_INDEX, doc_type=self.ES_DOC_TYPE, id=rec_id, body={ 'doc': doc })
                
            else:
                self.stats.Incr("new_image")
                
                filename_move = self.dest_folder + img_dtl.id + "." + img_dtl.extension
                
                metadata = dict()
                img_dtl.cnt = 1
                img_dtl.path_sig_db = filename_move
                metadata["details"] = [ common.to_dict(img_dtl) ] 
                metadata["details_cnt"] = 1
                metadata["website_info"] = [ img_dtl.website_info ]
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

    def update_metadata(self, url_info, ext):
        
        # Check if img is on DB
        query = { "query": { "terms": { "_id": url_info.initiator_id } } } 
        res = self.es.search(index=self.ES_INDEX, doc_type=self.ES_DOC_TYPE, body=query)
        print("%d documents found" % res['hits']['total'])
        
        found_rec = None
        if res['hits']['total'] == 1:
            found_rec = res['hits']['hits'][0]
        
        if found_rec is not None:
            rec_id=found_rec["id"]
            found_rec["metadata"]["link_website_info"] = ext.url_info.extract_info
            doc = { "metadata" : found_rec["metadata"] }
            self.es.update(index=self.ES_INDEX, doc_type=self.ES_DOC_TYPE, id=rec_id, body={ 'doc': doc })
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        