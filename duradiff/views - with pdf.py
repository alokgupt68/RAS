from django.shortcuts import render
from django.http import HttpResponse
import datetime, random, calendar, sys
from datetime import date
from calendar import monthrange
from .forms import gensalary
from duradiff.models import Category, Qualification, Citymaster, Statemaster, Resource, Timesheet, Salary
from django.db.models import Sum
import decimal
from decimal import Decimal
from django.http import HttpResponse
from django.views.generic import View
from yourproject.utils import render_to_pdf

def gensal(request):
    if request.method == 'POST':  
      form = gensalary(request.POST or None)
      if form.is_valid():
        mth = int(request.POST.get('month', ''))
        yr = int(request.POST.get('year', ''))
        rid = int(request.POST.get('rid', ''))
        misc = int(request.POST.get('misc', ''))
        conv = int(request.POST.get('conv', ''))
        currentresource = Resource.objects.get(rid = rid)
        #basic = (sum([e.basicsalary for e in Resource.objects.filter(rid)]))
        basic = currentresource.basicsalary
        days=monthrange(yr,mth)[-1]
        #absentdays = Timesheet.objects.filter(rid, absent__gte=1).count() gave an error that int object is not iterable
        absentdays = Timesheet.objects.filter(rid=rid).filter(absent__gte=1).count()
        absencededuction = ((basic)/days)*absentdays
        netbasic = basic - absencededuction
        #totalOThrs = sum([e.OT for e in Timesheet.objects.filter(rid,theday__month=mth, theday__year=yr)])
        totalOThrs = Timesheet.objects.filter(rid=rid).filter(theday__year=yr).filter(theday__month=mth).aggregate(Sum('OT'))
        totalovertime = sum(totalOThrs.values())
        totalOTamt = Decimal(((basic)/(26 * 8))) * totalovertime
        totalpaybl = Decimal(misc) + Decimal(conv) + Decimal(netbasic) + totalOTamt
        pfamt = (netbasic * 12)/100
        #esiamt = Decimal((totalpaybl * 1.75))/100
        #netpaybl = totalpaybl - pfamt - esiamt
        netpaybl = totalpaybl - Decimal(pfamt)
        #sal_obj = Salary(rid=rid, month=mth, year=yr,daysinmonth = days,totalOThrs = totalOThrs, netbasic = netbasic, totalOTamt = totalOTamt,totalpaybl=totalpaybl, pfamt = pfamt, esiamt = esiamt, miscellaneous = misc, conveyance = conv, netpaybl = netpaybl,totalabsent=totalabsent,absencededuction=absencededuction)
        sal_obj = Salary(rid=currentresource, month=mth, year=yr,daysinmonth = days, netbasic = netbasic, totalOThours = totalovertime,totalOTamt=totalOTamt,totalpaybl=totalpaybl, pfamt = pfamt, miscellaneous = misc, conveyance = conv, netpaybl = netpaybl,totalabsent=absentdays,absencededuction=absencededuction)
        sal_obj.save()
    else:
        form = gensalary()
    return render(request,'duradiff/hello.html',{'form':form})
        
 class GeneratePdf(View):
     def get(self, request, *args, **kwargs):
         data = {
                   'today': datetime.date.today(), 
                   'amount': 39.99,
                   'customer_name': 'Cooper Mann',
                   'order_id': 1233434,
                }
         pdf = render_to_pdf('pdf/invoice.html', data)
         return HttpResponse(pdf, content_type='application/pdf')