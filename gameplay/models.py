from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


GAME_STATUS_CHOICES = (
    ('F', 'First player to Move'),
    ('S', 'Second player to Move'),
    ('W', 'First player Wins'),
    ('L', 'Second player Wins'),
    ('D', 'Game ends in a Draw'),
)

BOARD_SIZE = 3

class GamesQuerySet(models.QuerySet):
    def games_for_user(self, user):
        return self.filter(
            Q(first_player = user) | Q(second_player = user)
        )

    def active(self):
        return self.filter(
            Q(status = 'F') | Q(status = 'S')
        )


class Game(models.Model):
    first_player = models.ForeignKey(User, related_name="games_first_player",on_delete=models.CASCADE)
    second_player = models.ForeignKey(User, related_name="games_second_player",on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1,default='F',choices=GAME_STATUS_CHOICES)
    objects = GamesQuerySet.as_manager()

    def board(self):
        board = [[None for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
        for move in self.move_set.all():
            board[move.y][move.x] = move
        return board

    def is_users_move(self, user):
        return (user == self.first_player and self.status == 'F') or\
               (user == self.second_player and self.status == 'S')

    def new_move(self):
        if self.status not in 'F' and self.status not in 'S':
            raise ValueError("Cannot make move on finished game")

        return Move(
            game = self,
            by_first_player=self.status == 'F'
        )

    def update_after_move(self, move):
        self.status = self.get_game_status_after_move(move)


    def get_game_status_after_move(self, move):
        x, y = move.x, move.y
        board = self.board()
        if (board[y][0] == board[y][1] == board[y][2]) or\
                (board[0][x] == board[1][x] == board[2][x]) or\
                (board[0][0] == board[1][1] == board[2][2]) or\
                (board[0][2] == board[1][1] == board[2][0]):
            return 'W' if move.by_first_player else "L"
        if self.move_set.count() >= BOARD_SIZE*BOARD_SIZE:
            return 'D'
        return 'S' if self.status == 'F' else 'F'

    def get_absolute_url(self):
        return reverse('gameplay_detail', args=[self.id])

    def __str__(self):
         return "{0} vs {1}".format(self.first_player, self.second_player)

class Move(models.Model):
    x = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(BOARD_SIZE-1)]
    )
    y = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(BOARD_SIZE-1)]
    )
    comment = models.CharField(max_length=300, blank=True)
    by_first_player = models.BooleanField(editable=False)
    game = models.ForeignKey(Game, editable=False, on_delete=models.CASCADE)

    def __eq__(self, other):
        if other is None:
            return False
        return other.by_first_player == self.by_first_player

    def save(self, *args, **kwargs):
        super(Move, self).save(*args, **kwargs)
        self.game.update_after_move(self)
        self.game.save()
