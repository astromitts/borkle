from django.template import loader
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect

from farkle.forms import FormGameSetup, FormPlayerName
from farkle.models import Game, Player, DiceSelection
from farkle.utils import Score


class Start(View):
    def get(self, request, *args, **kwargs):
        # clear out old game if it is there
        existing_game = Game.objects.filter(pk=request.session.get('game_id')).exists()
        if existing_game:
            Game.objects.get(pk=request.session['game_id']).delete()
            request.session['state'] = 'setup'
        Game.lazy_cleanup()

        request.session.set_expiry(0)  # sets session to terminate on browser close
        template = loader.get_template('farkle/forms/game_setup.html')
        form = FormGameSetup(initial={'how_many_points_are_you_playing_to': 5000, 'how_many_players': 2})
        context = {
            'form': form
        }
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        if request.POST.get('how_many_players'):
            num_players = int(request.POST['how_many_players'])
            if num_players > 6:
                num_players = 6
            elif num_players < 1:
                num_players = 1
            max_score = int(request.POST['how_many_points_are_you_playing_to'])
            if max_score < 1:
                max_score = 5000
            request.session['num_players'] = num_players
            request.session['max_score'] = max_score
            template = loader.get_template('farkle/forms/player_names.html')
            form = FormPlayerName()
            context = {
                'form': form,
                'num_players': range(request.session['num_players'])
            }
            return HttpResponse(template.render(context, request))
        else:
            new_game = Game(max_score=request.session['max_score'])
            new_game.save()
            request.session['game_id'] = new_game.pk
            request.session['players'] = []
            for i in range(request.session['num_players']):
                player_index = i + 1
                player_name = request.POST['player_name_{}'.format(player_index)]
                new_player = Player(name=player_name, game=new_game, player_order=player_index)
                new_player.save()
            return redirect('play_game')


class PlayGame(View):
    def get(self, request, *args, **kwargs):
        game = Game.objects.get(pk=request.session['game_id'])
        game.check_status()
        if game.status == 'active':
            template = loader.get_template('farkle/gameboard.html')
            game.start_round()
            current_player = game.current_player
            game.current_player.current_turn.roll()
            context = {
                'game': game,
                'current_player': current_player,
                'players': game.player_set.all(),
                'is_last_turn': game.last_turn
            }
        else:
            game.current_player.end_turn()
            template = loader.get_template('farkle/gameover.html')
            winner, is_tie = game.get_winner()
            context = {
                'game': game,
                'players': game.player_set.all(),
                'winner': winner,
                'is_tie': is_tie
            }
        return HttpResponse(template.render(context, request))


class Roll(View):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('farkle/rolleddice.html')
        game = Game.objects.get(pk=request.session['game_id'])
        game.current_player.current_turn.roll()
        test_score = Score([rv['value'] for key, rv in game.current_player.current_turn.rolled_values.items()])
        selections = game.current_player.current_turn.diceselection_set.all()
        scrubbed = not test_score.has_score
        if scrubbed:
            game.current_player.current_turn.scrub()
        context = {
            'dice': game.current_player.current_turn.rolled_values,
            'scrubbed': scrubbed,
            'selections': [selection.scored_values for selection in selections],
            'can_select_more': test_score.has_score > 0,
        }
        return HttpResponse(template.render(context, request))


class CheckSelection(View):
    def get(self, request, *args, **kwargs):
        vals = [int(v) for k,v in request.GET.items()]
        test_score = Score(vals)
        data = {
            'valid_selection': test_score.score > 0,
        }
        return JsonResponse(data)


class MakeSelection(View):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('farkle/rolleddice.html')
        game = Game.objects.get(pk=request.session['game_id'])
        current_player = game.current_player
        current_turn = current_player.current_turn
        new_selection = DiceSelection.create(current_turn, request.GET)
        test_score = Score([rv['value'] for key, rv in game.current_player.current_turn.rolled_values.items()])
        selections = game.current_player.current_turn.diceselection_set.order_by('-pk').all()
        context = {
            'dice': game.current_player.current_turn.rolled_values,
            'can_select_more': test_score.has_score,
            'selections': [selection.scored_values for selection in selections],
            'remaining_count': game.current_player.current_turn.available_dice,
        }
        return HttpResponse(template.render(context, request))


class UndoSelection(View):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('farkle/rolleddice.html')
        game = Game.objects.get(pk=request.session['game_id'])
        current_player = game.current_player
        current_turn = current_player.current_turn
        selection = DiceSelection.objects.get(pk=kwargs['selection_id'])
        if selection.turn == current_turn:
            current_turn.undo_selection(selection=selection)
        test_score = Score([rv['value'] for key, rv in game.current_player.current_turn.rolled_values.items()])
        selections = game.current_player.current_turn.diceselection_set.all()
        context = {
            'dice': game.current_player.current_turn.rolled_values,
            'can_select_more': test_score.has_score,
            'selections': [selection.scored_values for selection in selections],
            'remaining_count': game.current_player.current_turn.available_dice,
        }
        return HttpResponse(template.render(context, request))


class History(View):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('farkle/game_history.html')
        game = Game.objects.get(pk=request.session['game_id'])
        context = {'game': game}
        return HttpResponse(template.render(context, request))



class PreviewWinner(View):
    def get(self, request, *args, **kwargs):
        game = Game.objects.get(pk=request.session['game_id'])
        template = loader.get_template('farkle/gameover.html')
        winner, is_tie = game.get_winner()
        context = {
            'game': game,
            'players': game.player_set.all(),
            'winner': winner,
            'is_tie': is_tie
        }
        return HttpResponse(template.render(context, request))
