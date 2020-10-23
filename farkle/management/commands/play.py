from django.core.management.base import BaseCommand, CommandError

from farkle.models import Turn, Score, Game


class Command(BaseCommand):
    def _is_scoring_selection(self, keepers):
        test_score = Score(keepers)
        return test_score.score > 0

    def _selection_is_valid(self, keepers, game_set):
        available_dice = [d.value for d in game_set.dice]
        for kv in keepers:
            idx = 0
            matched = False
            for dv in available_dice:
                if kv == dv:
                    del(available_dice[idx])
                    matched = True
                    break
                idx += 1
            if not matched:
                return False
        return matched

    def _pick_dice(self, game_set, print_remaining_dice=False):
        selected_scoring_set = False
        while not selected_scoring_set:
            if print_remaining_dice:
                print('''
                Remaining dice:
                {}
                '''.format(', '.join(str(d.value) for d in game_set.dice))
                )
                keepers = input('Enter dice to keep or R to roll continue: ')
                if keepers.upper().strip() == 'R':
                    return False
            else:
                keepers = input('Enter list of dice to keep: ')
                if ',' in keepers:
                    keepers = keepers.split(',')
                elif ' ' in keepers:
                    keepers = keepers.split(' ')
            try:
                keeper_values = [int(k) for k in keepers]
                if not self._selection_is_valid(keeper_values, game_set):
                    print('Those dice are not in your roll. Nice try.')
                elif not self._is_scoring_selection(keeper_values):
                    print('That selection has no score. Try something else.')
                else:
                    selected_scoring_set = True
                    game_set.make_selection(keeper_values)
                    keep_picking = True
            except ValueError:
                print('You need to enter the values of the dice you wish to keep. Only numbers please.')
        return True


    def _do_turn(self, player):
        myturn = player.current_turn
        scrubbed = False
        keep_rolling = True
        while keep_rolling and myturn.current_set.dice_amount > 0:
            keep_rolling_q = input('You have {} dice. Ready to roll? (Y/N): '.format(myturn.current_set.dice_amount)).strip().upper()
            if keep_rolling_q == 'Y':
                myturn.current_set.roll()
                print('''
                    You rolled:
                    {}
                '''.format(', '.join(str(d.value) for d in myturn.current_set.dice))
                )
                if myturn.current_set.has_score:
                    self._pick_dice(myturn.current_set)
                    keep_picking = True
                    while myturn.current_set.has_score and keep_picking:
                        keep_picking = self._pick_dice(myturn.current_set, True)

                    if myturn.current_set.dice_amount == 0:
                        myturn.flush()

                else:
                    print("D'oh! You scrubbed! 0 points :(")
                    myturn.scrub()
                    scrubbed = True
                    keep_rolling = False
            elif keep_rolling_q == 'N':
                keep_rolling = False
            else:
                print('Enter Y to roll or N to end your turn')
                keep_rolling = True

        if not scrubbed:
            myturn.get_score()
            return myturn.total_score
        return 0

    def handle(self, *args, **options):
        players_names = [st.strip() for st in input("Who's plaing?? Enter each name separated by a comma: ").split(',')]
        max_score = input("What score are you playing to? (default: 5000) ")
        try:
            max_score = int(max_score)
        except ValueError:
            max_score = 5000

        farkle = Game(players_names, max_score)
        last_turn = False
        first_turn = True
        game_on = True

        while not farkle.all_players_had_last_turn:
            farkle.advance_to_next_player()
            player = farkle.current_player
            print("{}'s Turn! You have {} points so far.".format(player.name, player.total_score))
            player_has_rolled = False
            while not player_has_rolled:
                if not first_turn:
                    if farkle.is_last_turn:
                        print('This is your last turn!')
                    action = input("Would you like to (R) Roll or (S) see the current scores or (H) to see the score history? [R/S/H] ")
                else:
                    action = 'R'
                    first_turn = False
                action = action.upper().strip()
                if action == 'R':
                    turn_score = self._do_turn(player)
                    current_score, total_score = player.end_turn()
                    print('you scored {} points in this turn! You now have {} points total'.format(
                        current_score, total_score
                        )
                    )
                    player_has_rolled = True
                    if farkle.max_score_reached:
                        player.had_last_turn = True
                elif action == 'S':
                    farkle.print_scores()
                elif action == 'H':
                    farkle.print_history()
                else:
                    print("that's not a valid selection")


        winning_score = 0
        winner = None
        for player in farkle.players:
            if player.total_score > winning_score:
                winning_score = player.total_score
                winner = player.name
        print('{} is the winner! {} points to {}!'.format(winner, winning_score, winner))
        view_history = input('Would you like to view the whole score sheet? [Y/N] ').upper().strip()
        if view_history == 'Y':
            farkle.print_history()
