'''
Created on Dec 16, 2017

@author: eliad
'''

import os
from shutil import copyfile
import json 
import logging

# get exception info
import sys 
import traceback

# Local lib
import common
from object_model import image_record
from object_model import image_details

# Image match
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES

log = logging.getLogger(__name__)

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
            log.info("Init Elasticsearch().")
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
        
        self.stats.Add("load_image_array_len", len(image_details_arr))
        
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
                
                if found_rec["metadata"]["src"] == img_dtl.src:
                    self.stats.Incr("found_image_with_same_src")
                else:
                    self.stats.Incr("found_image_with_diff_src")
                    
                # Update main record params
                found_rec["metadata"]["cnt"] = found_rec["metadata"]["cnt"] + 1
                if img_dtl.src and img_dtl.src not in found_rec["metadata"]["src"]: 
                    found_rec["metadata"]["src"].append(img_dtl.src)
                if img_dtl.html_tag_title and img_dtl.html_tag_title not in found_rec["metadata"]["html_tag_title"]: 
                    found_rec["metadata"]["html_tag_title"].append(img_dtl.html_tag_title)
                if img_dtl.html_tag_alt and img_dtl.html_tag_alt not in found_rec["metadata"]["html_tag_alt"]:
                    found_rec["metadata"]["html_tag_alt"].append(img_dtl.html_tag_alt)
                if img_dtl.html_link and img_dtl.html_link not in found_rec["metadata"]["html_link"]:
                    found_rec["metadata"]["html_link"].append(img_dtl.html_link)
                    
                for html_text in img_dtl.html_text:
                    if html_text not in found_rec["metadata"]["html_text"]:
                        found_rec["metadata"]["html_text"].append(img_dtl.html_text)
                
                # Check if we already got this image from this url
                found_details = False
                for img_dtl_db in found_rec["metadata"]["details"]:
                    
                    if "browser_width" not in img_dtl_db or "browser_height" not in img_dtl_db:
                        self.stats.Incr("missing_browser_dims")
                        continue
                    
                    # Add to recurring if same domain and similar dims
                    width_diff = abs(img_dtl_db["browser_width"] - img_dtl.browser_width)
                    width_min = min(img_dtl_db["browser_width"], img_dtl.browser_width)
                    height_diff = abs(img_dtl_db["browser_height"] - img_dtl.browser_height)
                    height_min = min(img_dtl_db["browser_height"], img_dtl.browser_height)
                    if (img_dtl_db["website_domain"] == img_dtl.website_domain) and (width_diff != 0 or height_diff != 0):
                        self.stats.Incr("same_domain_diff_dims")
                     
                    log.info("width_diff='%d', width_min='%d', height_diff='%d', height_min='%d'.", width_diff, width_min, height_diff, height_min)
                    if (img_dtl_db["website_domain"] == img_dtl.website_domain) and (width_diff < (0.15 * width_min)) and (height_diff < (0.15 * height_min)):  
                        recurring = image_details.ImageDetailsRecurring(img_dtl)
                        img_dtl_db["recurring"].append(common.to_dict(recurring))
                        img_dtl_db["recurring_cnt"] = img_dtl_db["recurring_cnt"] + 1
                        
                        self.stats.Incr("recurring_true")
                        found_details = True
                        break
                    else:
                        self.stats.Incr("recurring_false")
                                       
                if not found_details:
                    img_dtl.id = found_rec["metadata"]["details"][0]["id"] # use old id for all img_dtl
                    found_rec["metadata"]["details"].append(common.to_dict(img_dtl))
                    found_rec["metadata"]["details_cnt"] = found_rec["metadata"]["details_cnt"] + 1
                
                rec_id = found_rec["id"]
                doc = { "metadata" : found_rec["metadata"] }
                self.es.update(index=self.ES_INDEX, doc_type=self.ES_DOC_TYPE, id=rec_id, body={ 'doc': doc })
                
            else:
                self.stats.Incr("new_image")
                
                filename_move = self.dest_folder + img_dtl.id + "." + img_dtl.extension
                                
                img_dtl.cnt = 1
                img_dtl.path_sig_db = filename_move
                
                image_rec = image_record.ImageRecord()
                image_rec.image_details_add(img_dtl)
                
                metadata = common.to_dict(image_rec)
              
                self.ses.add_image(img_dtl.path, None, False, metadata, False, img_dtl.id)
                
                # move (currently copy) file from his folder
                if not os.path.exists(filename_move):
                    #os.rename(img_dtl.path , filename_move)
                    copyfile(img_dtl.path , filename_move)
                    
        except Exception as e: 
            log.exception("Exception while loading '%s' to ES DB.", img_dtl.path)
            self.stats.Incr("exception_in_loader")

    def update_metadata(self, url_info, ext):
        
        # Check if img is on DB
        query = { "query": { "terms": { "_id": url_info.initiator_id } } } 
        res = self.es.search(index=self.ES_INDEX, doc_type=self.ES_DOC_TYPE, body=query)
        log.info("%d documents found" % res['hits']['total'])
        
        found_rec = None
        if res['hits']['total'] == 1:
            found_rec = res['hits']['hits'][0]
        
        if found_rec is not None:
            rec_id=found_rec["id"]
            found_rec["metadata"]["link_website_info"] = ext.url_info.extract_info
            doc = { "metadata" : found_rec["metadata"] }
            self.es.update(index=self.ES_INDEX, doc_type=self.ES_DOC_TYPE, id=rec_id, body={ 'doc': doc })
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        