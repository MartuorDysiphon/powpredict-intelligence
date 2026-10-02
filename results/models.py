from django.db import models

# Create your models here.
from django.db import models


class DrawResult(models.Model):
    GAME_CHOICES = [
        ("lotto",       "Lotto"),
        ("lotto-plus-1","Lotto Plus 1"),
        ("lotto-plus-2","Lotto Plus 2"),
        ("powerball",   "PowerBall"),
        ("powerball-plus", "PowerBall Plus"),
        ("daily",       "Daily Lotto"),
    ]

    game       = models.CharField(max_length=32, choices=GAME_CHOICES, db_index=True)
    draw_date  = models.DateField(db_index=True)
    main_1     = models.PositiveSmallIntegerField()
    main_2     = models.PositiveSmallIntegerField()
    main_3     = models.PositiveSmallIntegerField()
    main_4     = models.PositiveSmallIntegerField()
    main_5     = models.PositiveSmallIntegerField()
    main_6     = models.PositiveSmallIntegerField(null=True, blank=True)
    bonus_ball = models.PositiveSmallIntegerField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("game", "draw_date")
        ordering = ["-draw_date"]

    def __str__(self):
        return f"{self.game} {self.draw_date}"

    @property
    def mains(self):
        return [n for n in (self.main_1, self.main_2, self.main_3, self.main_4, self.main_5, self.main_6) if n]

    @property
    def all_balls(self):
        out = list(self.mains)
        if self.bonus_ball is not None:
            out.append(self.bonus_ball)
        return out