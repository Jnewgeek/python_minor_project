#coding:utf-8
'''
Created on Tue Jul 30 15:36:17 2019

@author: Allen

自定义多线程任务.
'''


import threading
from time import sleep,ctime

class MyThread(threading.Thread):

	def __init__(self,func,args,name='',prints=False):
		threading.Thread.__init__(self)
		self.name=name
		self.func=func
		self.args=args
		self.prints=prints

	def getResult(self):
		return self.res

	def run(self):
		if self.prints:print('Starting < %s > at: %s\n'%(self.name,ctime()))
		self.res=self.func(*self.args)
		if self.prints:print('< %s > finished at: %s\n'%(self.name,ctime()))