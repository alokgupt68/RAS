from django.contrib import admin
import csv
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin
from duradiff.models import Category,Qualification,Citymaster,Statemaster,Resource,Timesheet,Salary,Department
admin.site.register(Category)
admin.site.register(Qualification)
admin.site.register(Citymaster)
admin.site.register(Statemaster)
#admin.site.register(Resource)
admin.site.register(Department)

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
   #The function below removes the "Add Timesheet" button from custom django admin
   def has_add_permission(self, request, obj=None):
        return False
   def timesheet_resource(self,obj):
        return obj.rid
   date_hierarchy = 'theday'
   exclude = ('delta','OT',)
   fields = ('rid','theday','endday',('timeinhr','timeouthr'),('absent','fullOTday','OD'))
   list_display = ("rid","theday","endday","timeinhr","timeouthr","absent","OD","fullOTday")
   list_per_page = 10
   actions = ["export_as_csv"]
   #readonly_fields = [..., "headshot_image"]
   list_filter = ('rid','absent','fullOTday')
   #search_fields = ['=rid__rid']; note the case sensitivity is now removed from the search by removing '=' sign
   search_fields = ['rid__firstname']
   #The lines below relate to the above expression used in searching for foreign key

   """ Don't filter on a ForeignKey field itself!
Change this search_fields = ['foreinkeyfield'] to (notice TWO underscores)
search_fields = ['foreinkeyfield__name']
name represents the field-name from the table that we have a ForeinKey relationship with.'''
https://stackoverflow.com/questions/11754877/troubleshooting-related-field-has-invalid-lookup-icontains
https://stackoverflow.com/questions/45282848/exact-field-search-in-the-django-admin """

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin, ExportCsvMixin):
   #The function below removes the "Add Salary" button from custom django admin
   def has_add_permission(self, request, obj=None):
        return False
   #date_hierarchy = 'month'
   list_display = ("rid","month","year")
   actions = ["export_as_csv"]
   list_filter = ('rid','month','year','name')


@admin.register(Resource)
class ResourcedAdmin(admin.ModelAdmin, ExportCsvMixin):
   #date_hierarchy = 'month'
   list_display = ("rid","firstname","lastname","ACTIVE","basicsalary","splallowance")
   actions = ["export_as_csv"]
   list_filter = ('rid','firstname','lastname')
   search_fields = ['firstname']
