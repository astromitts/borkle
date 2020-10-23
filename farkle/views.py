from django.template import loader
from django.views import View
from django.http import HttpResponse
from django.shortcuts import redirect

from farkle.forms import FormHowManyPlayers, FormPlayerName
from farkle.models import Player


class Start(View):
    def get(self, request, *args, **kwargs):
        request.session.set_expiry(0)  # sets session to terminate on browser close
        template = loader.get_template('farkle/forms/form.html')
        form = FormHowManyPlayers()
        context = {
            'form': form
        }
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        if request.POST.get('how_many_players'):
            request.session['num_players'] = int(request.POST['how_many_players'])
            template = loader.get_template('farkle/forms/player_names.html')
            form = FormPlayerName()
            context = {
                'form': form,
                'num_players': range(request.session['num_players'])
            }
            return HttpResponse(template.render(context, request))
        else:
            request.session['players'] = []
            for i in range(request.session['num_players']):
                player_index = i + 1
                player_name = request.POST['player_name_{}'.format(player_index)]
                request.session['player_{}'.format(player_index)] = Player(player_name)
                request.session['players'].append(request.session['player_{}'.format(player_index)])
            return redirect('play_game')


class Game(View):
    def get(self, request, *args, **kwargs):
        import pdb
        pdb.set_trace()
