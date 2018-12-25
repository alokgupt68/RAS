from django.urls import path, include
from . import views
from duradiff.views import TimeView
app_name = 'duradiff'
urlpatterns = [
	    path('gensal/', views.gensal),
        path('upload/', views.upload_file),
        #path('multimesheet/',MultipleTimeView.as_view()),
        path('timesheet/', TimeView.as_view()),
        path('timesheet/timesheet/ajax/', views.getridname),
        path('admin_tools/',include('admin_tools.urls')),
        path('gensal/inactiveres/',views.redirect_view),
        ]
         
             
        