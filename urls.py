from django.conf.urls.defaults import *
import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.views import login, logout

admin.autodiscover()

urlpatterns = patterns('',
#    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATICFILES_DIRS}),
    (r'^schedule/$', 'wip.views.schedule_task'),
    (r'^$', 'wip.views.home'),
    (r'^home/$', 'wip.views.home'),
    (r'^data/(?P<name>\w+)/$','wip.views.data'),
    (r'^data/edit/update/$','wip.views.data_update'),
    (r'^catalog/edit/update/$','wip.views.catalog_update'),
    (r'^filter/edit/update/$','wip.views.filter_update'),
    (r'^data/json/(?P<name>\w+)/$','wip.views.data_json'), 
    (r'^chart/(?P<name>\w+)/$','wip.views.chart'),
    (r'^accounts/login/$',login,{'template_name':'login.html'}),
    (r'^accounts/logout/$',logout),
    url(r'^admin/', include(admin.site.urls)),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATICFILES_DIRS}),
    )
