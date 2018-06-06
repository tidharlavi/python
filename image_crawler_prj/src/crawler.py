'''
Created on Dec 21, 2017

@author: eliad
'''

import logging
from datetime import datetime
import uuid

# get exception info
import sys 
import traceback

# mongo
from pymongo import MongoClient

# tasks
import task_queue.tasks

# Local lib
import common


log = logging.getLogger(__name__)

class Crawler(object):
    '''
    classdocs
    '''


    def __init__(self, static_url_timedelta_days = 2):
        '''
        Constructor
        '''
        
        # Mongo DB
        self.client = MongoClient()
        
        self.db_urls = self.client.urls
        
        self.coll_urls = self.db_urls.urls
        
        # Statistics
        self.stats = common.Stats()
        
    def insert_new_url(self, url_info):
        self.stats.Incr("static_page_new")
                    
        # Insert to DB
        url_info.last_crawl = datetime.now()
        try:
            url_info_dic = common.to_dict(url_info)
            res = self.coll_urls.insert(url_info_dic)
        except Exception as e:
            log.exception("Mongo insert Exception") 
            self.stats.Incr("exception_mongo_insert")

        if res != url_info._id:
            print("Fail insert mongo id '" + url_info._id + "'")
            self.stats.Incr("error_mongo_add_res_mismatch")
        
        ###### Add url to Q - url extractor/proccessed
        #print("Going to extract url '"+url_info.url+"'.")
        task_queue.tasks.extract_load_crawl.delay(common.to_dict(url_info))
                
    def insert_urls(self, url_info_arr):
        '''
        Insert links to extractor task
        '''
        
        # Init stats
        self.stats = common.Stats()
        
        if url_info_arr is None:
            log.info("url_info_arr is None !!! return.")
            return
        
        self.stats.Add("url_info_arr_len", len(url_info_arr))
        
        for url_info in url_info_arr:
            
            # check depth
            if url_info.depth > url_info.depth_max:
                self.stats.Incr("reach_depth_max")
                continue
            
            try:
                # Check if url already exist in static list
                url_info_db = self.coll_urls.find_one({"_id": url_info._id})
                if url_info_db is None:
                    # page_url does not exist in DB, we can crawl - extract - load it, and add it to coll_urls
                    self.insert_new_url(url_info)
                else:
                    crwl_dic_key = "crwl_dic." + url_info.crwl_curr
                    
                    # check if this url already crawled in the current run (check by uuid)
                    if url_info.crwl_curr in url_info_db["crwl_dic"]:
                        self.stats.Incr("url_already_crawled")
                        self.coll_urls.update({'_id': url_info._id}, {'$inc': {crwl_dic_key: 1 }})
                    else:
                        self.stats.Incr("url_in_db_crwl_not_in_dic")
                    
            except Exception as e: 
                print("Crawler.insert_urls Exception: type '",sys.exc_info()[0],"', message '",e,"'")
                traceback.print_exc()
                return None
            
    def update_url_extract_info(self, extractor, url_info):
        
        if not hasattr(url_info, "extract_info") or not url_info.extract_info or type(url_info.extract_info) is not dict or not bool(url_info.extract_info):
            return
        
        self.coll_urls.update({"_id": url_info._id}, { "$set": { "extract_info" : url_info.extract_info, "extract_stats": extractor.stats.Get() } })
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            