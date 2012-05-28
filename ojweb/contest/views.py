from django.shortcuts import render_to_response as render, redirect, RequestContext
from ojweb.contest.models import *
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django import forms
from ojweb.web.models import *
from django.views.decorators.csrf import csrf_exempt    #disable the csrf
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

# Create your views here.
def contest_list(request):
    cts = Contest.objects.filter(status='1').order_by('begintime')
    for c in cts:
        if request.user.is_authenticated() and Contestant.objects.filter(contest=c).filter(user=request.user).exists():
            c.join = True
        else:
            c.join = False
    return render('web/contests.html', {'contests' : cts}, context_instance=RequestContext(request))

@login_required
def contest_detail(request, contest_id):
    try:
        c = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        raise Http404
    cus = Contestant.objects.filter(contest=c).filter(user=request.user)
    if len(cus) != 1:
        return redirect('/contests')
    cps = ContestProblem.objects.filter(contest=c).order_by('sequencechar')
    for cp in cps:
        if Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(user=request.user).filter(resultcode=1).exists():
            cp.trystatus = 1
        elif Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(user=request.user).exists():
            cp.trystatus = -1
        else:
            cp.trystatus = 0
    return render('contest/contest.html', {'contest' : c, 'contestproblem_list' : cps}, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def contest_register(request, contest_id):
    try:
        c = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        raise Http404
    if request.method == 'GET':
        return render('web/contest_entry.html', {'contest' : c}, context_instance=RequestContext(request))
    else:
        agree = request.POST.get('cbxAgree')
        print agree
        if agree:
            cus = Contestant.objects.filter(contest=c).filter(user=request.user)
            if len(cus) == 0:                    
                cu = Contestant()
                cu.contest = c
                cu.user = request.user
                cu.status = True
                cu.save()
            return redirect('/contest/%d' % int(contest_id))
        return redirect('/contests')

def _get_contest_problem(c, seq):
    cps = ContestProblem.objects.filter(contest=c).filter(sequencechar=seq)
    if len(cps) == 1:
        return cps[0].problem
    else:
        return None
@login_required
def contest_problem_detail(request, contest_id, sequence):
    try:
        c = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        raise Http404
    p = _get_contest_problem(c, sequence)
    if not p:
        raise Http404
    return render('contest/problem.html', {'problem' : p, 'contest' : c, 'sequence' : sequence}, context_instance=RequestContext(request))

class ContestSubmitForm(forms.Form):
    contest_id = forms.IntegerField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    problem_no = forms.IntegerField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    sequence = forms.CharField(max_length=1, widget=forms.TextInput(attrs={'readonly':'readonly'}))
    compiler = forms.ModelChoiceField(queryset=Compiler.objects.all().order_by(('sequence')))
    code = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':20, 'cols':80}))

def _check_submit_time(c):
    now = datetime.now()
    return (now > c.begintime and now < c.endtime)

@csrf_exempt
@login_required
def contest_submit(request, contest_id, sequence):
    try:
        c = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        raise Http404
    if not _check_submit_time(c):
        return redirect('/contest/%d' % int(contest_id))
    if(request.method == 'POST'):
        form = ContestSubmitForm(request.POST)
        if form.is_valid():
            pno = form.cleaned_data['problem_no']
            try:
                p = Problem.objects.get(no=pno)
            except Problem.DoesNotExist:
                return render('contest/submit.html', {'form' : form, 'contest' : c}, context_instance=RequestContext(request))
            compiler = form.cleaned_data['compiler']
            code = form.cleaned_data['code']
            s = Submit()
            s.problem = p
            s.contest = c     # if not in contest, c is None
            s.user = request.user
            s.compiler = compiler
            s.code = code
            s.codelen = len(code)
            s.resultcode = 0
            s.resultstring = 'Pending'
            s.runtime = -1
            s.runmem = -1
            s.save()
            return redirect('/contest/%d/status' % int(contest_id))
    else:
        p = _get_contest_problem(c, sequence)
        if not p:
            raise Http404
        form = ContestSubmitForm(initial={'contest_id' : contest_id, 'problem_no' : p.no, 'sequence' : sequence})
        return render('contest/submit.html', {'form' : form, 'contest' : c}, context_instance=RequestContext(request))

def contest_status(request, contest_id, page_idx):
    num_per_page = 50
    try:
        c = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        raise Http404
    pages = Paginator(Submit.objects.filter(contest=c).order_by('-id'), num_per_page)
    try:
        page = pages.page(page_idx)
    except (EmptyPage, InvalidPage):
        page = pages.page(1)
    for s in page.object_list:
        s.sequence = ContestProblem.objects.filter(contest=c).get(problem=s.problem).sequencechar
    return render('contest/status.html', {'pages' : pages, 'page' : page, 'contest' : c}, context_instance=RequestContext(request))

def _cmp(u1, u2):
    if u1.solved < u2.solved:
        return 1
    elif u1.solved == u2.solved:
        if u1.penalty > u2.penalty:
            return 1
        else:
            return -1
    else:
        return -1

def contest_standing(request, contest_id):
    try:
        c = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        raise Http404
    contest_problem_list = ContestProblem.objects.filter(contest=c).order_by('sequencechar')
    problem_sequence_list = [cp.sequencechar for cp in contest_problem_list]
    problem_list = [cp.problem for cp in contest_problem_list]
    map_seq_problem = dict(zip(problem_sequence_list, problem_list))
    cts = Contestant.objects.filter(contest=c)
    users = [ct.user for ct in cts]
    for u in users:
        u.solved = 0
        u.penalty = datetime.now() - datetime.now()
        submit = []
        for seq in problem_sequence_list:
            if Submit.objects.filter(contest=c).filter(user=u).filter(problem=map_seq_problem[seq]).filter(resultcode=1).exists():
                actime = Submit.objects.filter(contest=c).filter(user=u).filter(problem=map_seq_problem[seq]).filter(resultcode=1).order_by('-id')[0].jointime
                actime = actime - c.begintime
                u.solved = u.solved + 1
                u.penalty = u.penalty + actime
            else:
                actime = None
            trytime = Submit.objects.filter(contest=c).filter(user=u).filter(problem=map_seq_problem[seq]).exclude(resultcode=1).count()
            u.penalty = u.penalty + timedelta(minutes = trytime * 20)
            submit.append((actime, trytime))
        u.submit = submit
    users.sort(cmp=_cmp)
    return render('contest/standing.html', {'problem_sequence_list' : problem_sequence_list, 'contestants' : users, 'contest' : c}, context_instance=RequestContext(request))

@login_required
def contest_stat(request, contest_id):
    try:
        c = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        raise Http404
    contest_problem_list = ContestProblem.objects.filter(contest=c).order_by('sequencechar')
    problem_sequence_list = [cp.sequencechar for cp in contest_problem_list]
    problem_list = [cp.problem for cp in contest_problem_list]
    map_seq_problem = dict(zip(problem_sequence_list, problem_list))
    for cp in contest_problem_list:
        cp.submitnum = Submit.objects.filter(contest=c).filter(problem=cp.problem).count()
        cp.acnum = Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(resultcode=1).count()
        cp.penum = Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(resultcode=2).count()
        cp.cenum = Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(resultcode=3).count()
        cp.wanum = Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(resultcode=4).count()
        cp.mlenum = Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(resultcode=5).count()
        cp.tlenum = Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(resultcode=6).count()
        cp.olenum = Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(resultcode=7).count()
        cp.renum = Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(resultcode=8).count()
        cp.rfnum = Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(resultcode=9).count()
        cp.atnum = Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(resultcode=10).count()
        cp.ienum = Submit.objects.filter(contest=c).filter(problem=cp.problem).filter(resultcode=11).count()
    return render('contest/stat.html', {'contest_problem_list' : contest_problem_list, 'contest' : c}, context_instance=RequestContext(request))    

class BoardNewPostForm(forms.Form):
    contest_id = forms.IntegerField()
    title = forms.CharField(max_length=256)
    content = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':80}))

@csrf_exempt
@login_required
def contest_web_board(request, contest_id):
    try:
        c = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        raise Http404
    if request.method == 'GET':
        ds = Discussion.objects.filter(contest=c).filter(problem=None).filter(src=None).order_by('-id')
        f = BoardNewPostForm(initial={'contest_id' : contest_id})
        return render('contest/web_board.html', {'contest' : c, 'discuss' : ds, 'form' : f}, context_instance=RequestContext(request))
    else:
        f = BoardNewPostForm(request.POST)
        if not f.is_valid():
            return render('contest/web_board.html', {'contest' : c, 'form' : f}, context_instance=RequestContext(request))
        if contest_id != 0:
            c = Contest.objects.get(pk=contest_id)
        else:
            c = None
        d = Discussion()
        d.contest = c
        d.problem = None
        d.title = f.cleaned_data['title']
        d.content = f.cleaned_data['content']
        d.src = None
        d.user = request.user
        d.save()
        return redirect(request.path)    

@csrf_exempt
@login_required
def contest_web_board_detail(request, contest_id, discussion_id):
    try:
        s = Discussion.objects.get(pk=discussion_id)
    except Discussion.DoesNotExist:
        raise Http404
    if request.method == 'GET':
        ds = Discussion.objects.filter(src=s).order_by('id')
        f = BoardNewPostForm(initial={'contest_id':contest_id})
        return render('contest/web_board_detail.html', {'contest' : s.contest, 'src' : s, 'discuss' : ds, 'form' : f}, context_instance=RequestContext(request))
    else:
        f = BoardNewPostForm(request.POST)
        if not f.is_valid():
            return render('web/web_board_detail.html', {'contest' : s.contest, 'src' : s, 'discuss' : ds, 'form' : f}, context_instance=RequestContext(request))
        d = Discussion()
        d.contest = s.contest
        d.problem = None
        d.title = f.cleaned_data['title']
        d.content = f.cleaned_data['content']
        d.src = s
        d.user = request.user
        d.save()
        return redirect(request.path)
