'''
Created on Dec 31, 2017

@author: eliad
'''
import sys
import os

from bs4 import BeautifulSoup # handle html parsing and printing

import html2text
import requests
from topia.termextract import extract 

import lassie
import pprint 

from rake_nltk import Rake

import common

if __name__ == '__main__':
    pass


# https://github.com/ethangardner/py-keyword-extraction/blob/master/pykw.py
# http://www.cortical.io/extract-keywords.html - api and free manual tool for keyword extract
# https://www.textrazor.com/docs/python - api, 500 per day free


def extract_web_page_utext(url):  

    html_source = None
    if url == None:
        return None
    
    utext = ""
    
    html_file = "/home/eliad/workspace/python.tests/html_pages/" + common.UrlParser(url).encode_url() + ".html"
    if (not os.path.isfile(html_file)):
        res = requests.get(url)
        
        with open(html_file, 'w') as html_file_handler:
            html_file_handler.write(res.content)
            
        content_type = res.headers['Content-Type'] # figure out what you just fetched
        ctype, charset = content_type.split(';')
        encoding = charset[len(' charset='):] # get the encoding
        #print encoding # ie ISO-8859-1
    
        utext = res.content.decode(encoding)
            
    if not utext:
        with open(html_file, 'r') as file:
            html_source = file.read().decode('utf-8')
            # done have headers, assume encoding utf-8
            utext = html_source
            
    return utext
    
    
def use_html2text(utext):
        
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.bypass_tables = True
    h.ignore_images = True
    h.ignore_links = True
    h.ignore_emphasis = True
    h.skip_internal_links = True
    #html = urllib.urlopen( url ).read()
    result = h.handle(utext)
    
    print "html2text result: ============================================================="
    print(result)
    
    clean_result = ""
    bad_words = ['*', '#']
    for line in result.splitlines(True):
        if not any(bad_word in line for bad_word in bad_words) and len(line) > 40:
            clean_result += line
    
    print "html2text clean result: ============================================================="
    print(clean_result)
           
    return clean_result
    

# test

def use_topia(clean_text):        
    # https://pypi.python.org/pypi/topia.termextract/
    
    ### TermExtractor
    extractornlp = extract.TermExtractor()
    
    ### Tags
    tagg = extractornlp.tagger(clean_text)
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
    
    sorted_term = sorted(extractornlp(clean_text))
    sorted_by_count = sorted(sorted_term, key=lambda tup: tup[1], reverse=True)
    term_top = sorted_by_count[:len(sorted_by_count) / 10]
    
#     for key in sorted_by_count:
#         print str(key[2]) + " -- " + str(key[1]) + " -- " + key[0] 
    
    return tag_dic, term_top    
    
def use_bs(utext):
        
    soup = BeautifulSoup(utext, 'html.parser')
                
    keywords = None
    meta_tags = soup.findAll("meta", attrs={"name":"keywords"})
    if len(meta_tags) == 1:
        for meta_tag in meta_tags:
            if "content" in meta_tag.attrs:
                print("meta name 'keywords' = " + meta_tag["content"])
                keywords = meta_tag["content"]
        
    desription = None
    meta_tags = soup.findAll("meta", attrs={"name":"description"})
    if len(meta_tags) == 1:
        for meta_tag in meta_tags:
            if "content" in meta_tag.attrs:
                print("meta name 'description' = " + meta_tag["content"])
                desription = meta_tag["content"]
         
    title = soup.title.string
    print("title=" + title)
    
    return title, keywords, desription
         
def bs_get_text(utext):
    
    soup = BeautifulSoup(utext, 'html.parser')
        
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out    

    # get text
    text = soup.get_text()
 
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk) 

    print sys.stdout.encoding
    print(text).encode(sys.stdout.encoding, errors='replace')

def use_lassie(url):
    pprint.pprint (lassie.fetch(url, all_images=True))
    
    
def use_rake(texts, tag_dic, term_top):
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
            keywords_new.append(keyword)
     
    print "keywords  : " + repr(keywords_new[0:30]).decode("unicode-escape")
    
    return ranked_phrases
    
    
    
    
urls = [
         #"https://www.ynet.co.il/home/0,7340,L-544,00.html", # ynet category tech
         #"https://www.ynet.co.il/articles/0,7340,L-5063952,00.html", # ynet article trump - iran
         #"https://www.nytimes.com/", # nyt home page
         "https://www.nytimes.com/2017/12/29/opinion/dont-cheer-as-the-irs-grows-weaker.html" # nyc article irs
        ]

for url in urls:
    print "Start '{0}'.".format(url) 
    utext = extract_web_page_utext(url)
    
    title, keywords, desription = use_bs(utext)
    
    clean_text = use_html2text(utext)
    
    tag_dic, term_top = use_topia(clean_text)
    
    print "[title, keywords, desription, clean_text]"
    use_rake([title, keywords, desription, clean_text], tag_dic, term_top)

    
    
    
    
    
    
