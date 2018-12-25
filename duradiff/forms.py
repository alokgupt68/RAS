from django import forms
from django.forms import widgets
from django.contrib.admin import widgets
#from django.contrib.admin.widgets import AdminDateWidget
from duradiff.models import Salary, Timesheet, Resource
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (
    PrependedText, PrependedAppendedText, AppendedText, FormActions)

CHOICES = ((None,'Select month'),('1','JAN'), ('2','FEB'),('3','MAR'),('4','APR'),('5','MAY'),('6','JUN'),('7','JUL'),('8','AUG'),('9','SEP'),('10','OCT'),('11','NOV'),('12','DEC'))
 
class gensalary(forms.Form):
    month = forms.ChoiceField(choices=CHOICES)
    def clean_month(self):
      value = self.cleaned_data['month']
      return int(value)
    year = forms.IntegerField(label='Year:')
    rid = forms.IntegerField(label='rid:')
    #misc = forms.IntegerField(label='misc:')
    conv = forms.IntegerField(label='conv:')
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-2'
    helper.form_show_errors = True
    #helper.error_text_inline = True
    helper.layout = Layout(
        Field('month',css_class='input-sm'),
        Field('year', css_class='input-sm'),
        Field('rid', css_class='input-sm'),
        PrependedText('conv', '<b>₹ </b>', placeholder="Conveyance "),
        FormActions(Submit('Calculate Salary', 'Calculate Salary', css_class='btn-primary'))
    )
    
#class timeentryform(forms.Form):
#    rid = forms.IntegerField(label='rid:')
#    theday = forms.DateField(label='theday:')
#    timeinhr = forms.TimeField(label='timeinhr')
#    timeouthr = forms.TimeField(label='timeouthr')
#    absent = forms.BooleanField(label = 'absent',required = False)
#    fullOTday = forms.BooleanField(label = 'fullOTday',required = False)
#    helper = FormHelper()
#    helper.form_method = 'POST'
#    helper.form_class = 'form-horizontal'
#    helper.label_class = 'col-sm-2'
#    helper.field_class = 'col-sm-2'
#    helper.layout = Layout(
#        Field('rid',css_class='input-sm'),
#        Field('theday', css_class='input-sm'),
#        Field('timeinhr', css_class='input-sm'),
#        Field('timeouthr', css_class='input-sm'),
#        Field('absent', css_class='input-sm'),
#        Field('fullOTday', css_class='input-sm'),
#        FormActions(Submit('Submit', 'Submit', css_class='btn-primary'))
#    )

class timeentryform(forms.ModelForm):
    rid = forms.ModelChoiceField(queryset=Resource.objects.all(), widget=forms.TextInput(attrs={'onchange':'get_name();'}), label="rid")
    #theday = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    # You can disable autocomplete on such fields by setting the HTML5 autocomplete attribute to off. 
    # To achieve this in Django's forms you need to pass additional information to the widget for each input,
    theday = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS,widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    endday = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS,widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    #self.fields['theday'].widget = widgets.AdminDateWidget()
    timeinhr = forms.TimeField(required = False)
    timeouthr  = forms.TimeField(required = False)
    absent = forms.BooleanField(required = False)
    fullOTday = forms.BooleanField(required = False)
    OD = forms.BooleanField(required = False)
    class Meta:
        model = Timesheet
        fields = ['rid','theday','endday','timeinhr','timeouthr','absent','fullOTday','OD']

