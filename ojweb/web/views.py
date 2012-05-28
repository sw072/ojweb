from django.shortcuts import render_to_response as render, redirect, RequestContext
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django import forms
from ojweb.web.models import *
from django.views.decorators.csrf import csrf_exempt    #disable the csrf
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext, ugettext_lazy as _

# Create your views here.
def index(request):
    num_show = 3
    news_list = News.objects.filter(status=True).order_by('-id')[:3]
    return render('web/index.html', {'news_list' : news_list}, context_instance=RequestContext(request))

def news(request, news_id):
    try:
        news = News.objects.get(pk=news_id)
    except News.DoesNotExist:
        raise Http404
    return render('web/news.html', {'news' : news}, context_instance=RequestContext(request))

def problem_list(request, page_idx):
    num_per_page = 50
    pages = Paginator(Problem.objects.filter(status='A').all().order_by('no'), num_per_page)
    try:
        page = pages.page(page_idx)
    except (EmptyPage, InvalidPage):
        page = pages.page(1)
    if request.user.is_authenticated():
        for p in page.object_list:
            if Submit.objects.filter(problem=p).filter(user=request.user).filter(resultcode=1).exists():
                p.trystatus = 1
            elif Submit.objects.filter(problem=p).filter(user=request.user).exists():
                p.trystatus = -1
            else:
                p.trystatus = 0
    return render('web/problem_list.html', {'pages' : pages, 'page' : page}, context_instance=RequestContext(request))

def problem_detail(request, problem_no):
    try:
        p = Problem.objects.get(no=int(problem_no))
    except Problem.DoesNotExist:
        raise Http404
    if not p.is_available:
        raise Http404
    return render('web/problem.html', {'problem' : p}, context_instance=RequestContext(request))

def problem_stat(request, problem_no, page_idx):
    try:
        p = Problem.objects.get(no=problem_no)
    except Problem.DoesNotExist:
        raise Http404
    p.acnum = Submit.objects.filter(problem=p).filter(resultcode=1).count()
    p.submitnum = Submit.objects.filter(problem=p).count()
    p.penum = Submit.objects.filter(problem=p).filter(resultcode=2).count()
    p.cenum = Submit.objects.filter(problem=p).filter(resultcode=3).count()
    p.wanum = Submit.objects.filter(problem=p).filter(resultcode=4).count()
    p.mlenum = Submit.objects.filter(problem=p).filter(resultcode=5).count()
    p.tlenum = Submit.objects.filter(problem=p).filter(resultcode=6).count()
    p.olenum = Submit.objects.filter(problem=p).filter(resultcode=7).count()
    p.renum = Submit.objects.filter(problem=p).filter(resultcode=8).count()
    p.rfnum = Submit.objects.filter(problem=p).filter(resultcode=9).count()
    p.atnum = Submit.objects.filter(problem=p).filter(resultcode=10).count()
    p.ienum = Submit.objects.filter(problem=p).filter(resultcode=11).count()
    num_per_page = 10
    pages = Paginator(Submit.objects.filter(problem=p).all().order_by('-id'), num_per_page)
    try:
        page = pages.page(page_idx)
    except (EmptyPage, InvalidPage):
        page = pages.page(1)
    return render('web/problem_stat.html', {'problem' : p, 'pages' : pages, 'page' : page}, context_instance=RequestContext(request))

class NewPostForm(forms.Form):
    problem_no = forms.IntegerField()
    title = forms.CharField(max_length=256)
    content = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':80}))

@csrf_exempt
@login_required
def problem_discuss_list(request, problem_no, contest_id, sequence):
    if contest_id != 0:
        c = Contest.objects.get(pk=contest_id)
        cp = ContestProblem.objects.filter(contest=c).filter(sequencechar=sequence)[0]
        problem_no = cp.problem.no
    else:
        c = None
    try:
        p = Problem.objects.get(no=problem_no)
        if c:
            p.sequence = sequence
            p.contest = c
    except Problem.DoesNotExist:
        raise Http404
    if request.method == 'GET':
        if contest_id != 0:
            ds = Discussion.objects.filter(problem=p).filter(src=None).filter(contest__id=contest_id).order_by('-id')
        else:
            ds = Discussion.objects.filter(problem=p).filter(src=None).order_by('-id')
        f = NewPostForm(initial={'problem_no' : p.no})
        return render('web/problem_discuss_list.html', {'problem' : p, 'discuss' : ds, 'form' : f}, context_instance=RequestContext(request))
    else:
        f = NewPostForm(request.POST)
        if not f.is_valid():
            return render('web/problem_discuss_list.html', {'problem' : p, 'form' : f}, context_instance=RequestContext(request))
        if contest_id != 0:
            c = Contest.objects.get(pk=contest_id)
        else:
            c = None
        d = Discussion()
        d.contest = c
        d.problem = p
        d.title = f.cleaned_data['title']
        d.content = f.cleaned_data['content']
        d.src = None
        d.user = request.user
        d.save()
        print p.no, d.id
        return redirect(request.path)
    
@csrf_exempt
@login_required
def problem_discuss_detail(request, problem_no, discussion_id):
    try:
        s = Discussion.objects.get(pk=discussion_id)
    except Discussion.DoesNotExist:
        raise Http404
    p = s.problem
    if not problem_no:
        if s.contest:
            cp = ContestProblem.objects.filter(contest=s.contest).filter(problem=p)[0]
            p.sequence = cp.sequencechar
            p.contest = s.contest
    if request.method == 'GET':
        ds = Discussion.objects.filter(src=s).order_by('id')
        f = NewPostForm(initial={'problem_no':p.no})
        return render('web/problem_discuss_detail.html', {'problem' : p, 'src' : s, 'discuss' : ds, 'form' : f}, context_instance=RequestContext(request))
    else:
        f = NewPostForm(request.POST)
        if not f.is_valid():
            return render('web/problem_discuss_detail.html', {'problem' : p, 'src' : s, 'discuss' : ds, 'form' : f}, context_instance=RequestContext(request))
        d = Discussion()
        d.contest = s.contest
        d.problem = p
        d.title = f.cleaned_data['title']
        d.content = f.cleaned_data['content']
        d.src = s
        d.user = request.user
        d.save()
        return redirect(request.path)
        
class SubmitForm(forms.Form):
    problem_no = forms.IntegerField()
    compiler = forms.ModelChoiceField(queryset=Compiler.objects.all().order_by(('sequence')))
    code = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':20, 'cols':80}))

@csrf_exempt
@login_required
def submit(request, problem_no):
    if(request.method == 'POST'):
        form = SubmitForm(request.POST)
        if form.is_valid():
            pno = form.cleaned_data['problem_no']
            try:
                p = Problem.objects.get(no=pno)
            except Problem.DoesNotExist:
                return render('web/submit.html', {'form' : form}, context_instance=RequestContext(request))
            compiler = form.cleaned_data['compiler']
            code = form.cleaned_data['code']
            s = Submit()
            s.problem = p
            s.contest = None     # if not in contest, c is None
            s.user = request.user
            s.compiler = compiler
            s.code = code
            s.codelen = len(code)
            s.resultcode = 0
            s.resultstring = 'Pending'
            s.runtime = -1
            s.runmem = -1
            s.save()
            return redirect('/status')
            # return render('web/submit.html', {'form' : form}, context_instance=RequestContext(request))    
    else:
        try:
            p = Problem.objects.get(no=problem_no)
        except Problem.DoesNotExist:
            p = Problem.objects.get(no=1000)
        form = SubmitForm(initial={'problem_no' : p.no})
        return render('web/submit.html', {'form' : form}, context_instance=RequestContext(request))

JUDGE_RESULT_CHOICES = ((-1, '--'), (1, 'Accepted'), (3, 'Compile Error'), (2, 'Presentation Error'), (4,'Wrong Answer'), (5,'Memory Limit Exceeded'), (6,'Time Limit Exceeded'), (7,'Output Limit Exceeded'), (8,'Runtime Error'), (9,'Restricted Function'), (10,'Abnormal Termination'), (11,'Internal Error'))
LANG_CHOICES = (('A', '--'), ('C', 'C'), ('C++', 'C++'), ('Java', 'Java'))
class StatusQueryForm(forms.Form):
    problem_no = forms.IntegerField(required=False)
    user_name = forms.CharField(max_length=32, required=False)
    lang = forms.ChoiceField(choices=LANG_CHOICES, required=False)
    result = forms.ChoiceField(choices=JUDGE_RESULT_CHOICES, required=False)
    
@csrf_exempt
def status(request, page_idx):
    if request.method == 'POST':
        f = StatusQueryForm(request.POST)
        if not f.is_valid():
            pass
        pno = f.cleaned_data['problem_no']
        uname = f.cleaned_data['user_name']
        lang = f.cleaned_data['lang']
        result = f.cleaned_data['result']
        print pno, result
    else:
        f = StatusQueryForm()
        pno = None
        uname = None
        lang = 'A'
        result = -1
    s = Submit.objects
    if pno:
        s = s.filter(problem__no=pno)
    if uname:
        s = s.filter(user__username=uname)
    if lang != 'A':
        s = s.filter(compiler__lang=lang)
    if result != -1:
        s = s.filter(resultcode=result)
    num_per_page = 15
    pages = Paginator(s.order_by('-id'), num_per_page)
    try:
        page = pages.page(page_idx)
    except (EmptyPage, InvalidPage):
        page = pages.page(1)
    return render('web/status.html', {'pages' : pages, 'page' : page, 'form' : f}, context_instance=RequestContext(request))

@login_required
def code(request, run_id):
    try:
        s = Submit.objects.get(pk=run_id)
    except Submit.DoesNotExist:
        raise Http404
    if s.user.id == request.user.id:
        return render('web/code.html', {'submit' : s}, context_instance=RequestContext(request))

def userrank(request, page_idx):
    num_per_page = 50
    pages = Paginator(UserProfile.objects.all().order_by('-solvednum', 'submitnum'), num_per_page)
    try:
        page = pages.page(page_idx)
    except (EmptyPage, InvalidPage):
        page = pages.page(1)
    return render('web/userrank.html', {'pages' : pages, 'page' : page}, context_instance=RequestContext(request))

def userdetail(request, user_name):
    try:
        u = User.objects.get(username=user_name)
    except User.DoesNotExist:
        raise Http404
    # ugly... Need modify
    solved_id_list = Submit.objects.filter(user=u).filter(resultcode=1).values('problem').distinct().all()
    solved_no_list = [Problem.objects.get(pk=problem_id['problem']).no for problem_id in solved_id_list]
    solved_no_list.sort()
    # There are some error when using object.raw, maybe the version of the mysqldb is not correct
    #qs = UserProfile.objects.raw('select count(*) as rank from web_userprofile where solvednum>%d or (solvednum=%d and submitnum<%d)', (u.get_profile().solvednum, u.get_profile().solvednum, u.get_profile().submitnum))
    return render('web/userdetail.html', {'user' : u, 'solved_list' : solved_no_list}, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def usermessage(request, user_name):
    try:
        u = User.objects.get(username=user_name)
    except User.DoesNotExist:
        raise Http404
    if u.id != request.user.id:
        raise Http404
    if request.method == 'GET':
        return redirect('/')
    else:
        return redirect('/')

def faq(request):
    return render('web/faq.html', context_instance=RequestContext(request))

class RegistForm(forms.Form):
    username = forms.CharField(max_length=32)
    password = forms.CharField(max_length=32, widget=forms.widgets.PasswordInput)
    password2 = forms.CharField(max_length=32, widget=forms.widgets.PasswordInput)
    email = forms.EmailField()
    school = forms.CharField(max_length=128)
    homepage = forms.URLField()
    motto = forms.CharField(max_length=256, widget=forms.widgets.Textarea)
    
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    
    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])
           
    def clean_password2(self):
        password1 = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'])
        return password2

@csrf_exempt
def register(request):
    if request.method == 'GET':
        g = RegistForm()
        return render('web/register.html', {'form' : g}, context_instance=RequestContext(request))
    else:
        g = RegistForm(request.POST)
        if not g.is_valid():
            return render('web/register.html', {'form' : g}, context_instance=RequestContext(request))
        u = User()
        u.username = g.cleaned_data['username']
        upwd = g.cleaned_data['password']
        u.set_password(upwd)
        u.email = g.cleaned_data['email']
        u.save()
        uinfo = UserProfile()
        uinfo.user = u
        uinfo.school = g.cleaned_data['school']
        uinfo.homepage = g.cleaned_data['homepage']
        uinfo.motto = g.cleaned_data['motto']
        uinfo.school = g.cleaned_data['school']
        uinfo.role = 'C'  # ordinary user
        uinfo.save()
        u = authenticate(username=u.username, password=upwd)
        login(request, u)
        return redirect('/')

class SigninForm(forms.Form):
    username = forms.CharField(max_length=32)
    password = forms.CharField(max_length=32, widget=forms.widgets.PasswordInput)
    next_url = forms.CharField(widget=forms.widgets.HiddenInput)

@csrf_exempt
def signin(request):
    if request.method == 'GET':
        sign = SigninForm(initial={'next_url':request.GET.get('next', '/')})
        return render('web/signin.html', {'form' : sign}, context_instance=RequestContext(request))
    else:
        sign = SigninForm(request.POST)
        if not sign.is_valid():
            return render('web/signin.html', {'form' : sign}, context_instance=RequestContext(request))
        uname = sign.cleaned_data['username']
        upassword = sign.cleaned_data['password']
        user = authenticate(username=uname, password=upassword)
        if user: 
            if user.is_active:
                login(request, user)
                return redirect(request.POST['next_url'])   # redirect to the former page
            else:
                return redirect('/error')
        else:
            return redirect('/error')

@login_required
def signout(request):
    logout(request)
    return redirect('/')
    
    
