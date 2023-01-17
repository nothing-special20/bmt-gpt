from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.teams.decorators import login_and_team_required


def main(request, team_slug):
    if request.user.is_authenticated:
        return render(request, 'web/demo/demo.html')
        # return reverse('web:demo/demo')
        # return render(request, 'account/profile.html', {
    #     return render(request, 'web/demo/demo.html', {
    #         # 'form': form,
    #         'active_tab': 'demo',
    #         'page_title': _('Demo'),
    #         # 'social_accounts': SocialAccount.objects.filter(user=request.user),
    #         # 'user_has_valid_totp_device': user_has_valid_totp_device(request.user),
    # })
    else:
        return render(request, 'web/landing_page.html')


# @login_and_team_required
