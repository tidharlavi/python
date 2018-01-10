'''
Created on Dec 20, 2017

@author: eliad
'''

# celery
from __future__ import absolute_import, unicode_literals
from .celery import app
from celery.utils.log import get_task_logger

# general
import json

# tasks
import extractor
import loader
import crawler

# locals
import object_model

# Image match
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES


logger = get_task_logger(__name__)

   
@app.task
def extract_load_crawl(url_info_dic):
    print "start extract_load_crawl()"
    logger.info('start task extract_load_crawl'.format())
    
    url_info = object_model.url_info.UrlInfo(url_info_dic)
    
    print ', '.join("%s: %s" % url_info for url_info in vars(url_info).items())
    
    es = Elasticsearch()
    ses = SignatureES(es)
    ldr =  loader.Loader({"es": es,
                          "ses": ses,
                         })

    ext = extractor.extractor({
                               "dest_folder": "/home/eliad/python/image_crawler/images_db"
    })
    
    print "extract_load_crawl(): Going to ext.extract_info()."
    ext.extract_info(url_info)
    print("Statistics extractor: '"+json.dumps(ext.stats.Get(), sort_keys=True, indent=4)+"'.")
    
    # Go over extract images and add them to image
    print "extract_load_crawl(): ldr.load_image_details_array()."
    ldr.load_image_details_array(ext.image_details_arr)
    print("Statistics loader: '"+json.dumps(ldr.stats.Get(), sort_keys=True, indent=4)+"'.")

    # Add internal links to taskq 
    crlr = crawler.Crawler({})
    print "extract_load_crawl(): crlr.update_url_extract_info()."
    crlr.update_url_extract_info(url_info)
    
    print "extract_load_crawl(): crlr.insert_urls()."
    crlr.insert_urls(ext.internal_links)
    print("Statistics crawler: '"+json.dumps(crlr.stats.Get(), sort_keys=True, indent=4)+"'.")
    
    print "extract_load_crawl(): crlr.insert_urls()."
    crlr.insert_urls(ext.image_links)
    print("Statistics crawler: '"+json.dumps(crlr.stats.Get(), sort_keys=True, indent=4)+"'.")
    
    
    





     