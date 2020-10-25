from django.db import models
from django.db.models import Max
import random
from datetime import datetime, timedelta
from copy import deepcopy

from farkle.utils import Score

dice_set = [1, 2, 3, 4, 5, 6]
dice_choices = [(i, i) for i in dice_set]

class Game(models.Model):
    max_score = models.IntegerField(default=5000)
    turn_index = models.IntegerField(default=1)
    last_turn = models.BooleanField(default=False)
    status = models.CharField(max_length=10, default='active')
    start_time = models.DateTimeField(default=datetime.now)

    @property
    def current_player(self):
        return self.player_set.filter(is_current_player=True).first()

    def start_round(self):
        starting_player = self.advance_player()

    @property
    def game_over(self):
        return self.player_set.filter(had_last_turn=True).count() == self.player_set.count()

    def check_status(self):
        if self.game_over:
            self.status = 'over'
            self.save()

    def get_winner(self):
        is_tie = False
        winner = None
        max_score = self.player_set.all().aggregate(maxscore=Max('total_score'))['maxscore']
        winner_qs = self.player_set.filter(total_score=max_score)
        winner_count = winner_qs.count()
        if winner_count > 1:
            is_tie = True
            winner = winner_qs.all()
        else:
            winner = winner_qs.first()
        return winner, is_tie

    @property
    def turn_over(self):
        players_went = Turn.objects.filter(player_id__in=[p.pk for p in self.player_set.all()], index=self.turn_index).count()
        return players_went == self.player_set.count()

    def initiate_last_turn(self):
        self.last_turn = True
        self.save()

    def advance_player(self):
        if self.turn_over:
            self.turn_index += 1
            self.save()
        if not self.current_player:
            next_player = random.choice(self.player_set.all())
            next_player.is_current_player = True
            next_player.save()
        else:
            if self.current_player.player_order == self.player_set.count():
                next_player_index = 1
            else:
                next_player_index = self.current_player.player_order +1
            self.current_player.end_turn()
            next_player = self.player_set.get(player_order=next_player_index)
            next_player.is_current_player = True
            next_player.save()
        next_player.start_turn()
        return next_player

    @property
    def max_score_reached(self):
        for player in self.player_set.all():
            if player.total_score >= self.max_score:
                return True
        return False

    @property
    def ordered_players(self):
        return self.player_set.order_by('player_order').all()


    @property
    def history(self):
        history = {}
        players = self.player_set.order_by('player_order')
        for turn_index in reversed(range(1, self.turn_index + 1)):
            this_turn = history.get(
                turn_index, {}
            )
            for player in players:
                turn = Turn.objects.filter(player=player, index=turn_index).first()
                if turn:
                    this_turn[player] = DiceSelection.objects.filter(turn=turn).all()
            history[turn_index] = this_turn
        return history

    @classmethod
    def lazy_cleanup(cls):
        expire_threshold = datetime.now() - timedelta(1)
        cls.objects.filter(start_time__lte=expire_threshold).delete()


class Player(models.Model):
    name = models.CharField(max_length=30)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    is_current_player = models.BooleanField(default=False)
    player_order = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    had_last_turn = models.BooleanField(default=False)

    def __str__(self):
        return "game: {} // {}".format(self.game.pk, self.name)

    def save(self, *args, **kwargs):
        if self.is_current_player:
            Player.objects.filter(game=self.game, is_current_player=True).update(is_current_player=False)
        super(Player, self).save(*args, **kwargs)

    @property
    def current_turn(self):
        return self.turn_set.filter(status='current').first()

    def end_turn(self):
        if self.current_turn:
            new_points = self.current_turn.end()
            self.total_score += new_points
            self.save()
            if self.total_score >= self.game.max_score:
                self.game.initiate_last_turn()
        if self.game.last_turn:
            self.had_last_turn = True
            self.save()
            self.game.check_status()

    def start_turn(self):
        if self.current_turn:
            self.end_turn()
        new_turn = Turn(index=self.game.turn_index, player=self, game=self.game, status='current')
        new_turn.save()
        if self.game.last_turn:
            self.had_last_turn = True
            self.save()
            self.game.check_status()

    @property
    def history(self):
        return self.turn_set.order_by('-pk').all()


class Turn(models.Model):
    index = models.IntegerField(default=1)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=[('current', 'current'), ('over', 'over')])
    score = models.IntegerField(default=0)
    available_dice = models.IntegerField(default=6)
    scrubbed = models.BooleanField(default=False)
    dice_1 = models.IntegerField(choices=dice_choices, null=True)
    dice_2 = models.IntegerField(choices=dice_choices, null=True)
    dice_3 = models.IntegerField(choices=dice_choices, null=True)
    dice_4 = models.IntegerField(choices=dice_choices, null=True)
    dice_5 = models.IntegerField(choices=dice_choices, null=True)
    dice_6 = models.IntegerField(choices=dice_choices, null=True)

    def end(self):
        if self.status != 'over':
            for selection in self.diceselection_set.all():
                self.score += selection.score
            self.status = 'over'
            self.save()
        return self.score

    def roll(self):
        self.dice_1 = None
        self.dice_2 = None
        self.dice_3 = None
        self.dice_4 = None
        self.dice_5 = None
        self.dice_6 = None

        if self.available_dice >= 1:
            self.dice_1 = random.choice(dice_set)
        if self.available_dice >= 2:
            self.dice_2 = random.choice(dice_set)
        if self.available_dice >= 3:
            self.dice_3 = random.choice(dice_set)
        if self.available_dice >= 4:
            self.dice_4 = random.choice(dice_set)
        if self.available_dice >= 5:
            self.dice_5 = random.choice(dice_set)
        if self.available_dice >= 6:
            self.dice_6 = random.choice(dice_set)
        self.save()

    def scrub(self):
        for selection in self.diceselection_set.all():
            selection.delete()

        scrubbed_selection = DiceSelection(
            turn=self,
            score=0,
            score_type='farkle'
        )
        scrubbed_selection.save()
        self.scrubbed = True
        self.score = 0
        self.save()

    @property
    def rolled_values(self):
        slots = [self.dice_1, self.dice_2, self.dice_3, self.dice_4, self.dice_5, self.dice_6, ]
        values = {}
        idx = 1
        for die in slots:
            if die:
                values['dice_{}'.format(idx)] = {'value': die, 'img_url': 'images/dice/{}.png'.format(die) }
            idx +=1
        return values


class DiceSelection(models.Model):
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE)
    dice_1 = models.IntegerField(choices=dice_choices, null=True)
    dice_2 = models.IntegerField(choices=dice_choices, null=True)
    dice_3 = models.IntegerField(choices=dice_choices, null=True)
    dice_4 = models.IntegerField(choices=dice_choices, null=True)
    dice_5 = models.IntegerField(choices=dice_choices, null=True)
    dice_6 = models.IntegerField(choices=dice_choices, null=True)
    score = models.IntegerField(default=0)
    score_type = models.CharField(max_length=30, blank=True, null=True)

    @property
    def scored_values(self):
        slots = [self.dice_1, self.dice_2, self.dice_3, self.dice_4, self.dice_5, self.dice_6, ]
        values = {
            'score': self.score,
            'score_type': self.score_type,
            'dice': {}
        }
        idx = 1
        for die in slots:
            if die:
                values['dice']['dice_{}'.format(idx)] = {'value': die, 'img_url': 'images/dice/{}.png'.format(die) }
            idx +=1
        return values

    def save(self, *args, **kwargs):
        score_set = []
        slots = [self.dice_1, self.dice_2, self.dice_3, self.dice_4, self.dice_5, self.dice_6, ]
        for die in slots:
            if die and die > 0:
                score_set.append(die)
        score = Score(score_set)
        self.score = score.score
        self.score_type = score.score_type
        if self.score == 0:
            self.score_type = 'farkle'
        super(DiceSelection, self).save(*args, **kwargs)

    @classmethod
    def create(cls, turn, selected_dice):
        new_selection = cls(turn=turn)
        if selected_dice.get('dice_1'):
            new_selection.dice_1 = int(selected_dice['dice_1'])
            new_selection.turn.available_dice -= 1
            new_selection.turn.dice_1 = 0
        if selected_dice.get('dice_2'):
            new_selection.dice_2 = int(selected_dice['dice_2'])
            new_selection.turn.available_dice -= 1
            new_selection.turn.dice_2 = 0
        if selected_dice.get('dice_3'):
            new_selection.dice_3 = int(selected_dice['dice_3'])
            new_selection.turn.dice_3 = 0
            new_selection.turn.available_dice -= 1
        if selected_dice.get('dice_4'):
            new_selection.dice_4 = int(selected_dice['dice_4'])
            new_selection.turn.available_dice -= 1
            new_selection.turn.dice_4 = 0
        if selected_dice.get('dice_5'):
            new_selection.dice_5 = int(selected_dice['dice_5'])
            new_selection.turn.available_dice -= 1
            new_selection.turn.dice_5 = 0
        if selected_dice.get('dice_6'):
            new_selection.dice_6 = int(selected_dice['dice_6'])
            new_selection.turn.available_dice -= 1
            new_selection.turn.dice_6 = 0
        new_selection.save()
        if new_selection.turn.available_dice == 0:
            new_selection.turn.available_dice = 6
        new_selection.turn.save()
