'''
Created on Dec 19, 2017

@author: eliad
'''

if __name__ == '__main__':
    pass



from celery import Celery

app = Celery('celery_test', backend='rpc://guest@localhost//', broker='pyamqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y


