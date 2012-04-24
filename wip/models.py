from django.db import models
import json

class JiraCatalog(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    seqno = models.IntegerField(blank = True)
    webproducer = models.CharField(max_length=100)
    developers = models.CharField(max_length=100)
    revision_indev = models.CharField(max_length=100,blank=True)
    revision_intest = models.CharField(max_length=100,blank=True)
    url = models.URLField(blank=True)
    default_filter = models.CharField(max_length=300,blank=True)
    is_active = models.BooleanField()   
    def __unicode__(self):
        return self.key
        
class JiraData(models.Model):
    created = models.DateField()
    catalog = models.ForeignKey(JiraCatalog)
    analysis_count = models.IntegerField()
    ready_count = models.IntegerField()
    indev_count = models.IntegerField()
    blocked_count = models.IntegerField()
    resolved_count = models.IntegerField()
    removed_count = models.IntegerField()
    testing_count = models.IntegerField()
    released_count = models.IntegerField()
    total_count = models.IntegerField()

class JiraFilter(models.Model):
    seqno = models.IntegerField()
    key = models.CharField(max_length=20)
    query = models.CharField(max_length=100)
    field_name = models.CharField(max_length=20)    
    description = models.CharField(max_length=100,blank=True)
    catalog = models.ForeignKey(JiraCatalog)
    is_private = models.BooleanField()    
    def __unicode__(self):
        return self.query
 