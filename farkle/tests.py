from django.test import TestCase
from farkle.models import Score, Turn, Set, Die

# Create your tests here.
class ScoreTest(TestCase):
    def test_50_points(self):
        score = Score([5, 2, 3, 3, 6])
        self.assertEqual(score.score, 50)

    def test_2_50_points(self):
        score = Score([5, 5, 3, 3, 6])
        self.assertEqual(score.score, 100)

    def test_100_points(self):
        score = Score([5, 5, 3, 3, 6])
        self.assertEqual(score.score, 100)

    def test_2_100_points(self):
        score = Score([1, 1, 3, 3, 6])
        self.assertEqual(score.score, 200)

    def test_2_100_points_and_1_50(self):
        score = Score([1, 1, 3, 3, 5])
        self.assertEqual(score.score, 250)

    def test_3ok_2(self):
        dice = [2, 2, 2]
        score = Score(dice)
        self.assertEqual(score.score, 200)

    def test_3ok_3(self):
        dice = [3, 3, 3]
        score = Score(dice)
        self.assertEqual(score.score, 300)

    def test_3ok_4(self):
        dice = [4, 4, 4]
        score = Score(dice)
        self.assertEqual(score.score, 400)

    def test_3ok_5(self):
        dice = [5, 5, 5]
        score = Score(dice)
        self.assertEqual(score.score, 500)

    def test_3ok_6(self):
        dice = [6, 6, 6]
        score = Score(dice)
        self.assertEqual(score.score, 600)

    def test_is_a_straight(self):
        dice = [3, 2, 4, 5, 1, 6]
        score = Score(dice)
        self.assertEqual(score.score, 1500)

    def test_is_3_pairs(self):
        dice = [6, 6, 5, 5, 3, 3]
        score = Score(dice)
        self.assertEqual(score.score, 1500)

    def test_is_four_of_kind_and_pair(self):
        dice = [3, 3, 3, 3, 1, 1]
        score = Score(dice)
        self.assertEqual(score.score, 2500)

    def test_total_scores(self):
        dice_sets = [
            [6, 6, 6],  # should be 600
            [5, 5],  # should be 100
            [1],  # should be 100
        ]

        turn = Turn()
        turn.selections = dice_sets
        turn.get_score()
        self.assertEqual(turn.total_score, 800)

        dice_sets = [
            [6, 6, 6,],  # should be 600
            [5, 1],  # should be 150
        ]

        turn = Turn()
        turn.selections = dice_sets
        turn.get_score()
        self.assertEqual(turn.total_score, 750)

        dice_sets = [
            [6, 6, 3, 3],  # should be nothing
            [5, 1],  # should be 150
        ]

        turn = Turn()
        turn.selections = dice_sets
        turn.get_score()
        self.assertEqual(turn.total_score, 150)


class TestTurn(TestCase):
    def test_game(self):
        myturn = Turn()
        myturn.current_set.roll()
        myturn.current_set.dice = [
            Die(2),
            Die(2),
            Die(2),
            Die(6),
            Die(5),
        ]
        myturn.current_set.make_selection([0, 1, 2, 3])
        myturn.current_set.roll()

        self.assertEqual(len(myturn.current_set.dice), 2)
        myturn.current_set.dice = [
            Die(6),
            Die(2),
        ]
        self.assertFalse(myturn.current_set.has_score)
