from django.forms import (
    Form,
    IntegerField,
    CharField
)

class FormHowManyPlayers(Form):
    how_many_players = IntegerField()


class FormPlayerName(Form):
    player_name = CharField(required=True)
