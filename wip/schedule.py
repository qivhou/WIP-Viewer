from djangosite.wip.models import JiraCatalog, JiraData, JiraFilter
from djangosite.wip.spider import JiraSpider
import datetime
import logging

def newtask_run():
    today = datetime.datetime.now().date()
    LOG_FILE="wip_"+ str(today) +".log"
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)-15s %(message)s',datefmt='%Y %b %d  %H:%M:%S ',filename=LOG_FILE,filemode='a') 
    logging.info("Start to insert today's %s data. " % str(today)) 
    # connect to Jira System
    ret = True
    jiraSpider= JiraSpider()
    jiraSpider.connect()
    if jiraSpider.isLogin : 
        #get all jiracatalogs
        catalogs = JiraCatalog.objects.filter(is_active=1) 
        for catalogObj in catalogs :
            # No need to execute below steps if today's data existing
            try :
                JiraData.objects.get(created = today,catalog=catalogObj) 
            except JiraData.DoesNotExist :
                queryDict = dict(created = today, catalog = catalogObj)
                #get default filter
                if catalogObj.default_filter !='' : 
                    defaultQuery = catalogObj.default_filter + '  AND  '
                else :
                    defaultQuery = ''                
                #check if there's a specific filters for current catalog.
                filters = JiraFilter.objects.filter(catalog = catalogObj,is_private=1)
                if filters.count():
                    is_private = 1
                else:
                    filters = JiraFilter.objects.filter(is_private=0)
                    is_private = 0

                #get all filters
                for filterObj in filters:
                    fieldName = filterObj.field_name
                    #we can get count form Jira as a default option
                    getFlag = True
                    logging.info("Fileter : %s for Catalog: %s ." % (fieldName,catalogObj.key))  
                    #is_private to execute the query defined in filter.
                    if is_private :
                        filterQuery = filterObj.query
                    else:
                        #use the public filters to combine query then get count
                        if fieldName == 'resolved_count' :
                            if catalogObj.revision_indev != '' :
                                filterQuery = filterObj.query + ' AND fixVersion in (%s) ' % catalogObj.revision_indev
                            else :
                                getFlag = False               
                        elif fieldName == 'released_count' :
                            filterQuery = filterObj.query
                            if catalogObj.revision_indev != '' :
                                filterQuery = filterQuery + ' AND fixVersion not in (%s) ' % catalogObj.revision_indev
                            if catalogObj.revision_intest != '' : 
                                filterQuery = filterQuery + ' AND fixVersion not in (%s) ' % catalogObj.revision_intest                 
                        elif fieldName == 'testing_count' :
                            if catalogObj.revision_intest != '' :                     
                                filterQuery = filterObj.query+ ' AND fixVersion in (%s) ' %  catalogObj.revision_intest
                            else :
                                getFlag = False                        
                        else : 
                            filterQuery = filterObj.query
                            
                    filterQuery = defaultQuery + filterQuery
                    if getFlag :
                        #get count by spider
                        fieldValue = jiraSpider.getCount(filterQuery)
                    else :
                        fieldValue = 0
                    queryDict[fieldName] = fieldValue
                
                #insert data to SQL DB   
                jiraData = JiraData(**queryDict)
                jiraData.save()
                logging.info("Added today's (%s) data for %s ." % (str(today),catalogObj.key))             
            else : 
                logging.info("No need to insert today's (%s) data for %s again,it already existed " % (str(today),catalogObj.key))       
        ret = True
        logging.info("Task to insert today's (%s) data Sucess." % str(today))          
    else : 
        ret = False
        logging.info("Task to insert today's (%s) data Failed." % str(today))
    return ret


def task_run():
    today = datetime.datetime.now().date()
    LOG_FILE="wip_"+ str(today) +".log"
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)-15s %(message)s',datefmt='%Y %b %d  %H:%M:%S ',filename=LOG_FILE,filemode='a') 
    logging.info("Start to insert today's %s data. " % str(today)) 
    # connect to Jira System
    ret = True
    jiraSpider= JiraSpider()
    jiraSpider.connect()
    if jiraSpider.isLogin : 
        #get all jiracatalogs
        catalogs = JiraCatalog.objects.filter(is_active=1) 
        for catalogObj in catalogs :
            # No need to execute below steps if today's data existing
            try :
                JiraData.objects.get(created = today,catalog=catalogObj) 
            except JiraData.DoesNotExist :
                queryDict = dict(created = today, catalog = catalogObj)
                #get default filter
                if catalogObj.default_filter !='' : 
                    defaultQuery = catalogObj.default_filter + '  AND  '
                else :
                    defaultQuery = ''            
                #get all filters
                for filterObj in JiraFilter.objects.all() : 
                    fieldName = filterObj.field_name
                    getFlag = True
                    logging.info("Fileter : %s for Catalog: %s ." % (fieldName,catalogObj.key))  
                    #project in (APCPRODOC ) AND resolution = Fixed and (status = Closed or status = Resolved) and fixVersion ="v03.06.00" 
                    if fieldName == 'resolved_count' :
                        if catalogObj.revision_indev != '' :
                            filterQuery = filterObj.query + ' AND fixVersion in (%s) ' % catalogObj.revision_indev
                        else :
                            getFlag = False               
                    elif fieldName == 'released_count' :
                        filterQuery = filterObj.query
                        if catalogObj.revision_indev != '' :
                            filterQuery = filterQuery + ' AND fixVersion not in (%s) ' % catalogObj.revision_indev
                        if catalogObj.revision_intest != '' : 
                            filterQuery = filterQuery + ' AND fixVersion not in (%s) ' % catalogObj.revision_intest                 
                    elif fieldName == 'testing_count' :
                        if catalogObj.revision_intest != '' :                     
                            filterQuery = filterObj.query+ ' AND fixVersion in (%s) ' %  catalogObj.revision_intest
                        else :
                            getFlag = False                        
                    else : 
                        filterQuery = filterObj.query  

                    filterQuery = defaultQuery + filterQuery        
                    if getFlag :
                        #get count by spider
                        fieldValue = jiraSpider.getCount(filterQuery)
                    else :
                        fieldValue = 0
                    queryDict[fieldName] = fieldValue
                
                #insert data to SQL DB   
                jiraData = JiraData(**queryDict)
                jiraData.save()
                logging.info("Added today's (%s) data for %s ." % (str(today),catalogObj.key))             
            else : 
                logging.info("No need to insert today's (%s) data for %s again,it already existed " % (str(today),catalogObj.key))       
        ret = True
        logging.info("Task to insert today's (%s) data Sucess." % str(today))          
    else : 
        ret = False
        logging.info("Task to insert today's (%s) data Failed." % str(today))
    return ret
