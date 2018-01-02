'''
Created on Dec 19, 2017

@author: eliad
'''

if __name__ == '__main__':
    pass


from celery_test import add
result = add.delay(4, 4)

print result.ready()

print result.get(timeout=1)

## Exception handling
#result.get(propagate=False) # dont propogate exception to result
#result.traceback # get Exception traceback


