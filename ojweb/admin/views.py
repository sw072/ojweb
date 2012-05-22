from django.shortcuts import render_to_response as render, redirect
from django import forms
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404
from django.template import RequestContext
from ojweb.web.models import *
import time
from django.views.decorators.csrf import csrf_exempt    #disable the csrf
# Create your views here.
def admin_index(request):
    return render('admin/index.html', context_instance=RequestContext(request))
    
def admin_problem_list(request, page_idx):
    num_per_page = 50
    pages = Paginator(Problem.objects.all().order_by('no'), num_per_page)
    try:
        page = pages.page(page_idx)
    except (EmptyPage, InvalidPage):
        page = pages.page(1)
    return render('admin/problem_list.html', {'pages' : pages, 'page' : page}, context_instance=RequestContext(request))


class AdminProblemForm(forms.Form):
    problem_no = forms.CharField()
    title = forms.CharField(max_length=256)
    timelmt = forms.IntegerField()
    memlmt = forms.IntegerField()
    desc = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':15,'cols':120}))
    inputdesc = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':15,'cols':120}))
    outputdesc = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':15,'cols':120}))
    sampleinput = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':15,'cols':120}))
    sampleoutput = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':15,'cols':120}))
    hint = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':15,'cols':120}))
    source = forms.CharField(max_length=256)
    status = forms.ChoiceField(choices=PROBLEM_STATUS_CHOICES)

@csrf_exempt
def admin_problem(request, action, problem_id):
    if request.method == 'GET':
        if action == 'new':
            f = AdminProblemForm()
            return render('admin/problem.html', {'form' : f}, context_instance=RequestContext(request))
        elif action == 'edit':
            try:
                p = Problem.objects.get(pk=problem_id)
            except Problem.DoesNotExist:
                raise Http404
            f = AdminProblemForm({'problem_no':p.no, 'title':p.title, 
                                  'timelmt':p.timelmt,'memlmt':p.memlmt, 
                                  'desc':p.desc, 'inputdesc':p.inputdesc,
                                  'inputdesc':p.inputdesc, 'outputdesc':p.outputdesc,
                                  'sampleinput':p.sampleinput, 'sampleoutput':p.sampleoutput,
                                  'hint':p.hint, 'source':p.source, 'status':p.status})
            return render('admin/problem.html', {'form' : f}, context_instance=RequestContext(request))
        elif action == 'disable':
            try:
                p = Problem.objects.get(pk=problem_id)
            except Problem.DoesNotExist:
                raise Http404
            p.status = 'N'
            p.save()
            return redirect('/admin/problems')
        elif action == 'enable':
            try:
                p = Problem.objects.get(pk=problem_id)
            except Problem.DoesNotExist:
                raise Http404
            p.status = 'A'
            p.save()            
            return redirect('/admin/problems')
        else:
            raise Http404
    else:
        f = AdminProblemForm(request.POST)
        if not f.is_valid():
            return render('admin/problem.html', {'form' : f}, context_instance=RequestContext(request))
        p = Problem()
        if problem_id == 0: 
            p.id = None
            if Problem.objects.filter(no=f.cleaned_data['problem_no']).count() > 0:
                return render('admin/problem.html', {'form' : f}, context_instance=RequestContext(request))
        else: 
            p.id = problem_id
            try:
                p = Problem.objects.get(pk=problem_id)
            except Problem.DoesNotExist:
                raise Http404
        p.no = f.cleaned_data['problem_no']
        p.title = f.cleaned_data['title']
        p.timelmt = f.cleaned_data['timelmt']
        p.memlmt = f.cleaned_data['memlmt']
        p.desc = f.cleaned_data['desc']
        p.inputdesc = f.cleaned_data['inputdesc']
        p.outputdesc = f.cleaned_data['outputdesc']
        p.sampleinput = f.cleaned_data['sampleinput']
        p.sampleoutput = f.cleaned_data['sampleoutput']
        p.hint = f.cleaned_data['hint']
        p.source = f.cleaned_data['source']
        p.status = f.cleaned_data['status']
        p.specialjudge = False
        p.contriuser = request.user
        p.save()
        return redirect('/admin/problem/edit/%d' % int(p.id))
        
def admin_contests(request):
    cts = Contest.objects.all().order_by('-id')
    return render('admin/contests.html', {'contests' : cts}, context_instance=RequestContext(request))

class AdminContestForm(forms.Form):
    contestid = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}))
    title = forms.CharField(max_length=256)
    desc = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':80}))
    begintime = forms.DateTimeField()
    endtime = forms.DateTimeField()
    public = forms.BooleanField(required=False)
    status = forms.BooleanField(required=False)
    
@csrf_exempt
def admin_contest(request, action, contest_id):
    if request.method == 'GET':
        if action == 'new':
            f = AdminContestForm(initial={'contestid' : 0})
            return render('admin/contest.html', {'form' : f}, context_instance=RequestContext(request))
        elif action == 'edit':
            try:
                c = Contest.objects.get(pk=contest_id)
            except Contest.DoesNotExist:
                raise Http404
            cps = ContestProblem.objects.filter(contest=c).order_by('sequencechar')
            f = AdminContestForm(initial={'contestid' : c.id, 'title' : c.title, 'desc' : c.desc, 'begintime' : c.begintime, 'endtime' : c.endtime, 'public' : c.public, 'status' : c.status})
            return render('admin/contest.html', {'form' : f, 'contestproblem_list' : cps}, context_instance=RequestContext(request))
    else:
        f = AdminContestForm(request.POST)
        if not f.is_valid():
            return render('admin/contest.html', {'form' : f}, context_instance=RequestContext(request))
        if contest_id == 0:
            c = Contest()
            c.id = None
        else:
            try:
                c = Contest.objects.get(pk=contest_id)
            except Contest.DoesNotExist:
                raise Http404
        c.title = f.cleaned_data['title']
        c.desc = f.cleaned_data['desc']
        c.begintime = f.cleaned_data['begintime']
        c.endtime = f.cleaned_data['endtime']
        c.public = f.cleaned_data['public']
        c.status = f.cleaned_data['status']
        c.save()
        return redirect('/admin/contest/%d/action/edit' % c.id)
        
def _get_contestproblem(c, seq):
    cps = ContestProblem.objects.filter(contest=c).filter(sequencechar=seq)
    if len(cps) == 1:
        return cps[0]
    else:
        return None

class AdminContestProblem(forms.Form):
    contest_id = forms.IntegerField()
    sequencechar = forms.ChoiceField(choices=SEQUENCE_CHARSET)
    problem_no = forms.IntegerField()

@csrf_exempt
def admin_contestproblem(request, action, contest_id, sequence):
    try:
        c = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        raise Http404
    cps = ContestProblem.objects.filter(contest=c).order_by('sequencechar')
    if request.method == 'GET':
        if action=='null':
            f = AdminContestProblem(initial={'contest_id' : contest_id})
            return render('admin/contestproblems.html', {'form' : f, 'contestproblem_list' : cps}, context_instance=RequestContext(request))
        elif action == 'delete':
            print c.title, sequence
            cp = _get_contestproblem(c, sequence)
            cp.delete()
            return redirect('/admin/contest/%d/contestproblems' % int(contest_id))
        else:
            raise Http404
    else:
        f = AdminContestProblem(request.POST)
        if action == 'new':
            if not f.is_valid():
                return render('admin/contestproblems.html', {'form' : f, 'contestproblem_list' : cps}, context_instance=RequestContext(request))
            try:
                p = Problem.objects.get(no=f.cleaned_data['problem_no'])
            except Problem.DoesNotExist:
                return render('admin/contestproblems.html', {'form' : f, 'contestproblem_list' : cps}, context_instance=RequestContext(request))
            cp = ContestProblem()
            cp.id = None
            cp.contest = c
            cp.problem = p
            cp.sequencechar = f.cleaned_data['sequencechar']
            cp.save()
        else:
            raise Http404
        return redirect('/admin/contest/%d/contestproblems' % int(contest_id))
            
    
    
    
        