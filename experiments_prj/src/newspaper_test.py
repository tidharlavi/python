'''
Created on Jun 9, 2018

@author: eliad
'''

import newspaper 
import logging

# logging
LOGGING_FILE_NAME = ""
loggingFormat = '%(asctime)-15s|%(levelname)s|%(name)s|%(funcName)s|%(lineno)d|%(message)s'
logging.basicConfig(level=logging.INFO, format=loggingFormat, filename=LOGGING_FILE_NAME)

log = logging.getLogger(__name__)


url = "https://www.nytimes.com/"
#url = "https://www.nytimes.com/section/business"
#url = "https://www.nytimes.com/2018/05/16/lens/what-does-gentrification-look-like-in-an-overwhelmingly-white-city.html"

if False:
    nytimes_paper = newspaper.build(url, memoize_articles=False)
    log.info(nytimes_paper.size())
    
    log.info("Category '%d':", len(nytimes_paper.category_urls()))
    for category in nytimes_paper.category_urls():
        log.info(category)
    
    log.info("Articles '%d':", len(nytimes_paper.articles))
    for article in nytimes_paper.articles:
        log.info(article.url)

    article = nytimes_paper.articles[0]
    
if True:
    article = newspaper.Article(url=url)
    
article.download()
article.parse()

log.info(article.url)
log.info(article.authors)
log.info(article.publish_date)
log.info(article.top_image)
log.info(article.images)
log.info(article.movies)
log.info(article.title)


article.nlp()
log.info(article.keywords)
log.info(article.summary)

if __name__ == '__main__':
    pass