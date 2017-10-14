from django.shortcuts import render
import urllib2
import urlparse
from bs4 import BeautifulSoup
import numpy as np
import math
import random 
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

def population(num):
	chromosomes=[]
	for j in range(0,num):
		chromosomes.append([]);
		for s in range(0,10):
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

def result(request):
	if request.method == 'GET':
		string=request.GET.get('searchbox')
		string="http://google.com/search?q="+string
		url=opener.open(string)
		content=url.read()
		soup=BeautifulSoup(content,"lxml")
		title=soup.find_all("h3",{"class":"r"})
		obj=[]
		for t in title:
			x=t.find('a').get('href')
			data=urlparse.parse_qs(urlparse.urlparse(x).query)
			obj.append(scrape(t.find('a').getText(),data['q'][0]))
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
		if(fit[0]>fit[1]):
			obj=obj[c[0]==1]
			print(c[0])
		else:
			obj=obj[c[1]==1]
			print(c[1])
		return render(request,'result.html',{'context':obj})
	else:
		return render(request,'index.html')
