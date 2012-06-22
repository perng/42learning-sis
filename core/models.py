import datetime,base64,os
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from operator import  attrgetter #, itemgetter

from django.contrib.localflavor.us.models import  PhoneNumberField #, USPostalCodeField
from sis.core.util import id_encode, det_encode


this_year = datetime.date.today().year
BIRTH_YEAR_CHOICES = tuple([(str(n), str(n)) for n in range(this_year - 22, this_year - 2)])
SEMESTER_YEAR_CHOICES = tuple([(str(n), str(n)) for n in range(this_year - 1, this_year + 3)])

MONTH_CHOICES = ((1, 'Jan'), (2, 'Feb'), (3, 'Mar'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'),
        (9, 'Sep'), (10, 'Oct'), (11, 'Nov'), (12, 'Dec'))
DAY_CHOICES = tuple([(n, n) for n in range(1, 32)])
SEMESTER_CHOICES = (('Fall', 'Fall'), ('Spring', 'Spring'), ('Summer', 'Summer'))
STATE_CHOICES = (('NY', 'NY'), ('CT', 'CT'))


class School(models.Model):
    name = models.CharField(max_length=30, verbose_name='School Name')
    domain = models.CharField( max_length=100)

    chineseName = models.CharField(max_length=30, verbose_name='Chinese Name', blank=True, default='')
    location = models.TextField(null=True, blank=True)
    mailStop = models.TextField(null=True, blank=True)
    phone = PhoneNumberField(help_text='Home Phone',null=True, blank=True)
    
    #adminEmail = models.EmailField(blank=True, help_text='Principal email')
    #deanEmail = models.EmailField(blank=True, help_text='Dean email')
    #registrarEmail = models.EmailField(blank=True, help_text='Registrar email')
    #treasurerEmail = models.EmailField(blank=True, help_text='Treasurer email')
    policy = models.TextField(null=True, blank=True)
    createDate = models.DateField(auto_now_add=True)
    banner=models.FileField(upload_to = 'school%y%m%d%H%M%S/', null=True, blank=True)
    logo=models.FileField(upload_to = 'school%y%m%d%H%M%S/', null=True, blank=True)
    admin=models.ForeignKey(User, null=True)
    
    def eid(self):
        return id_encode(self.id)

    def det_id(self):
        return det_encode(self.id) 
    def __repr__(self):
        return self.name

class Semester(models.Model):
    school = models.ForeignKey(School)
    schoolYear = models.CharField(max_length=20, choices=SEMESTER_YEAR_CHOICES)
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES)
    need_enroll = models.BooleanField()   # If enrollment is needed. set false to 2nd semester which has not change
    regStart = models.DateField(null=True, verbose_name='Registration Start Data', help_text='Format: YYYY-MM-DD')
    regEnd = models.DateField(null=True, verbose_name='Registration End Data', help_text='Format: YYYY-MM-DD')
    recordStart = models.DateField(null=True, verbose_name='Score recording start data', help_text='Format: YYYY-MM-DD')
    recordEnd = models.DateField(null=True, verbose_name='Score recording end data', help_text='Format: YYYY-MM-DD')
    copyFrom = models.ForeignKey('Semester', null=True, blank=True, related_name="previous", help_text="Copy semester setting from") # The previous semester with same classes

    def eid(self):
        return id_encode(self.id)

    def __repr__(self):
        return self.schoolYear + ' ' + self.semester
    def __str__(self):
        return self.schoolYear + ' ' + self.semester
    class Meta:
        unique_together = (('schoolYear', 'semester'))


class Family(models.Model):
    school = models.ForeignKey(School)
    user = models.OneToOneField(User)
    staff_role = models.CharField(max_length=50)
    streetNumber = models.CharField(max_length=50, help_text='Street')
    city = models.CharField(max_length=50, help_text='City')
    state = models.CharField(choices=STATE_CHOICES, max_length=3, help_text='State')
    zipcode = models.CharField(max_length=10, help_text='Zip Code')
    homePhone = PhoneNumberField(help_text='Home Phone')
    mobilePhone = PhoneNumberField(blank=True, help_text='Cell Phone')
    altEmail = models.EmailField(blank=True, help_text='Alt. Email')
    parent1FirstName = models.CharField(max_length=20, help_text='First Name')
    parent1LastName = models.CharField(max_length=20, help_text='Last Name')
    parent1ChineseFullName = models.CharField(blank=True, max_length=20, help_text='Chinese Name')
    parent2FirstName = models.CharField(blank=True, max_length=20, help_text='First Name')
    parent2LastName = models.CharField(blank=True, max_length=20, help_text='Last Name')
    parent2ChineseFullName = models.CharField(blank=True, max_length=20, help_text='Chinese Name')
    participation = models.CharField(blank=True, max_length=20, help_text='Participation')
    enroll = models.ManyToManyField('Semester', through='Tuition')

    def eid(self):
        return id_encode(self.id)

    def teaches(self,request):
        semester = current_reg_semester(request)
        classes = list(Class.objects.filter(Q(semester=semester) &(Q(headTeacher=self) | Q(assocTeacher1=self) | Q(assocTeacher2=self))))
        classes.sort(key=attrgetter('name'))
        return classes
    def is_parent(self):
        return self.student_set.all()
    def is_teacher(self):
        return self.teaches()
    def is_admin(self):
        return self.user.is_superuser
    def parent1(self):
        return self.parent1FirstName + ' ' + self.parent1LastName
    def parent1_fullname(self):
        return self.parent1FirstName + ' ' + self.parent1LastName + ("("+self.parent1ChineseFullName+")"  if self.parent1ChineseFullName else '')
        
    
    def parent2(self):
        return self.parent2FirstName + ' ' + self.parent2LastName+ ("("+self.parent2ChineseFullName+")"  if self.parent2ChineseFullName else '')
    def address(self):
        return ','.join([self.streetNumber, self.city, self.state, self.zipcode])

ROLE_CHOICES =(('School Admin', 'School Admin'), ('Dean', 'Dean'), ('Registrar', 'Registrar'))

class Staff(models.Model):
    family = models.ForeignKey(Family)
    title = models.CharField(max_length=30, verbose_name='Title')

    firstName = models.CharField(max_length=30, verbose_name='First Name')
    lastName = models.CharField(max_length=30, verbose_name='Last Name')
    chineseFullName = models.CharField(max_length=30, verbose_name='Chinese Full Name', blank=True, default='')
    bio = models.TextField()
    roles = models.ManyToManyField('Role')

class Role(models.Model):
    user= models.OneToOneField(User)
    is_admin = models.BooleanField(default=False)
    is_dean = models.BooleanField(default=False)
    is_registrar = models.BooleanField(default=False)
    is_staff1 = models.BooleanField(default=False)
    is_staff2 = models.BooleanField(default=False)

LANG_CHOICES = (('English', 'English'), ('Mandarin', 'Mandarin'), ('Cantonese', 'Cantonese'), ('Other', 'Other'))
GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))
class Student(models.Model):
    studentID = models.CharField(max_length=20)
    firstName = models.CharField(max_length=30, verbose_name='First Name')
    lastName = models.CharField(max_length=30, verbose_name='Last Name')
    chineseFullName = models.CharField(max_length=30, verbose_name='Chinese Full Name', blank=True, default='')
    birthday = models.DateField(null=True, verbose_name='Birthday', help_text='Format: YYYY-MM-DD')
    homeLanguage = models.CharField(max_length=15, choices=LANG_CHOICES, verbose_name='Home Language')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    family = models.ForeignKey(Family)
    enroll = models.ManyToManyField('Class'  , through='EnrollDetail')
    def eid(self):
        return id_encode(self.id)
    def __str__(self):
        return self.firstName + ' ' + self.lastName
    class Meta:
        unique_together = (('firstName', 'birthday', 'family'))

class Class(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(default='', null=True,blank=True)
    semester = models.ForeignKey(Semester)
    elective = models.BooleanField(default=False, help_text="check if this is an elective")
    headTeacher = models.ForeignKey(User, related_name='HeadTeacher', null=True, blank=True)
    assocTeacher1 = models.ForeignKey(User, related_name='AssocTeacher1', null=True, blank=True)
    assocTeacher2 = models.ForeignKey(User, related_name='AssocTeacher2', null=True, blank=True)
    recordAttendance = models.BooleanField(default=True)
    recordGrade = models.BooleanField(default=True)
    
    mandate=models.ForeignKey('Class', related_name='mandate_class', null=True, blank=True, 
                                help_text='The class needs to be taken with this one')

    elective_required=models.BooleanField(verbose_name="Elective req'd", default=False, help_text='Required to take an elective class')
    #gradingCategories = models.ManyToManyField('GradingCategory')
    total_ready = models.BooleanField(default=False)
    highest = models.FloatField(null=True)
    lowest = models.FloatField(null=True)
    average = models.FloatField(null=True)
    median = models.FloatField(null=True)
    def __str__(self):
        return self.name
    def num_students(self):
        return len(self.student_set.all())
    class Meta:
        unique_together = (('name', 'semester'))
    def eid(self):
        return id_encode(self.id)

    def assignment_categories(self):
        return GradingCategory.objects.filter(classPtr=self, hasAssignment=True)
    def discounted_base_cc(self):
            return self.fee.basecc - self.fee.mdiscount
    def discounted_base_chk(self):
            return self.fee.basechk - self.fee.mdiscount
        

class EnrollDetail(models.Model):
    student = models.ForeignKey(Student)
    classPtr = models.ForeignKey(Class)
    final_score = models.FloatField(null=True)
    rank = models.IntegerField(null=True)
    note = models.TextField()
    class Meta:
        unique_together = (('student', 'classPtr'))
    def eid(self):
        return id_encode(self.id)


class Award(models.Model):
    student = models.ForeignKey(Student)
    semester = models.ForeignKey(Semester)
    classPtr = models.ForeignKey(Class, null=True)
    awardDescription = models.TextField(blank=False)
    deleted = models.BooleanField(default=False)
    def eid(self):
        return id_encode(self.id)

class GradingCategory(models.Model):
    classPtr = models.ForeignKey(Class)
    name = models.CharField(max_length=64)
    order = models.IntegerField(null=True)
    weight = models.IntegerField()
    hasAssignment = models.BooleanField(default=False)
    def eid(self):
        return id_encode(self.id)
    
class GradingItem(models.Model):
    name = models.CharField(max_length=64)
    students = models.ManyToManyField(Student, through='Score')
    date = models.DateField(null=True, verbose_name='Test/Grading date', help_text='Format: YYYY-MM-DD')
    category = models.ForeignKey(GradingCategory)
    highest = models.FloatField(null=True)
    lowest = models.FloatField(null=True)
    average = models.FloatField(null=True)
    median = models.FloatField(null=True)
    assignmentDescr = models.TextField(blank=True, default='')
    duedate = models.DateField(null=True, verbose_name='Due date', help_text='Format: YYYY-MM-DD')

    class Meta:
        unique_together = (('name', 'category'))

    def hasAssignment(self):
        return self.category.hasAssignment
    def eid(self):
        return id_encode(self.id)
    
    def download_path(self):
        path='/'.join([self.category.classPtr.semester.semester+ ' '+self.category.classPtr.semester.schoolYear,
                           self.category.classPtr.name,self.category.name,
                           self.name])       
        for c in '\:*?"<>|':
            path = path.replace(c,'')
        return  path
    def create_download_dir(self):
        path=self.download_path()
        path=path.replace(' ',r'\ ')
        os.system('ssh staff@homework.nwcsny.org mkdir -p "/home/staff/homework/%s"' %( path,))

    def download_url(self):
        path=self.download_path()
        b='http://homework.nwcsny.org/index.php?folder=' 
        
        encoded_path=base64.b64encode(path)
        return b+encoded_path

class Score(models.Model):
    student = models.ForeignKey(Student)
    gradingItem = models.ForeignKey(GradingItem)
    score = models.FloatField(null=True)
    def eid(self):
        return id_encode(self.id)


class ClassSession(models.Model):
    classPtr = models.ForeignKey(Class)
    date = models.DateField(null=True, verbose_name='Date', help_text='Format: YYYY-MM-DD')
    def eid(self):
        return id_encode(self.id)

ATT_CHOICES = (('-', '-'), ('P', 'P'), ('A', 'A'), ('L', 'L'), ('E', 'E'))

class Attendance(models.Model):
    student = models.ForeignKey(Student)
    session = models.ForeignKey(ClassSession)
    attended = models.CharField(max_length=6, default='', choices=ATT_CHOICES)
    def eid(self):
        return id_encode(self.id)

class Fee(models.Model):
    ''' Difference only in base fee'''
    basecc = models.FloatField(default=0)
    basechk = models.FloatField(default=0)
    book = models.FloatField(default=0)
    material = models.FloatField(default=0)
    misc = models.FloatField(default=0)
    mdiscount = models.FloatField(default=0, help_text='Discount when taking with a language class')
    classPtr = models.OneToOneField(Class)
    def eid(self):
        return id_encode(self.id)


class FeeConfig(models.Model):
    semester = models.OneToOneField(Semester)
    discount1 = models.FloatField(default=0, help_text='Discount for 1 student')
    discount2 = models.FloatField(default=0, help_text='Discount for 2 students')
    discount3 = models.FloatField(default=0, help_text='Discount for 3 students')
    discount4 = models.FloatField(default=0, help_text='Discount for 4 students')
    discount5 = models.FloatField(default=0, help_text='Discount for 5 students')
    familyFee = models.FloatField(default=0, help_text='Registration Fee')
    lateFee = models.FloatField(default=0, help_text='Late Fee')
    lateDate = models.DateField(null=True, verbose_name='Late registration start date', help_text='Format: YYYY-MM-DD')
    
    def get_discount(self, nStudent):
        if nStudent == 1:
            return self.discount1
        elif nStudent == 2:
            return self.discount2
        elif nStudent == 3:
            return self.discount3
        elif nStudent == 4:
            return self.discount4
        elif nStudent == 5:
            return self.discount5
    def eid(self):
        return id_encode(self.id)

class Tuition(models.Model):
    family = models.ForeignKey(Family)
    semester = models.ForeignKey(Semester)
    due = models.FloatField(null=True)
    latest_due_calculation = models.DateField(null=True, verbose_name='Latest due calculation ',
        help_text='Format: YYYY-MM-DD')
    paid = models.FloatField(default=0.0)
    checkno = models.CharField(max_length=40, null=True, verbose_name='PayPal/check number')
    pay_date = models.DateField(null=True, verbose_name='Payment confirmed date', help_text='Format: YYYY-MM-DD')
    pay_credit = models.BooleanField(help_text="Pay by Credit Card")
    def eid(self):
        return id_encode(self.id)

    def fully_paid(self):
        return self.paid == self.due
    class Meta:
        unique_together = (('family', 'semester'))

def current_reg_semester(request):
    today = datetime.datetime.today()
    sems = Semester.objects.filter(school=request.school, regStart__lte=today, regEnd__gte=today)
    if sems:  # find the one ended last
        return reduce((lambda x, y:x if x.regEnd > y.regEnd else y), sems)
    return None
def current_record_semester(request):
    today = datetime.datetime.today()
    sems = Semester.objects.filter(school=request.school, recordStart__lte=today, recordEnd__gte=today)
    if sems:  # find the one ended last
        return reduce((lambda x, y:x if x.recordEnd > y.recordEnd else y), sems)
    return None


types= ['string','float','int','dollar','text','boolean','date','url','email','time']

TYPE_CHOICES = tuple(zip(types,types) )

class Config(models.Model):
    school = models.ForeignKey(School)    
    name = models.CharField(max_length=100)
    verbose_name = models.CharField(max_length=100)
    
    valueType = models.CharField(max_length=10)
    
    stringValue = models.CharField(max_length=400, default='')
    floatValue = models.FloatField(null=True, default=0)
    intValue = models.IntegerField(null=True, default=0)
    dollarValue = models.IntegerField(null=True, default=0)
    textValue = models.TextField(null=True, default='')
    booleanValue= models.BooleanField(default=False)
    dateValue= models.DateField(null=True)
    emailValue=models.EmailField(null=True, default='')
    urlValue=models.URLField(null=True, default='')
    timeValue=models.TimeField(null=True)

    description = models.CharField(max_length=400, null=True)
    def eid(self):
        return id_encode(self.id)

    def is_text(self):
        return self.valueType == 'text'

    def value(self):
        t=self.valueType
        if t == 'string':
            return self.stringValue
        elif t == 'int':
            return self.intValue
        elif t == 'float':
            return self.floatValue
        elif t == 'text':
            return self.textValue
        elif t == 'email':
            return self.emailValue

    def set_value(self, value ):
        t=self.valueType
        if t == 'string':
            self.stringValue= value
        elif t == 'int':
            self.intValue = int(value)
        elif t == 'float':
            self.floatValue = float(value)
        elif t == 'text':
            self.textValue = str(value)
        elif t == 'email':
            self.emailValue = str(value)
        

