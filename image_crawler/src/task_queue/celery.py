'''
Created on Dec 20, 2017

@author: eliad
'''

from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery('task_queue',
             broker='pyamqp://guest@localhost//',
             backend='rpc://guest@localhost//',
             include=['task_queue.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    #task_always_eager=True
)

if __name__ == '__main__':
    app.start()