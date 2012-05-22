from django.conf.urls import patterns, include, url
from ojweb.web.views import *
from ojweb.admin.views import *
from ojweb.contest.views import *
import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', index),
    (r'^register/$', register),
    (r'^signin/$', signin),
    (r'^signout/$', signout),
    (r'^problems/$', problem_list, {'page_idx' : 1}),
    (r'^problems/(?P<page_idx>\d+)$', problem_list),
    (r'^problem/(?P<problem_no>\w+)$', problem_detail),
    (r'^problem/(?P<problem_no>\w+)/stat$', problem_stat, {'page_idx' : 1}),
    (r'^problem/(?P<problem_no>\w+)/stat/(?P<page_idx>\d+)$', problem_stat),
    (r'^problem/(?P<problem_no>\w+)/discuss$', problem_discuss_list, {'contest_id' : 0, 'sequence' : 0}),
    (r'^problem/(?P<problem_no>\w+)/discuss/(?P<discussion_id>\d+)$', problem_discuss_detail),
    (r'^submit/$', submit, {'problem_no' : 1000}),
    (r'^submit/(?P<problem_no>\w+)$', submit),
    (r'^status/$', status, {'page_idx' : 1}),
    (r'^status/(?P<page_idx>\d+)$', status),
    (r'^code/(?P<run_id>\d+)$', code),
    (r'^rank/$', userrank, {'page_idx' : 1}),
    (r'^rank/(?P<page_idx>\d+)$', userrank),
    (r'^user/(?P<user_name>\w+)$', userdetail),
    (r'^user/(?P<user_name>\w+)/message$', usermessage),
    (r'^faq/$', faq),
    # Contest
    (r'^contests$', contest_list),
    (r'^contest/(?P<contest_id>\d+)$', contest_detail),
    (r'^contest/(?P<contest_id>\d+)/reg/$', contest_register),
    (r'^contest/(?P<contest_id>\d+)/problem/(?P<sequence>\w)$', contest_problem_detail),
    (r'^contest/(?P<contest_id>\d+)/submit/(?P<sequence>\w)$', contest_submit),
    (r'^contest/(?P<contest_id>\d+)/problem/(?P<sequence>\w)/discuss/$', problem_discuss_list, {'problem_no' : 0}),
    (r'^contest/\d+/problem/\w/discuss/(?P<discussion_id>\d+)$', problem_discuss_detail, {'problem_no' : 0}),
    (r'^contest/(?P<contest_id>\d+)/status/$', contest_status, {'page_idx' : 1}),
    (r'^contest/(?P<contest_id>\d+)/status/(?P<page_idx>\d+)$', contest_status),
    (r'^contest/(?P<contest_id>\d+)/standing/$', contest_standing),
    (r'^contest/(?P<contest_id>\d+)/stat/$', contest_stat),
    (r'^contest/(?P<contest_id>\d+)/webboard/$', contest_web_board),
    (r'^contest/(?P<contest_id>\d+)/webboard/(?P<discussion_id>\d+)$', contest_web_board_detail),
    # admin
    (r'^admin/$', admin_index),
    (r'^admin/problems/$', admin_problem_list, {'page_idx' : 1}),
    (r'^admin/problems/(?P<page_idx>\d+)$', admin_problem_list),
    (r'^admin/problem/(?P<action>\w+)/$', admin_problem, {'problem_id' : 0}),
    (r'^admin/problem/(?P<action>\w+)/(?P<problem_id>\d+)$', admin_problem),
    (r'^admin/contests$', admin_contests),
    (r'^admin/contest/(?P<action>\w+)$', admin_contest, {'contest_id' : 0}),
    (r'^admin/contest/(?P<contest_id>\d+)/action/(?P<action>\w+)$', admin_contest),
    (r'^admin/contest/(?P<contest_id>\d+)/contestproblems/$', admin_contestproblem, {'action' : 'null', 'sequence' : 'Z'}),
    (r'^admin/contest/(?P<contest_id>\d+)/contestproblems/(?P<action>\w+)$', admin_contestproblem, {'sequence' : 'Z'}),
    (r'^admin/contest/(?P<contest_id>\d+)/contestproblems/(?P<action>\w+)/(?P<sequence>\w)$', admin_contestproblem),
    # tiny_mce
    (r'^media/(?P<path>.*)', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT}),
    # static
    (r'^static/(?P<path>.*)', 'django.views.static.serve', {'document_root' : settings.STATIC_ROOT}),
    # Examples:
    # url(r'^$', 'ojweb.views.home', name='home'),
    # url(r'^ojweb/', include('ojweb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
