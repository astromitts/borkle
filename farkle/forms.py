from django.forms import (
    Form,
    IntegerField,
    CharField
)

class FormGameSetup(Form):
    how_many_players = IntegerField()
    how_many_points_are_you_playing_to = IntegerField()


class FormPlayerName(Form):
    player_name = CharField(required=True)
