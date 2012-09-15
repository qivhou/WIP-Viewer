from django.conf.urls.defaults import *
import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.views import login, logout

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'wip.views.home'),
    (r'^wip/$', 'wip.views.home'),
    (r'^wip/home/$', 'wip.views.home'), 
    (r'^wip/data/(?P<name>\w+)/$','wip.views.data'),
    (r'^wip/data/edit/update/$','wip.views.data_update'),
    (r'^wip/catalog/edit/update/$','wip.views.catalog_update'),
    (r'^wip/filter/edit/update/$','wip.views.filter_update'),
    (r'^wip/data/json/(?P<name>\w+)/$','wip.views.data_json'), 
    (r'^wip/chart/(?P<name>\w+)/$','wip.views.chart'), 
    (r'^wip/schedule/$', 'wip.views.schedule_task'),
    (r'^wip/accounts/login/$',login,{'template_name':'login.html'}), 
    (r'^wip/accounts/logout/$',logout),
	url(r'^wip/admin/', include(admin.site.urls)),    
    (r'^home/$', 'wip.views.home'),
    (r'^data/(?P<name>\w+)/$','wip.views.data'),  
    (r'^data/edit/update/$','wip.views.data_update'),    
    (r'^catalog/edit/update/$','wip.views.catalog_update'),    
    (r'^filter/edit/update/$','wip.views.filter_update'),   
    (r'^data/json/(?P<name>\w+)/$','wip.views.data_json'),     
    (r'^chart/(?P<name>\w+)/$','wip.views.chart'),    
    (r'^schedule/$', 'wip.views.schedule_task'),    
    url(r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$',login,{'template_name':'login.html'}),  
    (r'^accounts/logout/$',logout),
    
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        (r'^wip_static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
