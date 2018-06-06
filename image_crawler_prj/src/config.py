'''
Created on Jun 6, 2018

@author: eliad
'''

import os
import argparse
import json
from bson.json_util import default


config_default = {
    "CONFIG_FILE": "/home/eliad/git/python/image_crawler_prj/src/config.json",
}

config_dev = {
    "TEST_TMP_DIR": "tests",
    "TEST_TIMEOUT": 20
}

config_prod = {
    "SERVICE": "travis-ci",
    "HOOK_URL": "web-hooking-url-from-ci-service"
}


class Config:
    
    conf = config_default
    
    def __init__(self):
        
        parser = argparse.ArgumentParser()
        parser.add_argument('-mode', default='dev', help='Setting app mode')
        args = parser.parse_args()
        
        if args.mode == 'dev':
            self.conf_dict_add(config_dev)
        elif args.mode == 'prod': 
            self.conf_dict_add(config_dev)
            
        config_file = None
        if os.path.exists(self.conf["CONFIG_FILE"]):
            with open(self.conf["CONFIG_FILE"], 'r') as f:
                config_file = json.load(f)
                self.conf_dict_add(config_file)
        
        
    def conf_dict_add(self, conf_add):
        for key, value in conf_add.iteritems():
            self.conf[key] = value
        
        
