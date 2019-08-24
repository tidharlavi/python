'''
Created on Dec 5, 2017

@author: eliad
'''

from datetime import datetime # datetime now
import uuid # set image id

from enum import Enum

class ImageDetails(object):
    '''
    classdocs
    '''


    def __init__(self, ver="1.1" ):
        '''
        Constructor
        '''
        self.ver = ver
        
        # Recurring (same: domain, image src, dims. different: time, crawl, in page location, page)
        self.time = datetime.utcnow()
        self.cnt = 0
        
        self.recurring = [] # { time, crawl, page }
        self.recurring_cnt = 0
        
        self.id = ""
        self.path = ""
        self.path_sig_db = ""
        self.crwl = ""
        
        # Image source URL
        self.src =  ""
        
        self.website_src_url =  ""
        self.website_domain = ""
        #self.website_info = None
        
        self.extract_method = ExtractMethodEnum.other
        self.download_method = DownloadMethodEnum.other
        
        # HTML tag 
        self.html_tag_id = ""
        self.html_tag_height = ""
        self.html_tag_width = ""
        self.html_tag_alt = ""
        self.html_tag_title = ""
        
        # HTML (surrounding image)
        self.html_text = []
        self.html_link = ""

        self.html_adv = AdvertisersEnum.none
        
        # Driver/Browser      
        self.browser_window_size = None
        self.browser_location = None
        self.browser_location_once_scrolled_into_view = None  
        self.browser_width = 0
        self.browser_height = 0
        
        # image properties
        self.image_height = ""
        self.image_width = ""
        #self.image_format = ""
        #self.image_format_description = ""
        #self.image_info = None
        #self.image_mode = ""
        #self.image_text_dic = None # Dict
        #self.image_tile = None
                
        # OS
        self.os_size = 0
        
    def id_set(self):
        self.id = "image_" + str(uuid.uuid4())
        return self.id 


class ImageDetailsRecurring(object):
    '''
    classdocs
    '''

    def __init__(self, img_dtl):
        self.time = img_dtl.time
        self.website_src_url = img_dtl.website_src_url
        self.crwl = img_dtl.crwl
        

class ExtractMethodEnum(Enum):
    img_tag = 10
    style_attribute = 20
    search = 30
    other = 900
     
class DownloadMethodEnum(Enum):
    src_url = 10
    embeeded = 20
    uploaded = 30
    other = 900
     
class AdvertisersEnum(Enum):
    doubleclick = 10
    taboola = 20
    outbrain = 30
    none = 900
    
    
    
    
