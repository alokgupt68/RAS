from django.db import models
from datetime import date, time, datetime, timedelta
import decimal
from decimal import Decimal

class Category(models.Model):
    skill = models.CharField(max_length=25)
    def __str__(self):
          return self.skill
    class Meta:
           verbose_name_plural = "Categories"

class Qualification(models.Model):
    jobtitle = models.CharField(max_length=25)
    def __str__(self):
          return self.jobtitle

class Department(models.Model):
    Dept = models.CharField(max_length=25)
    def __str__(self):
          return self.Dept

class Statemaster(models.Model):
    state = models.CharField(max_length=25)
    def __str__(self):
          return self.state
    class Meta:
           verbose_name_plural = "States"

class Citymaster(models.Model):
    city = models.CharField(max_length=25)
    state = models.ForeignKey(Statemaster, on_delete = models.CASCADE,default='')
    def __str__(self):
          return self.city
    class Meta:
           verbose_name_plural = "Cities"

class Resource(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    GENDER_CHOICES = ((MALE, 'Male'), (FEMALE, 'Female'),)
    ACTIVE_STATUS = ((ACTIVE, 'Active'), (INACTIVE, 'Inactive'),)
    rid = models.IntegerField(primary_key=True)
    firstname = models.CharField(max_length = 45)
    lastname = models.CharField(max_length = 45, blank=True)
    parentname = models.CharField(max_length = 45, blank=True)
    dateofbirth = models.DateField(blank=True, null=True) 
    mobileno = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=8, choices=ACTIVE_STATUS, default=ACTIVE)
    gender = models.CharField(max_length=2,choices=GENDER_CHOICES,default=MALE)
    UAN = models.CharField(max_length = 45, blank=True)
    ESIno = models.CharField(max_length = 45, blank=True)
    shifthrs = models.DecimalField(max_digits=5, decimal_places=2,blank= False,default = 0)
    basicsalary = models.IntegerField(blank=False)
    splallowance = models.DecimalField(max_digits=8, decimal_places=2,blank= False,default = 0,verbose_name = 'Special Allowance')
    skill = models.ForeignKey(Category, on_delete = models.CASCADE)
    jobtitle = models.ForeignKey(Qualification, on_delete = models.CASCADE)
    Dept = models.ForeignKey(Department, on_delete = models.CASCADE, default=1, null=True)
    state = models.ForeignKey(Statemaster, on_delete = models.CASCADE)
    city = models.ForeignKey(Citymaster, on_delete = models.CASCADE)
    #Approvalnote = models.FileField(null = True, blank=True)
    Remarks = models.CharField(max_length = 70, blank=True)
    
    def __str__(self):
        return '%s %s' % (self.firstname, self.lastname)

    def save(self, *args, **kwargs):
        super(Resource, self).save(*args, **kwargs)
        #filename = self.Approvalnote.url
        # Do anything you'd like with the data in filename

class Timesheet(models.Model):
    rid = models.ForeignKey(Resource, on_delete = models.CASCADE)
    theday = models.DateField(blank=True, null=True)
    endday = models.DateField(blank=True, null=True)
    timeinhr = models.TimeField('%H:%M',blank=True, null=True)
    timeouthr = models.TimeField('%H:%M',blank=True, null=True)
    # is the delta field truly needed? It is only an interim calculation for hrsworked field.
    delta = models.DurationField(blank=True,null=True)
    hrsworked = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
    OT = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
    absent = models.BooleanField(default=False)
    fullOTday = models.BooleanField(default=False)
    OD = models.BooleanField(default=False)
    shiftshortfall = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
    #shiftpenalty = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
    ridshifthrs = models.DecimalField(max_digits=5, decimal_places=2,blank= False,default = 0)
    def __str__(self):
        return '%s' % (self.rid)
    
    def save(self, *args, **kwargs):
        if (self.OD == True):
          self.hrsworked = self.ridshifthrs
          self.OT = 0
        if (self.absent == True):
          #the next two lines just initialize the in and out time to the same time in case of an absence
          # strptime function returns a datetime corresponding to date_string, parsed according to format. 
          self.timeinhr = datetime.strptime('00:00', '%H:%M').time()
          self.timeouthr = datetime.strptime('00:00', '%H:%M').time()
          self.delta = datetime.combine(date.today(), self.timeouthr) - datetime.combine(date.today(), self.timeinhr)
          self.hrsworked = self.delta.total_seconds()/3600
          self.OT = 0
        super(Timesheet,self).save(*args,**kwargs)
        if (self.fullOTday == True):
                if (self.timeinhr < self.timeouthr):
                  # date.today() returns today's date in yyyy-mm-dd format and is used below only to calculate the time difference between in and out times
                  #self.delta = datetime.combine(date.today(), self.timeouthr) - datetime.combine(date.today(), self.timeinhr)
                  #self.hrsworked = self.delta.total_seconds()/3600
                  self.hrsworked = round(((datetime.combine(self.endday,self.timeouthr) - datetime.combine(self.theday,self.timeinhr)).total_seconds())/3600,2)
                  self.OT = self.hrsworked
                else:
              #the next line is used to cater to night shift for e.g. timein is 20:00 and timeout is 08:00 on the next day
              #so the datetime.combine function is given an argument of date.today()+timedelta(days=1) for the timeouthr
              #to denote the next day
                  #self.delta = datetime.combine(date.today()+ timedelta(days=1), self.timeouthr) - datetime.combine(date.today(), self.timeinhr)
                  #self.hrsworked = self.delta.total_seconds()/3600
                  self.hrsworked = round(((datetime.combine(self.endday,self.timeouthr) - datetime.combine(self.theday,self.timeinhr)).total_seconds())/3600,2)
                  self.OT = self.hrsworked
        super(Timesheet,self).save(*args,**kwargs)

        if (self.absent != True and self.fullOTday != True and self.OD != True):
          if (self.timeinhr < self.timeouthr):
              #self.delta = datetime.combine(date.today(), self.timeouthr) - datetime.combine(date.today(), self.timeinhr)
              #self.hrsworked = self.delta.total_seconds()/3600
              self.hrsworked = round(((datetime.combine(self.endday,self.timeouthr) - datetime.combine(self.theday,self.timeinhr)).total_seconds())/3600,2)
          else:
              #same comment as above
              self.hrsworked = round(((datetime.combine(self.endday,self.timeouthr) - datetime.combine(self.theday,self.timeinhr)).total_seconds())/3600,2)
          if (self.hrsworked <= self.ridshifthrs):
              self.OT = 0
              self.shiftshortfall = self.ridshifthrs - decimal.Decimal(self.hrsworked)
              ## insert lines for calculating incomplete shift hours
          else:
              self.shiftshortfall = 0
              self.OT = decimal.Decimal(self.hrsworked) - self.ridshifthrs
        super(Timesheet,self).save(*args,**kwargs)
    class Meta:
          unique_together = (("rid", "theday"),)

class Salary(models.Model):
    rid = models.ForeignKey(Resource, on_delete = models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    daysinmonth = models.IntegerField()
    name =  models.CharField(max_length = 45, default=' ')
    pfamt = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True, verbose_name = 'PF amt')
    esiamt = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True,verbose_name = 'ESI amt')
    totalOThours = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True)
    netbasic = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True)
    totalOTamt = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True)
    totalpaybl = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True)
    netpaybl = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True)
    splallowance = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True)
    conveyance = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True)
    totalabsent = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True)
    absencededuction = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True, verbose_name = 'absence deduction')
    shiftpenalty = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
    class Meta:
            verbose_name_plural = "Salaries"