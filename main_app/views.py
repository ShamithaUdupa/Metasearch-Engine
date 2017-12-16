from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import render_to_response
from multiprocessing import Pool
import urllib2
import urllib
import urlparse
from bs4 import BeautifulSoup
import numpy as np
import math
import random 
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from models import Store
from collections import OrderedDict
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
obj=[]
def population(num,doc):
	chromosomes=[]
	for j in range(0,num):
		chromosomes.append([]);
		for s in range(0,doc):
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
	
def bookmarks(request):
	if request.method == 'GET':
		var=request.GET.get('action','')
		if(var=="add"):
			p1=Store(text=request.GET.get('text'),url=request.GET.get('url'))
			p1.save()
		elif(var=="remove"):
			p2=Store.objects.filter(text=request.GET.get('text'),url=request.GET.get('url'))
			p2.delete()
		urls=Store.objects.all()
		return render(request,'bookmarks.html',{'context':urls})

def about(request):
	return render(request,'about.html')

def fitness(chromosomes,crisp):
	fit=[]
	for j in range(0,chromosomes.shape[0]):
		val=0
		for k in range(0,chromosomes.shape[1]):
			if(chromosomes[j][k]==1):
				val+=((j+1)*(crisp[k]))
		fit.append(val)
	fit=np.array(fit)
	return fit

def printfuzzy(dict_g):
	triangle = [[] for i in range(len(dict_g))]
	for i in range(len(dict_g)):
		for j in range(len(dict_g)):
			if dict_g[i][1] - dict_g[j][1] < -0.6 * len(dict_g):
				triangle[i].append([7,9,9])
			elif dict_g[i][1] - dict_g[j][1] < 0:
				triangle[i].append([5,7,9])
			elif dict_g[i][1] - dict_g[j][1] > 0.6 * len(dict_g):
				triangle[i].append([1,1,3])
			elif dict_g[i][1] - dict_g[j][1] > 0:
				triangle[i].append([1,3,5])
 			else:
				triangle[i].append([3,5,7])
	alpha = 0.5
	lam = 0.3
	alpha_cut = [[] for i in range(len(dict_g))]
	crisp = [[] for i in range(len(dict_g))]
	for i in range(len(dict_g)):
		for j in range(len(dict_g)):
			aleft = alpha * (triangle[i][j][1] - triangle[i][j][0]) + triangle[i][j][0]
			aright = triangle[i][j][2] - alpha*(triangle[i][j][2] - triangle[i][j][1])
			alpha_cut[i].append([aleft,aright])
			crisp[i].append(lam*aright+(1-lam)*aleft)	
	crisp = np.array(crisp)
	crisp = crisp*1.0/np.sum(crisp,axis=0)
	crisp = np.sum(crisp,axis=1)	
	#print triangle
	#print alpha_cut	
	print crisp
	return crisp

def merge_dict(dict_g,dict_b):
	merged = []
	for u in dict_b.items():
		if u[0] not in dict_g:
			dict_g[u[0]] = u[1] 
		
	dict_g = sorted(dict_g.iteritems(), key=lambda (k,v): (v,k))
	print dict_g
	crisp = printfuzzy(dict_g)
	for i in  dict_g:
		merged.append(scrape(i[0][0],i[0][1]))	
	return merged,crisp

class scrape:
	def __init__(self,title,link):
		self.title=title
		self.link=link

def result(request):
	if request.method == 'GET':
		searchstring=request.GET.get('searchbox')
		page=request.GET.get('page',1)
		global obj
		if page==1:
			string="http://google.com/search?q=%s&num=50" %(urllib.quote_plus(searchstring))
			string_bing="http://www.bing.com/search?q=%s&count=50&first=0" %(urllib.quote_plus(searchstring)) 
			url=opener.open(string)
			content=url.read()
			soup=BeautifulSoup(content,"lxml")
			title=soup.find_all("h3",{"class":"r"})
			dict_g={}
			rank=0
			for t in title:
				if t.find('a')!=None:
					x=t.find('a').get('href')
					data=urlparse.parse_qs(urlparse.urlparse(x).query)
					#print data['q'][0]
					if('q' in data):
						dict_g[t.find('a').getText(),data['q'][0]] = rank
						rank = rank + 1
			url=opener.open(string_bing)
			content=url.read()
			soup=BeautifulSoup(content,"lxml")
			title=soup.find_all("li",{"class":"b_algo"})
			dict_b={}
			rank=0
			for t in title:
				if t.find('a')!=None:
					x=t.find('a').get('href')
					#print data['q'][0]
					data = t.find('a').getText()			
					dict_b[data,x] = rank
					rank = rank + 1
			obj,crisp=merge_dict(dict_g,dict_b)
			chromosomes=population(2,len(obj))
			#print(chromosomes)
			c=np.array(chromosomes)
			fit=fitness(c,crisp)
			#chromosomes=selection(chromosomes,fit)
			chromosomes=crossover(chromosomes,2)
			chromosomes=mutation(chromosomes,2)
			c=np.array(chromosomes)
			fit=fitness(c,crisp)
			obj=np.array(obj)
			if(fit[0]>fit[1]):
				obj=obj[c[0]==1]
				print(c[0])
			else:
				obj=obj[c[1]==1]
				print(c[1])
			paginator=Paginator(obj,10)
			try:
				context=paginator.page(page)
			except PageNotAnInteger:
				context=paginator.page(1)
			except EmptyPage:
				context=paginator.page(paginator.num_pages)
			return render(request,'result.html',{'context':context})
		else:
			global obj
			paginator=Paginator(obj,10)
			try:
				context=paginator.page(page)
			except PageNotAnInteger:
				context=paginator.page(1)
			except EmptyPage:
				context=paginator.page(paginator.num_pages)
			return render(request,'result.html',{'context':context})
	else:
		return render(request,'index.html')
