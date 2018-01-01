'''
Created on Dec 5, 2017

@author: eliad
'''

class image_details(object):
    '''
    classdocs
    '''


    def __init__(self, params = {"v": 1.1} ):
        '''
        Constructor
        '''
        self.v = params.get("v")

        

from enum import Enum

class extract_method(Enum):
    img_tag = 10
    style_attribute = 20
     
class download_method(Enum):
    src_url = 10
    embeeded = 20
     
class advertisers(Enum):
    doubleclick = 10
    taboola = 20
    outbrain = 30