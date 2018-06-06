'''
Created on Dec 19, 2017

@author: eliad
'''

import uuid

# Local lib
import common

class UrlInfo(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        self.v = params.get("v")
        if not self.v:
            self.v = 1.1
        
        self.parent_url = params.get("parent_url")
        self.url_orig = params.get("url")
        
        
        self.type = params.get("type")
        
        self.initiator_type = params.get("initiator_type")
        self.initiator_id = params.get("initiator_id") # Example: for extracted should be the depth 0 link, for image should be image._id
        
        self.depth = params.get("depth")
        if not self.depth:
            self.depth = 0
        
        self.depth_max = params.get("depth_max")

        # If not dic, create        
        if not hasattr(self, "crwl_dic"):
            self.crwl_dic = dict()
        
        # if no crel, create
        self.crwl_curr = params.get("crwl_curr")
        if self.crwl_curr is None:
            # New url, lets create a uuid
            self.crwl_curr = "crwl_" + str(uuid.uuid4())

        # update dic
        if self.crwl_curr in self.crwl_dic:
            self.crwl_dic[self.crwl_curr] += 1
        else:
            self.crwl_dic[self.crwl_curr] = 1
            
        self.last_crawl = params.get("last_crawl")
        
        self._id = common.UrlParser(self.url_orig).url_complete_from_parent(self.parent_url, encode=True, add_scheme=False)
        self.url = common.UrlParser(self.url_orig).url_complete_from_parent(self.parent_url)

from enum import Enum

class UrlInfoTypeEnum(Enum):
    static = 10
    dynamic = 20
    unknown = 90
    
class UrlInfoInitiatorTypeEnum(Enum):
    manual = 10
    scheduled = 20
    extracted = 30
    image = 40
    search = 50