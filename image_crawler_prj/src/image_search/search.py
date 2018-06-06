'''
Created on Jan 13, 2018

@author: eliad
'''

import os # Check if folder/file exists/sizes
import urllib2
import json
import uuid

from PIL import Image

# Local lib
import common
import crawler
from object_model import image_details
from object_model import url_info

# Image match
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES

# G Image reverse search 
from g_reverse_image_search import GReverseImageSearch


class Search(object):
    '''
    classdocs
    '''


    def __init__(self, params="{}"):
        '''
        Constructor
        '''
      
        if "dest_folder" in params:
            self.dest_folder = params["dest_folder"]
        else:
            self.dest_folder = "/home/eliad/python/image_crawler/images_sig_db/"
    
    def search(self, image_url=None, image_path=None):
        
        return_data = dict()
        
        if not image_url and not image_path:
            print("Search.search(): No image !!!")
            return
        
        # Search image in our DB
        es = Elasticsearch()
        ses = SignatureES(es)
        res = ses.search_image(image_url, all_orientations=True)
        
        # Check if we have a perfect match
        found_rec = None
        for rec in res:
            #print(rec["dist"])
            if rec["dist"] == 0.0:
                found_rec = rec
                break
        
        return_data["found_rec"] = None
        if found_rec is None:
            
            ### Fill image_details and load it to our ES DB
            img_dtl = image_details.ImageDetails()    
            img_dtl.src = image_url
            img_dtl.id_set()
            img_dtl.extract_method = image_details.ExtractMethodEnum.search
            img_dtl.download_method = image_details.DownloadMethodEnum.src_url
            
            print("image not in our DB, lets download it and add it to our DB")
            if image_url:
                filename = self.download_image(image_url, img_dtl.id)
                if not filename:
                    print("Search.search(), Error: Fail to download '{0}'.".format(image_url))
                    return None
                
                # validation
                img_dtl.os_size = os.stat(filename).st_size
                if img_dtl.os_size == 0:
                    #print("Fail to download '"+src+"', fileName '"+fileName+"'. File size is 0.")
                    self.stats.Incr("skip_os_file_size")
                    return None
                
                img_dtl.path = filename
                img_dtl_id = img_dtl.id
                
                try:
                    with Image.open(filename) as im:
                        # fill img object
                        img_dtl.image_height = im.size[1]
                        img_dtl.image_width = im.size[0]
                        #img_dtl.image_format = im.format
                        #img_dtl.image_format_description = im.format_description
                        #img_dtl.image_info = im.info
                        #img_dtl.image_mode = im.mode
                        #if hasattr(im, "text"):
                        #    img_dtl.image_text = im.text
                        #img_dtl.image_tile = im.tile
        
                except Exception as e: 
                    print("Fail to Image.open '"+filename+"'.")
            
            metadata = dict()
            img_dtl.cnt = 1
            img_dtl.path_sig_db = filename
            metadata["details"] = [ common.to_dict(img_dtl) ] 
            #metadata["website_info"] = [ img_dtl.website_info ]
            self.ses.add_image(img_dtl.path, None, False, metadata, False, img_dtl.id)
                
        else:
            print("image in our DB.")
            metadata = found_rec["metadata"]
            filename = metadata["details"][0].path
            img_dtl_id = metadata["details"][0].id
            return_data["found_rec"] = found_rec            
                
        
        print("filename='{0}.'".format(filename))
        return_data["filename"] = filename 
        
        # Reverse image search in google
        g_rev_img_srch = GReverseImageSearch()
        g_rev_img_srch.search(image_url = image_url) 
        print("Statistics '"+json.dumps(g_rev_img_srch.stats.Get(), sort_keys=True, indent=4)+"'.")
        
        return_data["g_img_dtl"] = g_rev_img_srch.g_img_dtl 
        
        url_info_arr = []
        for g_page_res in g_rev_img_srch.g_img_dtl.pages:
            # create extractor task for each url in page_result
            url_info_new = url_info.UrlInfo({
                                               "parent_url": None,
                                               "url": g_page_res.href,
                                               "type": url_info.UrlInfoTypeEnum.unknown,
                                               "initiator_type": url_info.UrlInfoInitiatorTypeEnum.search,
                                               "initiator_id": None,
                                               "depth": 0,
                                               "depth_max": 1,
                                               })
            
            url_info_arr.append(url_info_new)
            
            
        # Add internal links to taskq 
        crlr = crawler.Crawler({})
        print "Search.search()(): crlr.insert_urls() from GSearch."
        crlr.insert_urls(url_info_arr)
        print("Statistics crawler: '"+json.dumps(crlr.stats.Get(), sort_keys=True, indent=4)+"'.")
        
        # Add g_img_dtl to ES-DB
        metadata["g_details"] = [ g_rev_img_srch.g_img_dtl ]
        index='images'
        doc_type='image' 
        doc = { "metadata" : metadata }
        self.es.update(index=index, doc_type=doc_type, id=img_dtl_id, body={ 'doc': doc })
        
        return return_data
        
        
    def download_image(self, image_url, img_id):
        
        filename = self.dest_folder + img_id
        
        try:
            # try to get image
            opener = urllib2.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')]
            response = opener.open(image_url)
        except Exception:
            print("Fail to download '"+image_url+"'.")
            return None

        try:
            # try to save image
            with open(filename, 'wb') as f:
                f.write(response.read())
        except Exception:
            print("Fail to save '"+filename+"'.")
            return None
        
        return filename
        
        
        
        
if __name__ == "__main__":
    print("Running Search code example.")
                
    search = Search()
    return_data = search.search(image_url = "http://feedbox.com/wp-content/uploads/2018/01/what-you-need-to-do-because-of-flaws-in-computer-chips-1080x675.jpg")
    print("Search return data '"+json.dumps(common.to_dict(return_data), sort_keys=True, indent=4)+"'.")


 
