'''
Created on Dec 5, 2017

@author: eliad
'''
import object_model

import task_queue
from task_queue import tasks

import common
import crawler

# get exception info
import sys 
import traceback

# mongo
from pymongo import MongoClient



def insert_dynamic_pages_url(url):
    url_info = object_model.url_info.UrlInfo({
                                               "parent_url": url,
                                               "url": url,
                                               "type": object_model.url_info.url_info_type.dynamic,
                                               "initiator_type": object_model.url_info.url_info_initiator_type.manual,
                                               "initiator_id": "eliad",
                                               "depth": 0,
                                               })
    
    client = MongoClient()
    coll_dynamic_pages_urls = client.urls.dynamic_pages_urls
    
    # upsert to DB
    try:
        res = coll_dynamic_pages_urls.update({"_id": url_info._id}, common.to_dict(url_info), upsert=True)
    except Exception as e: 
        print("Mongo Exception: type '",sys.exc_info()[0],"', message '",e,"'")
        traceback.print_exc()
        return None
    
    print res
     


url = "https://www.ynet.co.il/home/0,7340,L-544,00.html"
url = "https://www.ynet.co.il/articles/0,7340,L-5063578,00.html"
url ="https://www.ynet.co.il/articles/0,7340,L-5063952,00.html"
#url = "https://www.nytimes.com/"
#url = "https://www.nytimes.com/2017/12/29/opinion/dont-cheer-as-the-irs-grows-weaker.html"
#insert_dynamic_pages_url(url)


import extractor

ext = extractor.extractor()
ext.extract_web_page_info(url)

#import lassie
#import pprint 
#pprint.pprint (lassie.fetch(url, all_images=True))

exit
 

### testing 
#common.link_extractor(url, None, "/home/eliad/python/image_crawler/images_db/walla.co.il/www.walla.co.il/2017_12_23-15")


crlr = crawler.Crawler({})
url_info = object_model.url_info.UrlInfo({
                                          "url": url,
                                          "initiator_type": object_model.url_info.url_info_initiator_type.manual,
                                          "initiator_id": "eliad",
                                          "depth_max": 2,
                                          })

#url_info.depth = 0
#url_info.uuid = [ "qweqwe" ]
#common.link_extractor(url_info, None, "/home/eliad/python/image_crawler/images_db/ynet.co.il/www.ynet.co.il%2Fhome%2F0%2C7340%2CL-544%2C00.html/2017_12_26-09")

crlr.insert_start_url(url_info)


#res = tasks.extract_load.delay(url)
#res = tasks.mul.delay(3, 2)
#print res.ready()
#print res.get()
## Exception handling
#result.get(propagate=False) # dont propogate exception to result
#print res.traceback # get Exception traceback

    
    
    
    
    
    


