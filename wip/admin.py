from django.contrib import admin
from djangosite.wip.models import JiraCatalog, JiraData, JiraFilter

class JiraCatalogAdmin(admin.ModelAdmin):
	list_display = ('seqno','name', 'key', 'webproducer','developers','revision_indev','revision_intest','is_active','default_filter')
	search_fields = ('name', 'key')

class JiraDataAdmin(admin.ModelAdmin):
	list_display = ('created','catalog', 'analysis_count', 'ready_count','indev_count','blocked_count','resolved_count','removed_count','testing_count','released_count','total_count')
	date_hierarchy = 'created'
	ordering = ('-created','catalog')
	raw_id_fields = ('catalog',)
	readonly_fields = ('created', 'catalog')
	
class JiraFilterAdmin(admin.ModelAdmin):
	list_display = ('seqno','catalog','key', 'query','field_name','is_private')

admin.site.register(JiraCatalog,JiraCatalogAdmin)
admin.site.register(JiraData,JiraDataAdmin)
admin.site.register(JiraFilter,JiraFilterAdmin)