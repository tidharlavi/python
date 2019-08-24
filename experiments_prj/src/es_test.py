'''
Created on Dec 1, 2017

@author: eliad
'''
from datetime import datetime
from elasticsearch import Elasticsearch

from topia.termextract import extract 
from rake_nltk import Rake
from nltk import word_tokenize
import nltk
from nltk.tag.stanford import StanfordNERTagger

##################
# Stats
##################
import time # Measure execution time
import json
class Stats(object):

    def __init__(self, statsList=[]):
        self.stats = {}

        for stat in statsList:
            self.stats[stat] = 0

    def Get(self):
        return self.stats

    def Incr(self, key):
        if key in self.stats:
            self.stats[key] += 1
        else:
            self.stats[key] = 1

    def TimeStart(self, key):
        self.stats[key] = time.time()

    def TimeEnd(self, key):
        timeStart = self.stats[key]
        timeEnd = time.time()
        self.stats[key] = timeEnd - timeStart

    def Add(self, key, val):
        self.stats[key] = val
        
    def AddVal(self, key, val):
        if key in self.stats:
            self.stats[key] += val
        else:
            self.stats[key] = val

    def GetVal(self, key):
        return self.stats[key]
    
    def add_stats(self, stats_new, prefix=None):
        stats_dic_new = stats_new.Get()
        if not prefix:
            self.stats.update(stats_dic_new)
        else:
            for key, value in stats_dic_new.iteritems():
                self.Add(prefix + "_" + key, value)
    
    def Print(self, pretty=True):
        stats_str = ""
        if pretty:
            stats_str = json.dumps(self.Get(), sort_keys=True, indent=4)
        else:
            stats_str = json.dumps(self.Get(), sort_keys=True)
        
        return stats_str

##################
# Logging
##################
import logging
LOGGING_FILE_NAME = ""
loggingFormat = '%(asctime)-15s|%(levelname)s|%(name)s|%(funcName)s|%(lineno)d|%(message)s'
logging.basicConfig(level=logging.INFO, format=loggingFormat, filename=LOGGING_FILE_NAME)

log = logging.getLogger(__name__)

# Init ES
es = Elasticsearch()

if False:

    doc = {
        'author': 'kimchy',
        'text': 'Elasticsearch: cool. bonsai cool.',
        'timestamp': datetime.now(),
    }
    res = es.index(index="test-index", doc_type='tweet', id=1, body=doc)
    print(res['created'])
    
    res = es.get(index="test-index", doc_type='tweet', id=1)
    print(res['_source'])
    
    es.indices.refresh(index="test-index")
    
    res = es.search(index="test-index", body={"query": {"match_all": {}}})
    print("Got %d Hits:" % res['hits']['total'])
    for hit in res['hits']['hits']:
        print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
        

def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))

    return entity_names

        
if True:
    ES_INDEX = 'images'
    ES_DOC_TYPE = 'image'
    
    stats = Stats()

    res = es.search(index=ES_INDEX, body={'size' : 100, "query": {"match_all": {}}})
    
    log.info("res['hits']['total']=%d", res['hits']['total'])
    log.info("len(res['hits']['hits'])=%d", len(res['hits']['hits']))
    log.info("res['hits']['hits'][0]['_id']=%s", res['hits']['hits'][0]['_id'])
       
    
    for hit in res['hits']['hits']:
        
        meta = hit["_source"]["metadata"]
        if len(meta["html_text"]) and meta["html_text"][0]:
            stats.Incr("html_text_cnt_" + str(len(meta["html_text"])))
            
            log.info("html_text='%s'", meta["html_text"])
            # Photo      Credit Tang Ke/Xinhua, via Getty Images      Is China a Colonial Power?   Or is it presenting an alternative model of development to a world that could use one?   1d ago   By JAMES A. MILLWARD']'
            
            extractornlp = extract.TermExtractor()
            
            html_text = meta["html_text"][0]
            
            
            sentences = nltk.sent_tokenize(html_text)
            tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
            tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
            chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

            entity_names = []
            for tree in chunked_sentences:
                # Print results per sentence
                # print extract_entity_names(tree)
            
                entity_names.extend(extract_entity_names(tree))
            
            # Print all entity names
            print entity_names
            
            # Print unique entity names
            print set(entity_names)
                 
            # Download this file - https://gist.github.com/troyane/c9355a3103ea08679baf, https://nlp.stanford.edu/software/CRF-NER.html, https://gist.github.com/obahareth/27db373e0cc12cc4cff59df1befb6179
            st = StanfordNERTagger('stanford-ner/english.all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')
 
            for sent in nltk.sent_tokenize(html_text):
                tokens = nltk.tokenize.word_tokenize(sent)
                tags = st.tag(tokens)
                for tag in tags:
                    if tag[1]=='PERSON': print tag
        
            # ### Tags (https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html)
            #----------------------------- tagg = extractornlp.tagger(html_text)
#------------------------------------------------------------------------------ 
            #-------------------------------------------------- tag_dic = dict()
            #-------------------------------------------------- for key in tagg:
                #------------- #key    <type 'list'>: [u'photo', 'NN', u'photo']
                #------------------ tag_dic[key[0].lower()] = ( key[1], key[2] )
#------------------------------------------------------------------------------ 
            #--------------------- sorted_term = sorted(extractornlp(html_text))
#------------------------------------------------------------------------------ 
            #------------------------------------------- image_photographer = ""
            #--------------------------------------------------- image_site = ""
#------------------------------------------------------------------------------ 
            #--------------------------------- tokens = word_tokenize(html_text)
#------------------------------------------------------------------------------ 
            #-------------------------------- for i, token in enumerate(tokens):
                #--------------------------------- if "credit" == token.lower():
                    #------------------------ log.info(i, token, tag_dic[token])
                    #------------------------------ for j in range(i+ 1, i + 4):
                        #--------------------------------- if tag_key[tokens[j]]
                
        
        if len(meta["html_tag_alt"]) and meta["html_tag_alt"][0]:
            stats.Incr("html_tag_alt_cnt_" + str(len(meta["html_tag_alt"])))
        if len(meta["html_tag_title"]) and meta["html_tag_title"][0]:
            stats.Incr("html_tag_title_cnt_" + str(len(meta["html_tag_title"])))
            
        

        
        # Take terms
        # Take all NNP, 
        # remove credit 'Photo      Credit Tang Ke/Xinhua, via Getty Images'
        # remove artical owner 'By JAMES A. MILLWARD' 
            
        
        
    
log.info("%s", stats.Print())
log.info("End !!!")
    
    
# Add string len stats
    
    
    