import datetime, random, calendar, sys, os, decimal, openpyxl
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.validators import *
from django.contrib import messages
import pandas as pd
import numpy as np
from pandas import ExcelWriter, ExcelFile
from os import path
from django.db.models import Sum
from django.db import IntegrityError
from decimal import Decimal
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date, timedelta, time, datetime
from calendar import monthrange
from duradiff.models import *
from .forms import gensalary, timeentryform
from django.forms import modelformset_factory
from django.views.generic import View, TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import redirect, render, render_to_response
from django.core.exceptions import ValidationError, ObjectDoesNotExist

def redirect_view(request):
    return render(request,'duradiff/inactiveres.html')
def redirectfiletype_view(request):
    return render(request,'duradiff/filetype.html')
@login_required
def gensal(request):
    if request.method == 'POST':  
      form = gensalary(request.POST or None)
      if form.is_valid():
        #mth = int(request.POST.get('month', ''))
        mth = int(form.cleaned_data['month'])
        yr = int(form.cleaned_data['year'])
        rid = int(form.cleaned_data['rid'])
        conv = int(form.cleaned_data['conv'])
        currentresource = Resource.objects.get(rid = rid)
        currentstatus = currentresource.status
        if (currentstatus == 'Inactive'):

            return redirect('inactiveres/')
            #raise form.ValidationError('Inactive RID, salary cannot be generated')
        else:
                basic = currentresource.basicsalary
                splall = currentresource.splallowance
                name = currentresource.firstname + '  ' + currentresource.lastname
                days=monthrange(yr,mth)[-1]
                # Field lookups like (gte, year, month etc..) are how you specify the meat of an SQL WHERE clause.
                # They’re specified as keyword arguments to the QuerySet methods filter(), exclude() and get().
                absentdays = Timesheet.objects.filter(rid=rid).filter(absent__gte=1).count()
                absencededuction = ((basic)/days)*absentdays
                netbasic = basic - absencededuction
                totalOThrs = Timesheet.objects.filter(rid=rid).filter(theday__year=yr).filter(theday__month=mth).aggregate(Sum('OT'))
                totalovertime = sum(totalOThrs.values())
                totalOTamt = Decimal(((basic)/(26 * 8))) * totalovertime
                totalpaybl = Decimal(splall) + Decimal(conv) + Decimal(netbasic) + totalOTamt
                pfamt = (netbasic * 12)/100
                esiamt = (Decimal(totalpaybl) * Decimal(1.75))/100
                shiftpenalty = sum(Timesheet.objects.filter(rid=rid).filter(theday__year=yr).filter(theday__month=mth).aggregate(Sum('shiftshortfall')).values()) * Decimal((basic)/(26 * 8))
                netpaybl = totalpaybl - Decimal(pfamt) - esiamt - shiftpenalty
                sal_obj = Salary(rid=currentresource, month=mth, year=yr,daysinmonth = days, netbasic = netbasic, totalOThours = totalovertime,totalOTamt=totalOTamt,totalpaybl=totalpaybl, pfamt = pfamt, esiamt=esiamt, splallowance = splall, conveyance = conv, shiftpenalty = shiftpenalty, netpaybl = netpaybl,name=name,totalabsent=absentdays,absencededuction=absencededuction)
                sal_obj.save()  
      else:
          pass
    else:
        form = gensalary()
    return render(request,'duradiff/hello.html',{'form':form})
#@login_required
#def uploadform(request):
#    if request.method == 'POST':  
#      form = uploadform(request.GET or None)
#      if form.is_valid():
#        #form = uploadform(request)
#        #sal_obj = Salary(rid=currentresource, month=mth, year=yr,daysinmonth = days, netbasic = netbasic, totalOThours = totalovertime,totalOTamt=totalOTamt,totalpaybl=totalpaybl, pfamt = pfamt, esiamt=esiamt, miscellaneous = misc, conveyance = conv, shiftpenalty = shiftpenalty, netpaybl = netpaybl,name=name,totalabsent=absentdays,absencededuction=absencededuction)
#        #sal_obj.save()
#        return
#    else:
#        form = uploadform()
#    return render(request,'duradiff/upload.html',{'form':form})
decorators = [csrf_protect, login_required]
@method_decorator(decorators, name='dispatch')
class TimeView(FormView):
    template_name = 'duradiff/timesheet.html'

    def get(self, request):
        form = timeentryform()
        return render(request, self.template_name,{'form':form})

    def post(self,request):
        form = timeentryform(request.POST or None)
        if form.is_valid():
            #temprid = form.cleaned_data['rid']
            srid = form.cleaned_data['rid']
            #Accessing Foreign Key Values
            #When you access a field that’s a ForeignKey, in this case rid of Resource model, you’ll get the related model object from the ModelForm.
            #from that you need to access the relevant field, which here is done by srid.rid
            currentresource = Resource.objects.get(rid = srid.rid)
            ridshifthrs = currentresource.shifthrs 
            # commit=False means the form doesn't save at this time.
            # the value of ridshifthrs is fetched from the Resource Model and assigned
            model_instance = form.save(commit=False)
            model_instance.ridshifthrs = ridshifthrs
            # commit defaults to True which means it normally saves.
            model_instance.save()
            #the line below actually clears out the previous form and gives you a fresh form
            form = timeentryform()
        args = {'form':form}
        return render(request, self.template_name,args)
#By default, some of Django’s class-based views like this FormView support just a single form per view and multiple forms are not supported
# So the below code did not work
#class MultipleTimeView(FormView):
#    template_name = 'duradiff/multimesheet.html'  
#    def get(self, request):
#            TimeAddformset = modelformset_factory(Timesheet,form=timeentryform, extra=15)
#            formset = TimeAddformset(queryset=Timesheet.objects.none())
#            args = {'formset':formset}
#            return render(request, 'duradiff/multimesheet.html',args)
#    def post(self,request):
#        TimeAddformset = modelformset_factory(Timesheet, form=timeentryform, extra=15)
#        formset = TimeAddformset(request.POST or None)
#        for form in formset.forms:
#          if form.is_valid():
#            srid = form.cleaned_data['rid']
#            currentresource = Resource.objects.get(rid = srid.rid)
#            ridshifthrs = currentresource.shifthrs 
#            model_instance = form.save(commit=False)
#            model_instance.ridshifthrs = ridshifthrs
#            model_instance.save()
#          args = {'form':form}
#        return render(request, 'duradiff/multimesheet.html',args)

#@login_required
#def timesheet(request):
#    if request.method == 'POST':  
#      form = timeentry(request.POST or None)
#      if form.is_valid():
#        #mth = int(request.POST.get('month', ''))
#        #yr = int(request.POST.get('year', ''))
#        #rid = int(request.POST.get('rid', ''))
#        #misc = int(request.POST.get('misc', ''))
#        #conv = int(request.POST.get('conv', ''))
#        theday = form.cleaned_data['theday']
#        timeinhr = form.cleaned_data['timeinhr']
#        rid = int(form.cleaned_data['rid'])
#        timeouthr = form.cleaned_data['timeouthr']
#        absent = form.cleaned_data['absent']
#        fullOTday = form.cleaned_data['fullOTday']
#        timesheet_obj = Timesheet(rid=rid,theday = theday,timeinhr=timeinr, timeouthr=timeouthr,absent=absent,fullOTday=fullOTday)
#        timesheet_obj.save()
#    else:
#        form = timeentry()
#    return render(request,'duradiff/timesheet.html',{'form':form})
@login_required
def upload_file(request):
    if request.method == 'GET':
        return render(request, 'duradiff/upload.html', {})
    else:
        # request.FILES is a multivalue dictionary like object that keeps the files uploaded through a upload file button. In upload.html template the name of the button (type="file") is "excel_file" so excel_file will be the key in this dictionary.
        # Note the corresponding form in upload.html must have enctype="multipart/form-data"
        # Otherwise request.FILES below will return nil in the POST request
        excel_file = request.FILES["excel_file"]
        #excel_file = request.FILES["excel_file"] has several properties
        #file.name           # Gives name
        #file.content_type   # Gives Content type text/html etc
        #file.size           # Gives file's size in byte
        #file.read()         # Reads file
        # Putting validations to check extension or file size or worksheet name
        #ext = os.path.splitext(excel_file.name)[1]
        contenttype = excel_file.content_type
        if (contenttype != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
        #if (not(ext=='.xlsx' or ext=='.xls')):
           #raise ValidationError('upload only excel files')
           #messages.warning(request,'upload only excel')
           #return redirect('http://127.0.0.1:8000/accounts/login/gensal/upload')
           return redirect('../gensal/filetype')
        else:
           df = pd.read_excel(excel_file)
        listPunchTime = (df['PunchTime'])
        listPunchDate = (df['PunchDate'])
        trid = (df['CardNo'])
        i=0
        # getting the number of rows in the bio-metric attendance sheet which should be even, as entry and exit times for a day can only be a pair
        count = len(df.index)
        # to check if the no. of entries in the bio-metric attendance sheet are even
        if count % 2 == 0:
           pass # pass statement means do nothing and move on, it is different from continue and break statements
        else:
           messages.warning(request,'Uploaded odd no. of attendance entries i.e. some unpaired attendance entries exist, pl. correct')
           return redirect('/accounts/login/gensal/upload')
        #hrsworked = []
        while i < count:
            #Removing the first character 'C' from the card no of the bio-metric attendance sheet and converting to integer type for storing rid in Timesheet model
            srid = int(trid[i][1:])
            # The two lines below are used to access the shifthrs from the Resources model for the resource whose attendance records we are adding.
            try:
               currentresource = Resource.objects.get(rid = srid)
            except ObjectDoesNotExist:
               messages.warning(request,'Biometric timesheet card entry %s does not have equivalent rid. Please make rid entry in master for it. Then before reuploading, please note that all timesheet entries above and below it have been uploaded. When reuploading first delete these entries' % trid[i], extra_tags='warning')
               #return redirect('/accounts/login/gensal/upload')
               i=i+2
               continue
               # continue takes you back to the while loop, that is why to move to the next iteration from the failed iteration, we increment i by 2, otherwise we will go into an inifinite loop if we do not increment i by 2
            ridshifthrs = currentresource.shifthrs
            endday = listPunchDate[i].date()
            theday = listPunchDate[i+1].date()
            timeouthr = listPunchTime[i]
            timeinhr = listPunchTime[i+1]
            #delta = ((datetime.combine(listPunchDate[i].date(),listPunchTime[i]) - datetime.combine(listPunchDate[i+1].date(),listPunchTime[i+1])).total_seconds())
            hrsworked = round(((datetime.combine(listPunchDate[i].date(),listPunchTime[i]) - datetime.combine(listPunchDate[i+1].date(),listPunchTime[i+1])).total_seconds())/3600,2)
            #hrsworked = ((datetime.combine(listPunchDate[i].date(),listPunchTime[i]) - datetime.combine(listPunchDate[i+1].date(),listPunchTime[i+1])).total_seconds())
            OT = round((decimal.Decimal(hrsworked) - ridshifthrs),2)
            #if (((datetime.combine(listPunchDate[i].date(),listPunchTime[i]) - datetime.combine(listPunchDate[i+1].date(),listPunchTime[i+1])) < ridshifthrs)
                #shiftshortfall = round((ridshifthrs - hrsworked),2)
            time_obj = Timesheet(rid=currentresource, theday=theday, endday = endday, timeinhr = timeinhr, timeouthr=timeouthr,hrsworked=hrsworked,OT=OT,ridshifthrs=ridshifthrs)
            try:
                time_obj.save()
                i = i + 2
            except IntegrityError:
                messages.warning(request,'This rid %s exists with that timesheet %s' % (srid, theday))
                i = i + 2
                continue
        # Pandas dataframe can be converted to html table by itself.
        messages.success(request,'File is uploaded but correct the errors, if any')
        df_html = df.to_html()
        context = {'loaded_data':df_html}
        #totalworked = sum(hrsworked)
        #context = {'hrsworked':hrsworked,'totalworked':totalworked,'srid':srid}
        return render(request, 'duradiff/upload.html', context)
@csrf_exempt
def getridname(request):
    # Expect an auto 'type' to be passed in via Ajax and POST
    if request.is_ajax() and request.method == 'POST':
      ridname = Resource.objects.get(rid=request.POST.get('rid')).rid
    
    return HttpResponse(ridname)