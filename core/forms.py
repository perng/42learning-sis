from django import forms
from django.forms import ModelForm
from django.forms.fields import CharField
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple, TextInput, \
  HiddenInput

from django.forms.extras.widgets import SelectDateWidget
from sis.core.models import *

STATE_CHOICES = (('CA', 'CA'), ('NY', 'NY'), ('CT', 'CT'))
PARTICIPATION_CHOICES = (('Breakfast', 'Breakfast Club'), ('IT', 'IT Support'),
                         ('Event', 'Event Planning'))


class SchoolForm(ModelForm):
  class Meta:
    model = School
    exclude = ('admin',)


class FamilyForm(ModelForm):
  class Meta:
    model = Family
    fields = (
    'streetNumber', 'city', 'state', 'zipcode', 'homePhone', 'mobilePhone',
    'altEmail', 'parent1FirstName', 'parent1LastName', 'parent1ChineseFullName',
    'parent2FirstName', 'parent2LastName', 'parent2ChineseFullName',
    'participation')
    widgets = {'streetNumber': TextInput(attrs={'size': 60}), }


class StudentForm(ModelForm):
  class Meta:
    model = Student
    fields = ['firstName', 'lastName', 'chineseFullName', 'birthday',
              'homeLanguage', 'gender']
    widgets = {'birthday': SelectDateWidget(
      years=range(datetime.date.today().year - 2, 1960, -1))}


class UserForm(forms.ModelForm):
  class Meta:
    model = User
    exclude = ('email',)

  username = forms.EmailField(max_length=64,
                              help_text="The person's email address.")

  def clean_email(self):
    email = self.cleaned_data['username']
    return email


class SemesterForm(forms.ModelForm):
  class Meta:
    model = Semester
    fields = ['schoolYear', 'semester', 'need_enroll', 'copyFrom', 'regStart',
              'regEnd', 'recordStart', 'recordEnd']


class ClassForm(forms.ModelForm):
  class Meta:
    model = Class
    fields = ['name', 'elective', 'mandate', 'elective_required', 'headTeacher',
              'assocTeacher1', 'assocTeacher2', 'recordAttendance',
              'recordGrade', 'description']


class ClassFeeForm(forms.ModelForm):
  class Meta:
    model = Fee
    fields = ['basecc', 'basechk', 'book', 'material', 'misc', ]


class FeeConfigForm(forms.ModelForm):
  class Meta:
    model = FeeConfig
    widgets = {'semester': HiddenInput()}
    exclude = []


class HomeWorkForm(forms.ModelForm):
  class Meta:
    model = GradingItem
    fields = ['name', 'assignmentDescr', 'duedate', ]
    widgets = {'duedate': SelectDateWidget()}
