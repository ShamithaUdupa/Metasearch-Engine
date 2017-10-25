from django.shortcuts import render
from multiprocessing import Pool
import urllib2
import urllib
import urlparse
from bs4 import BeautifulSoup
import numpy as np
import math
import random 
from collections import OrderedDict
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

def population(num):
	chromosomes=[]
	for j in range(0,num):
		chromosomes.append([]);
		for s in range(0,15):
			a=random.random()
			if a<0.3:
				chromosomes[j].append(0)
			else:
				chromosomes[j].append(1)
	return chromosomes

def crossover(c,num):
	selected=np.random.randint(2,size=(num,))
	orig=c
	print(c)
	print(selected)
	for j in range(0,num):
		parent1=orig[selected[j]]
		parent2=orig[selected[(1+j)%num]]
		point=random.randint(0,len(c[0])-1)
		c[selected[j]]=parent1[:point]+parent2[point:]
	return c

def selection(c,fitness):
	prob=fitness/np.sum(fitness)
	chromosomes=[]
	for j in range(0,len(c)):
		r=random.uniform(0,1)
		value=0
		k=0
		for p in prob:
			value+=p
			if(value>=r):
				chromosomes.append(c[k])
				break
			k+=1
	return chromosomes

def mutation(c,num):
	selected=np.random.randint(2,size=(num,))
	for j in range(0,num):
		c[selected[j]][random.randint(0,len(c[0])-1)]=(c[selected[j]][random.randint(0,len(c[0])-1)]+1)%2
	return c
	
# Create your views here.
def index(request):
	return render(request,'index.html')
	
class scrape:
	def __init__(self,title,link):
		self.title=title
		self.link=link

def fitness(chromosomes):
	fit=[]
	for j in range(0,chromosomes.shape[0]):
		val=0
		for k in range(0,chromosomes.shape[1]):
			if(chromosomes[j][k]==1):
				val+=((j+1)*(chromosomes.shape[1]-k))
		fit.append(val)
	fit=np.array(fit)
	return fit

def merge_dict(dict_g,dict_b):
	merged = []
	for u in dict_b.items():
		if u[0] not in dict_g:
			dict_g[u[0]] = u[1] 
	
	dict_g = sorted(dict_g.iteritems(), key=lambda (k,v): (v,k))
	for i in  dict_g:
		merged.append(i[0])	
	return merged
			
def result(request):
	if request.method == 'GET':
		string=request.GET.get('searchbox')
		string_bing = "http://www.bing.com/search?q=%s" % (urllib.quote_plus(string))
		print string_bing
		string="http://google.com/search?q=%s" % (urllib.quote_plus(string))
		url=opener.open(string)
		print string
		content=url.read()
		#print content
		soup=BeautifulSoup(content,"lxml")	
		title=soup.find_all("h3",{"class":"r"})
		dict_g={}
		print title
		rank = 0		
		for t in title:
			x=t.find('a').get('href')
			data=urlparse.parse_qs(urlparse.urlparse(x).query)
			print x,'   x  \n',data,'  -----data----\n '	
			print data			
			dict_g[scrape(t.find('a').getText(),data['q'][0])] = rank
			rank = rank + 1
		
		
		url = opener.open(string_bing)
		content = url.read()
		#print content
		soup=BeautifulSoup(content,"lxml")
		#print soup.prettify()	
		title=soup.find_all("li",{"class":"b_algo"})
		dict_b = {}
		rank = 0
		for t in title:
			print t			
			x=t.find('a').get('href')	
			data = t.find('a').getText()			
			dict_b[scrape(data,x)] = rank
			rank = rank + 1

		obj = merge_dict(dict_g,dict_b)				
		print obj		
		chromosomes=population(2)
		#print(chromosomes)
		c=np.array(chromosomes)
		fit=fitness(c)
		#chromosomes=selection(chromosomes,fit)
		chromosomes=crossover(chromosomes,2)
		chromosomes=mutation(chromosomes,2)
		c=np.array(chromosomes)
		fit=fitness(c)
		obj=np.array(obj)
		print obj.shape,' ', obj
		if(fit[0]>fit[1]):
			obj=obj[np.where(c[0]==1)]
			print(c[0])
		else:
			obj=obj[np.where(c[1]==1)]
			print(c[1])
		
		return render(request,'result.html',{'context':obj})
	else:
		return render(request,'index.html')

		
