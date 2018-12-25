from django.contrib import admin
import csv
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin
from duradiff.models import Category,Qualification,Citymaster,Statemaster,Resource,Timesheet,Salary
admin.site.register(Category)
admin.site.register(Qualification)
admin.site.register(Citymaster)
admin.site.register(Statemaster)
admin.site.register(Resource)
#admin.site.register(Salary)

#class ViewAdmin(ImportExportModelAdmin):
   #pass
#django-import-export is a third party app that gives import export of models in the admin using the above ImportExportModelAdmin

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
       meta = self.model._meta
       field_names = [field.name for field in meta.fields]
       response = HttpResponse(content_type='text/csv')
       response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
       writer = csv.writer(response)
       writer.writerow(field_names)
       for obj in queryset:
              row = writer.writerow([getattr(obj, field) for field in field_names])
       return response
    export_as_csv.short_description = "Export Selected"

@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin, ExportCsvMixin):
   date_hierarchy = 'theday'
   exclude = ('delta','OT',)
   fields = ('rid','theday','endday',('timeinhr','timeouthr'),('absent','fullOTday','OD'))
   list_display = ("rid","theday","endday","timeinhr","timeouthr","absent","OD","fullOTday")
   list_per_page = 10
   actions = ["export_as_csv"]
   #readonly_fields = [..., "headshot_image"]
   list_filter = ('rid','absent','fullOTday')
   #search_fields = ['theday']

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin, ExportCsvMixin):
   #date_hierarchy = 'month'
   list_display = ("rid","month","year")
   actions = ["export_as_csv"]
   list_filter = ('rid','month','year','name')


   
