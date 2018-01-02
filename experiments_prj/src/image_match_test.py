'''
Created on Dec 1, 2017

@author: eliad
'''

import json # from print beautify

from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES


print("start !!!")

es = Elasticsearch()
ses = SignatureES(es)

ses.add_image('https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched.jpg/687px-Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched.jpg')
ses.add_image('https://pixabay.com/static/uploads/photo/2012/11/28/08/56/mona-lisa-67506_960_720.jpg')
ses.add_image('https://upload.wikimedia.org/wikipedia/commons/e/e0/Caravaggio_-_Cena_in_Emmaus.jpg')
ses.add_image('https://c2.staticflickr.com/8/7158/6814444991_08d82de57e_z.jpg')


res = ses.search_image('https://pixabay.com/static/uploads/photo/2012/11/28/08/56/mona-lisa-67506_960_720.jpg')

print json.dumps(res, sort_keys=True, indent=4)

print("start !!!")