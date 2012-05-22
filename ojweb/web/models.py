from django.db import models
from django.contrib.auth.models import User

ROLES_CHOICES = (('A', 'administrator'), ('M', 'manager'), ('C', 'ordinary user'))
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    role = models.CharField(max_length=1, choices=ROLES_CHOICES)
    school = models.CharField(max_length=128)
    motto = models.CharField(max_length=256)
    homepage = models.URLField()
    solvednum = models.IntegerField(default=0)
    submitnum = models.IntegerField(default=0)
    def _is_admin(self):
        return self.role == 'A'
    def _is_manager(self):
        return self.role == 'M'
    def _is_ordinaryuser(self):
        return self.role == 'C'
    is_admin = property(_is_admin)
    is_manager = property(_is_manager)
    is_ordinaryuser = property(_is_ordinaryuser)
    
PROBLEM_STATUS_CHOICES = (('A', 'Available'), ('C', 'In Contest'), ('N', 'Not Available'))
class Problem(models.Model):
    no = models.IntegerField(unique=True)
    title = models.CharField(max_length=256)
    desc = models.TextField()
    inputdesc = models.TextField()
    outputdesc = models.TextField()
    sampleinput = models.TextField()
    sampleoutput = models.TextField()
    hint = models.TextField()
    source = models.CharField(max_length=256)
    timelmt = models.IntegerField()
    memlmt = models.IntegerField()
    acceptednum = models.IntegerField(default=0)
    submitnum =  models.IntegerField(default=0)
    specialjudge = models.BooleanField(default=False)
    contriuser = models.ForeignKey(User)
    jointime = models.DateTimeField(auto_now_add = True)
    status = models.CharField(max_length=1, choices=PROBLEM_STATUS_CHOICES)
    def _is_available(self):
        return self.status == 'A'
    is_available = property(_is_available)
    
COMPILER_CHOICES = (('GCC', 'GCC'), ('G++', 'G++'), ('Java', 'Java'))
LANGUAGE_CHOICES = (('C', 'C'), ('C++', 'C++'), ('Java', 'Java'))
class Compiler(models.Model):
    name = models.CharField(max_length=64, choices=COMPILER_CHOICES)
    lang = models.CharField(max_length=32, choices=LANGUAGE_CHOICES)
    command = models.CharField(max_length=256)
    sequence = models.IntegerField()
    def __unicode__(self):
        return '%s' % self.name

# contest
class Contest(models.Model):
    title = models.CharField(max_length=256)
    desc = models.TextField()
    begintime = models.DateTimeField()
    endtime = models.DateTimeField()
    public = models.BooleanField()
    status = models.BooleanField()
    jointime = models.DateTimeField(auto_now_add=True)

SEQUENCE_CHARSET = (('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G'))
class ContestProblem(models.Model):
    contest = models.ForeignKey(Contest)
    problem = models.ForeignKey(Problem)
    sequencechar = models.CharField(max_length=1, choices=SEQUENCE_CHARSET)

class Contestant(models.Model):
    contest = models.ForeignKey(Contest)
    user = models.ForeignKey(User)
    jointime = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)


class Submit(models.Model):
    problem = models.ForeignKey(Problem)
    contest = models.ForeignKey(Contest, null=True, blank=True)   # Note!!
    user = models.ForeignKey(User)
    compiler = models.ForeignKey(Compiler)
    code = models.CharField(max_length=4096)
    codelen = models.IntegerField()
    resultcode = models.IntegerField()
    resultstring = models.CharField(max_length=128)
    runtime = models.IntegerField(default=-1)
    runmem = models.IntegerField(default=-1)
    jointime = models.DateTimeField(auto_now_add=True)

class CompileError(models.Model):
    submit = models.ForeignKey(Submit)
    info = models.TextField()
    
class Discussion(models.Model):
    src = models.ForeignKey('self', null=True, blank=True)
    contest = models.ForeignKey(Contest, null=True, blank=True)
    problem = models.ForeignKey(Problem, null=True, blank=True)
    user = models.ForeignKey(User)
    title = models.CharField(max_length=256)
    content = models.TextField()
    jointime = models.DateTimeField(auto_now_add=True)

class InternalMail(models.Model):
    userfrom = models.ForeignKey(User, related_name='userform_id')
    userto = models.ForeignKey(User, related_name='userto_id')
    title = models.CharField(max_length=256)
    content = models.TextField()
    jointime = models.DateTimeField(auto_now_add=True)

class News(models.Model):
    title = models.CharField(max_length=256)
    content = models.TextField()
    status = models.BooleanField(default=True)
    jointime = models.DateTimeField(auto_now_add=True)
    


