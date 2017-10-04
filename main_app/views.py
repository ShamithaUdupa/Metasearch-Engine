from django.shortcuts import render
import urllib2
import urlparse
from bs4 import BeautifulSoup
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

# Create your views here.
def index(request):
	return render(request,'index.html')
	
class scrape:
	def __init__(self,title,link):
		self.title=title
		self.link=link
	
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
		return render(request,'result.html',{'context':obj})
	else :
		return render(request,'index.html')
