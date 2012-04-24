# Create your views here.
import json
import datetime

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.views import login, logout
from django.core.paginator import PageNotAnInteger, Paginator, InvalidPage, EmptyPage
from django.core.serializers import serialize
from django.utils.simplejson import dumps, loads, JSONEncoder
from django.db.models.query import QuerySet
from django.utils.functional import curry

from wip.schedule import task_run, newtask_run
from djangosite.wip.models import JiraCatalog, JiraData, JiraFilter

class DjangoJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuerySet):
            # `default` must return a python serializable
            # structure, the easiest way is to load the JSON
            # string produced by `serialize` and return it
            return loads(serialize('json', obj))
        return JSONEncoder.default(self,obj)

# partial function, we can now use dumps(my_dict) instead
# of dumps(my_dict, cls=DjangoJSONEncoder)
dumps = curry(dumps, cls=DjangoJSONEncoder)

def schedule_task(request):
    ret = newtask_run()
    return HttpResponse('["'+str(ret)+'"]')

def data(request,name):
    catalogObj = JiraCatalog.objects.get(key=name)
    #check if there's a specific filters for current catalog.
    filters = JiraFilter.objects.filter(catalog = catalogObj,is_private=True)
    if filters.count():
        filters = filters.order_by('seqno')
        is_private = 1
    else:
        filters = JiraFilter.objects.filter(is_private=0).order_by('seqno')
        is_private = 0
    return render_to_response('data.html', {'filters': filters,'is_private':is_private,'catalog':catalogObj})

def data_update(request):
    try:
        if request.POST.has_key('oper'):
            action = request.POST['oper']
            id = request.POST['id']
            if action == 'edit':
                catalog_id = request.POST['catalog_id']
                if id =="new_row":
                    # add a new record
                    record = JiraData(catalog = JiraCatalog.objects.get(id=catalog_id))
                    ret = '[true,"added successuful!",""]'                
                else:
                    # updated exsisting record
                    record = JiraData.objects.get(id=id)
                    if not record:
                        catalog_id = request.POST['catalog_id']
                        record = JiraData(catalog = JiraCatalog.objects.get(id=catalog_id))
                        ret = '[true,"added successuful!",""]'  
                    else:
                        ret = '[true,"updated successuful!",""]'  
                record.created = datetime.datetime.strptime(request.POST['fields.created'],"%Y-%m-%d")
                record.analysis_count = request.POST['fields.analysis_count']
                record.ready_count = request.POST['fields.ready_count']
                record.indev_count = request.POST['fields.indev_count']
                record.blocked_count = request.POST['fields.blocked_count']
                record.resolved_count = request.POST['fields.resolved_count']
                record.removed_count = request.POST['fields.removed_count']
                record.testing_count = request.POST['fields.testing_count']
                record.released_count = request.POST['fields.released_count']
                record.total_count = request.POST['fields.total_count']               
                record.save() 
            elif action == 'del':
                #delete existing record
                record = JiraData.objects.get(id=id)
                if record:
                    record.delete()
                    ret = '[true,"removed successuful!",""]'
                else:
                    ret = '[false,"there''s no record!",""]'
        else:
            ret = '[false,"No parameter oper!",""]'
    except:
        ret = '[false,"Please try it again!",""]'    
    return HttpResponse(ret)

def catalog_update(request):
    try:
        if request.POST.has_key('id'):
            #do update for existing record
            id = request.POST['id']
            record = JiraCatalog.objects.get(id=id)
            if record :             
                ret = '[true,"updated successuful!",""]'   
            else:
                record = JiraCatalog(id=id)
                ret = '[true,"added successuful!",""]'                
        else:
            record = JiraCatalog()
            ret = '[true,"added successuful!",""]'              
        record.name = str(request.POST['catalog_name'])
        record.key = str(request.POST['catalog_key'])
        record.webproducer = str(request.POST['catalog_webproducer'])
        record.developers = str(request.POST['catalog_developers'])
        record.revision_indev = str(request.POST['catalog_revision_indev'])
        record.revision_intest = str(request.POST['catalog_revision_intest'])
        record.url = str(request.POST['catalog_url'])
        record.default_filter = str(request.POST['catalog_default_filter'])
        record.save()         
    except:
        ret = '[false,"Please try it again!",""]'
    return HttpResponse(ret)

def filter_update(request):
    if request.POST.has_key('id'):
        #do update for existing record
        id = request.POST['id']
        catalog = JiraCatalog.objects.filter(id=id)[0]
        filter_list=['analysis','ready','released','resolved','testing','indev','blocked','removed','total']
        for keyword in filter_list:
            filters = JiraFilter.objects.filter(catalog=catalog,key=keyword,is_private=True)
            n = JiraFilter.objects.all().count()
            if filters.count():
                filter = filters[0]
                filter.query = request.POST[keyword]
                filter.save()
            else:
                queryDict = dict()
                queryDict['key'] = keyword
                queryDict['query'] = request.POST[keyword]
                queryDict['field_name'] = keyword+"_count"
                queryDict['description'] = ""                   
                queryDict['catalog'] = catalog
                queryDict['is_private'] = True
                queryDict['seqno'] = n+1                
                filter = JiraFilter(**queryDict)
                filter.save()              
        ret = '[true,"updated successuful!",""]'               
    else:
        ret = '[false,"No catalog ID!",""]'            
    return HttpResponse(ret)
    
def chart(request,name):
    catalogObj = JiraCatalog.objects.filter(key=name)[0]
    records = JiraData.objects.filter(catalog=catalogObj).order_by('-created')
    return render_to_response('chart.html', {'catalog':catalogObj,'records':dumps(records)})

def data_json(request,name):
    catalogObj = JiraCatalog.objects.filter(key=name)[0]
    #filtered by created
    if request.GET.has_key('start_date') and request.GET.has_key('end_date'):
        records = JiraData.objects.filter(catalog=catalogObj,created__gte = request.GET['start_date'], created__lte = request.GET['end_date']).order_by('-created')
    else :
        records = JiraData.objects.filter(catalog=catalogObj).order_by('-created')

    if not request.GET.has_key('page'):
        pagenum = 1
    else:
        if request.GET['page']:
            pagenum = int(request.GET['page'])
        else:
            pagenum = 1 
            
    if not request.GET.has_key('rows'):
        rownum = 15
    else:
        if request.GET['rows']:
            #get all records for jqchart
            if request.GET['rows'] == 'all':
                rownum = records.count()
            else :
                rownum = int(request.GET['rows'])
        else:
            rownum = 15

    paginator = Paginator(records,rownum)    
    try:
        jsonlist = paginator.page(pagenum).object_list
    except(EmptyPage,InvalidPage,PageNotAnInteger):
        jsonlist = paginator.page(paginator.num_pages).object_list
    return HttpResponse('{"root":'+dumps(jsonlist)+',"total":"'+str(paginator.num_pages)+'","page":"'+str(pagenum)+'","records":"'+str(records.count())+'"}')    
    
def home(request):
    catalogs = JiraCatalog.objects.filter(is_active=1).order_by('seqno')
    latest = JiraData.objects.order_by('-created')[0]
    records = JiraData.objects.filter(created = latest.created)
    return render_to_response('index.html',{'catalogs':catalogs,'records':records,'latest_day':latest.created})

