from django.db import models
import random
from copy import deepcopy

class Score(object):
    score = 0

    def get_sets(self):
        sets = {}
        for d in self.selection:
            sets[d] = sets.get(d, 0)
            sets[d] += 1
        return sets

    @property
    def has_any_of_a_kind(self):
        sets = self.get_sets()
        for idx, count in sets.items():
            if count >= 3:
                return True
        return False

    @property
    def has_one_or_five(self):
        return 1 in self.selection or 5 in self.selection

    @property
    def is_three_of_a_kind(self):
        return len(self.selection) == 3 and len(set(self.selection)) == 1

    @property
    def is_four_of_a_kind(self):
        return len(self.selection) == 4 and len(set(self.selection)) == 1

    @property
    def is_five_of_a_kind(self):
        return len(self.selection) == 5 and len(set(self.selection)) == 1

    @property
    def is_six_of_a_kind(self):
        return len(self.selection) == 6 and len(set(self.selection)) == 1

    @property
    def is_a_straight(self):
        return len(self.selection) == 6 and len(set(self.selection)) == 6

    @property
    def is_three_pairs(self):
        if len(self.selection) == 6:
            sets = self.get_sets()
            num_of_pairs = 0
            for k, amount in sets.items():
                if amount == 2:
                    num_of_pairs += 1
            return num_of_pairs == 3
        return False



    @property
    def is_two_triplets(self):
        if len(self.selection) == 6:
            sets = self.get_sets()
            num_of_trips = 0
            for k, amount in sets.items():
                if amount == 3:
                    num_of_trips += 1
            return num_of_trips == 2
        return False

    @property
    def is_four_of_kind_and_pair(self):
        if len(self.selection) == 6:
            sets = self.get_sets()
            has_a_four = False
            has_a_pair = False
            if len(sets) == 2:
                for k, amount in sets.items():
                    if amount == 4:
                        has_a_four = True
                    if amount == 2:
                        has_a_pair = True
                return has_a_pair and has_a_four
        return False

    @property
    def is_all_fives(self):
        return len(set(self.selection)) == 1 and self.selection[0] ==  5

    @property
    def is_all_ones(self):
        return len(set(self.selection)) == 1 and self.selection[0] == 1


    def __init__(self, selection):
        self.selection = selection
        self.score = 0
        if self.is_four_of_kind_and_pair or self.is_two_triplets:
            self.score = 2500
        elif self.is_a_straight or self.is_three_pairs:
            self.score = 1500
        elif self.is_three_of_a_kind and self.is_all_ones:
            self.score = 300
        elif self.is_three_of_a_kind:
            self.score = self.selection[0] * 100
        elif self.is_four_of_a_kind:
            self.score = 1000
        elif self.is_five_of_a_kind:
            self.score = 2000
        elif self.is_six_of_a_kind:
            self.score = 3000
        elif self.is_all_fives:
            self.score = len(self.selection) * 50
        elif self.is_all_ones:
            self.score = len(self.selection) * 100


class Die(object):
    value = None
    def __init__(self, value=None):
        if value is None and value not in [1, 2, 3, 4, 5, 6]:
            self.value = random.choice([1, 2, 3, 4, 5, 6])


class Set(object):
    """ A set represents a series of dice rolls, starting from 6 dice
        You can continue rolling as long as you have at least 1 die available
    """

    dice_amount = 6
    selections = []

    def __init__(self):
        self.dice_amount = 6
        self.selections = []

    def roll(self):
        self.dice = []
        for i in range(0, self.dice_amount):
            self.dice.append(Die())

    @property
    def has_score(self):
        test_score = Score([d.value for d in self.dice])
        if test_score.has_one_or_five:
            return True
        if test_score.has_any_of_a_kind:
            return True
        if test_score.is_a_straight:
            return True
        if test_score.is_two_triplets:
            return True
        if test_score.is_three_pairs:
            return True
        if test_score.is_four_of_kind_and_pair:
            return True
        return False

    @property
    def value(self):
        return [d.value for d in self.dice]

    def make_selection(self, selection_list):
        turn_selection = []
        remaining_dice = []
        for selection_val in selection_list:
            idx = 0
            for dv in self.dice:
                if dv.value == selection_val:
                    turn_selection.append(selection_val)
                    self.dice_amount -= 1
                    del(self.dice[idx])
                    break
                idx += 1
        self.selections.append(turn_selection)

    def __str__(self):
        return [d.value for d in self.dice]

    def __unicode__(self):
        return [d.value for d in self.dice]


class Turn(object):
    """ A turn represents multiple sets of dice rolls
        Each set of dice rolls has a score
        A total score, as long as you don't scrub, is calculated from each
        set at the end of a turn
    """
    selection_scores = []
    dice_amount = 6
    roll = None
    total_score = 0
    sets = []
    current_set = None

    def __init__(self):
        self.new_turn()

    def new_turn(self):
        self.selections = []
        self.selection_scores = []
        self.dice_amount = 6
        self.roll = None
        self.total_score = 0
        self.sets = []
        self.new_set()

    def new_set(self):
        if self.current_set:
            set_copy = deepcopy(self.current_set)
            self.sets.append(set_copy)
        self.current_set = Set()

    def scrub(self):
        self.current_set.selections = []

    def flush(self):
        self.current_set.dice_amount = 6

    def get_score(self):
        self.total_score = 0
        self.selection_scores = []
        if self.current_set not in self.sets:
            self.sets.append(self.current_set)
        for _set in self.sets:
            for selection in _set.selections:
                selection_score = Score(selection)
                self.selection_scores.append({'dice': selection, 'score': selection_score})
                self.total_score += selection_score.score


class Player(object):
    def __init__(self, name):
        self.name = name
        self.turns = []
        self.total_score = 0
        self.current_turn = None
        self.had_last_turn = False

    def end_turn(self):
        turn_score = 0
        if self.current_turn:
            self.current_turn.get_score()
            self.total_score += self.current_turn.total_score
            turn_score = self.current_turn.total_score
            current_turn_copy = deepcopy(self.current_turn)
            self.turns.append(current_turn_copy)
        self.current_turn = None
        return turn_score, self.total_score

    def start_turn(self):
        if self.current_turn:
            current_turn_copy = deepcopy(self.current_turn)
            self.turns.append(current_turn_copy)
        self.current_turn = Turn()


class Game(object):
    def __init__(self, players, max_score=5000):
        self.players = []
        self.max_score = max_score
        for player in players:
            playerobj = Player(player)
            self.players.append(playerobj)
        self.current_player_index = len(self.players) - 1
        self.current_player = self.players[self.current_player_index]
        self.current_turn = None

    @property
    def max_score_reached(self):
        for player in self.players:
            if player.total_score >= self.max_score:
                return True
        return False

    def advance_to_next_player(self):
        if self.current_player_index == len(self.players) - 1:
            self.current_player_index = 0
        else:
            self.current_player_index += 1
        self.current_player.end_turn()
        self.current_player = self.players[self.current_player_index]
        self.current_player.start_turn()

    def print_scores(self):
        for player in self.players:
            print("{}:\t\t\t{} points".format(player.name, player.total_score))

    def print_history(self):
        history = {}
        for player in self.players:
            print('{}'.format(player.name))
            turn_idx = 1
            for turn in player.turns:
                print("Turn {}".format(turn_idx))
                for _set in turn.sets:
                    set_score = 0
                    if not _set.selections:
                        print("SCRUB")
                    else:
                        for selection in _set.selections:
                            selection_score = Score(selection)
                            print("{} = {}".format(selection, selection_score.score))
                            set_score += selection_score.score
                    print("{} set total".format(set_score))
                turn_idx += 1

    @property
    def all_players_had_last_turn(self):
        for player in self.players:
            if not player.had_last_turn:
                return False
        return True

    @property
    def is_last_turn(self):
        for player in self.players:
            if player.had_last_turn:
                return True
        return False


