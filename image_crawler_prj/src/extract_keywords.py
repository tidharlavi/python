'''
Created on Jan 6, 2018

@author: eliad
'''

import os

import requests

from bs4 import BeautifulSoup

import html2text

from topia.termextract import extract 
from rake_nltk import Rake

class ExtractKeywords(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        
    def extract_keywords(self, url = None, html_decoded_text = None, html_file = None):
        
        print "Start extract_keywords '{0}'.".format(url) 
        
        html_text = self.utext_get(url, html_decoded_text, html_file)
                
        self.page_title, self.page_meta_keywords, self.page_meta_desription = self.extract_html_info(html_text)    
            
        text = self.extract_text_content(html_text)
                
        tag_dic, term_top = self.extract_term(text)
        
        texts = [self.page_title, self.page_meta_keywords, self.page_meta_desription, text]
        self.keywords = self.keywords_get(texts, tag_dic, term_top)
    
    def utext_get(self, url = None, html_decoded_text = None, html_file = None):        
        if html_decoded_text:
            return html_decoded_text.decode('utf-8')
            
        if html_file and os.path.isfile(html_file):
            
            with open(html_file, 'r') as file:
                html_text = file.read().decode('utf-8')
                # done have headers, assume encoding utf-8
                return html_text
            
        if url:
            res = requests.get(url)
                
            try:
                content_type = res.headers['Content-Type'] # figure out what you just fetched
                ctype, charset = content_type.split(';')
                encoding = charset[len(' charset='):] # get the encoding
                #print encoding # ie ISO-8859-1
            except:
                encoding = 'utf-8'
                
        
            html_text = res.content.decode(encoding)
            return html_text
        
    def extract_html_info(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
                
        keywords = None
        meta_tags = soup.findAll("meta", attrs={"name":"keywords"})
        if len(meta_tags) == 1:
            for meta_tag in meta_tags:
                if "content" in meta_tag.attrs:
                    keywords = meta_tag["content"]
                    print("meta name 'keywords' = " + keywords)
                    
            
        desription = None
        meta_tags = soup.findAll("meta", attrs={"name":"description"})
        if len(meta_tags) == 1:
            for meta_tag in meta_tags:
                if "content" in meta_tag.attrs:
                    desription = meta_tag["content"]
                    print("meta name 'description' = " + desription)
                    
             
        title = soup.title.string
        print("title=" + title)
        
        return title, keywords, desription 
        
    def extract_text_content(self, html_text):
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.bypass_tables = True
        h.ignore_images = True
        h.ignore_links = True
        h.ignore_emphasis = True
        h.skip_internal_links = True

        result = h.handle(html_text)
        
        # print "html2text result: ============================================================="
        # print(result)
        
        text = ""
        bad_words = ['*', '#']
        for line in result.splitlines(True):
            if not any(bad_word in line for bad_word in bad_words) and len(line) > 40:
                text += line
        
        #print "html2text clean result: ============================================================="
        #print(text)
               
        return text
    
    def extract_term(self, html_text):
        # use topia -- https://pypi.python.org/pypi/topia.termextract/
    
        ### TermExtractor
        extractornlp = extract.TermExtractor()
        
        ### Tags
        tagg = extractornlp.tagger(html_text)
        #     for key in tagg:
        #         print key[2] + " -- " + key[1] + " -- " + key[0] 
    
        tag_dic = dict()
        for key in tagg:
        #         if key[0] != key[2]:
        #             print key[2] + " -- " + key[1] + " -- " + key[0] + " ==> key[0] diff from key[2]"
            if key[0] in tag_dic:
                if tag_dic[key[0]][0][0] != key[1] or tag_dic[key[0]][0][1] != key[2]:
                    tag_dic[key[0]].append( ( key[1], key[2]) ) 
            else:
                tag_dic[key[0]] = [ ( key[1], key[2] ) ]
        
        sorted_term = sorted(extractornlp(html_text))
        sorted_by_count = sorted(sorted_term, key=lambda tup: tup[1], reverse=True)
        term_top = sorted_by_count[:len(sorted_by_count) / 10]
        
        #     for key in sorted_by_count:
        #         print str(key[2]) + " -- " + str(key[1]) + " -- " + key[0] 
        
        return tag_dic, term_top
        
    def keywords_get(self, texts, tag_dic, term_top):  
        ## https://github.com/csurfer/rake-nltk
    
        r = Rake() # Uses stopwords for english from NLTK, and all puntuation characters.
    
        #language = "he"
        #r = Rake(language) # To use it in a specific language supported by nltk.
        
        # If you want to provide your own set of stop words and punctuations to
        #r = Rake([u'\\u05d0\\u05ea'])    
        
        keywords = dict()
    
        print "term_top      : " + repr(term_top).decode("unicode-escape")
        for key in term_top[:10]:
                if key[0] in keywords:
                    keywords[key[0]] = keywords[key[0]] + key[1]
                else:
                    keywords[key[0]] = key[1]
        
        for text in texts:
            
            print "RAKE on len '{0}'. text: '{1}'".format(len(text), text[0:100].encode('utf-8'))
            
            r.extract_keywords_from_text(text)
        
            ranked_phrases = r.get_ranked_phrases_with_scores()
            print "ranked_phrases: " + repr(ranked_phrases).decode("unicode-escape")
            if False:
                for key in ranked_phrases[:10]:
                    if key[1] in keywords:
                        keywords[key[1]] = keywords[key[1]] + key[0]
                    else:
                        keywords[key[1]] = key[0]
                    
            
            word_degrees = r.get_word_degrees()
            word_degrees_sorted = sorted(word_degrees.iteritems(), key=lambda tup: tup[1], reverse=True) 
            print "word_degrees  : " + repr(word_degrees_sorted[0:30]).decode("unicode-escape")
            for key in word_degrees_sorted[:10]:
                if key[0] in keywords:
                    keywords[key[0]] = keywords[key[0]] + key[1]
                else:
                    keywords[key[0]] = key[1]
            
            get_word_frequency_distribution = r.get_word_frequency_distribution()
            get_word_frequency_distribution_sorted = sorted(get_word_frequency_distribution.iteritems(), key=lambda tup: tup[1], reverse=True) 
            print "word_frequency: " + repr(get_word_frequency_distribution_sorted[0:30]).decode("unicode-escape")
            for key in get_word_frequency_distribution_sorted[:10]:
                if key[0] in keywords:
                    keywords[key[0]] = keywords[key[0]] + key[1]
                else:
                    keywords[key[0]] = key[1]
            
            
        keywords_new = []
        keywords_sorted = sorted(keywords.iteritems(), key=lambda tup: tup[1], reverse=True)
        for keyword in keywords_sorted:
            if len(keyword[0]) > 2:
                keywords_new.append(keyword[0].encode('ascii', 'ignore'))
         
        print "keywords  : " + repr(keywords_new[0:30]).decode("unicode-escape")
        
        return keywords_new[:15]
        
        
        
        
        
        
        
        
        
    
    