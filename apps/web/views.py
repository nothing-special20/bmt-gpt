from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.teams.decorators import login_and_team_required
from django.views.decorators.clickjacking import xframe_options_exempt

from django.conf import settings

def home(request):
    if request.user.is_authenticated:
        team = request.team
        if team:
            return HttpResponseRedirect(reverse('web_team:home', args=[team.slug]))
        else:
            messages.info(request, _(
                'Teams are enabled but you have no teams. '
                'Create a team below to access the rest of the dashboard.'
            ))
            return HttpResponseRedirect(reverse('teams:manage_teams'))
    else:
        return render(request, 'web/demo-saas.html')


@login_and_team_required
@xframe_options_exempt
def team_home(request, team_slug):
    assert request.team.slug == team_slug
    return render(request, 'web/app_home.html', context={
        'team': request.team,
        'active_tab': 'dashboard',
        'page_title': _('{team} Dashboard').format(team=request.team),
        'loom_demo_url': settings.PROJECT_METADATA['LOOM_DEMO_URL']
    })


def simulate_error(request):
    raise Exception('This is a simulated error.')

def privacy_policy(request):
    return render(request, 'web/privacy_policy.html')