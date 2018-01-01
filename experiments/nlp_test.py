'''
Created on Dec 31, 2017

@author: eliad
'''
import sys

from bs4 import BeautifulSoup # handle html parsing and printing

import html2text
import requests
from topia.termextract import extract 

import lassie
import pprint 

from rake_nltk import Rake


if __name__ == '__main__':
    pass


# https://github.com/ethangardner/py-keyword-extraction/blob/master/pykw.py

def extract_web_page_utext(url):  

    html_source = None
    if url == None:
        return None
    
    res = requests.get(url)
    #html_source = res.text
    
    content_type = res.headers['Content-Type'] # figure out what you just fetched
    ctype, charset = content_type.split(';')
    encoding = charset[len(' charset='):] # get the encoding
    #print encoding # ie ISO-8859-1
    
    utext = res.content.decode(encoding) # now you have unicode
    
    #html_source = utext.encode('utf8', 'ignore')
    
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
        if not any(bad_word in line for bad_word in bad_words):
            clean_result += line
    
    print "html2text clean result: ============================================================="
    print(clean_result)
           
    return clean_result
    


def use_topia(clean_result):        
    # https://pypi.python.org/pypi/topia.termextract/
    
    ### TermExtractor
    extractornlp = extract.TermExtractor()
    
    sorted_term = sorted(extractornlp(clean_result))
    
    sorted_by_count = sorted(sorted_term, key=lambda tup: tup[1])
    
    for key in sorted_by_count:
        print str(key[2]) + " -- " + str(key[1]) + " -- " + key[0] 
        
    ### Tags
    tagg = extractornlp.tagger(clean_result)
    for key in tagg:
        print key[2] + " -- " + key[1] + " -- " + key[0] 
  

def use_bs(utext):
        
    soup = BeautifulSoup(utext, 'html.parser')
    
    meta_tags = soup.findAll("meta", attrs={"name":"keywords"})
    if len(meta_tags) == 1:
        for meta_tag in meta_tags:
            if "content" in meta_tag.attrs:
                print("meta name 'keywords' = " + meta_tag["content"])
        
    desription = None
    meta_tags = soup.findAll("meta", attrs={"name":"description"})
    if len(meta_tags) == 1:
        for meta_tag in meta_tags:
            if "content" in meta_tag.attrs:
                print("meta name 'description' = " + meta_tag["content"])
                desription = meta_tag["content"]
         
    title = soup.title.string
    print("title=" + title)
    
    return title, desription
         
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
    
    
def use_rake(texts):
    ## https://github.com/csurfer/rake-nltk
    
    r = Rake() # Uses stopwords for english from NLTK, and all puntuation characters.

    #language = "he"
    #r = Rake(language) # To use it in a specific language supported by nltk.
    
    # If you want to provide your own set of stop words and punctuations to
    #r = Rake([u'\\u05d0\\u05ea'])    

    
    for text in texts:
        
        print "RAKE on len '{0}'. text: '{1}'".format(len(text), text[0:100].encode('utf-8'))
        
        r.extract_keywords_from_text(text)
    
        ranked_phrases = r.get_ranked_phrases_with_scores()
        print repr(ranked_phrases).decode("unicode-escape")
        
        word_degrees = r.get_word_degrees()
        word_degrees_sorted = sorted(word_degrees.iteritems(), key=lambda tup: tup[1], reverse=True) 
        print repr(word_degrees_sorted[0:30]).decode("unicode-escape")
        
        get_word_frequency_distribution = r.get_word_frequency_distribution()
        get_word_frequency_distribution_sorted = sorted(get_word_frequency_distribution.iteritems(), key=lambda tup: tup[1], reverse=True) 
        print repr(get_word_frequency_distribution_sorted[0:30]).decode("unicode-escape")
        
        
    
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
    
    title, desription = use_bs(utext)
    
    clean_text = use_html2text(utext)
    
    use_rake([title, desription, clean_text])

    
    
    
    
    
    
