from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Store(models.Model):
	text=models.CharField(max_length=50,null=True)
	url=models.URLField(null=True)
	def __unicode__(self):
		return unicode(self.text) or u''
