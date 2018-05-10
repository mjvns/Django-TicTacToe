from django.db import models
from django.contrib.auth.models import User

class Invitation(models.Model):
    from_User = models.ForeignKey(User, related_name="invitations_sent", on_delete=models.CASCADE)
    to_User = models.ForeignKey(User, related_name="invitations_received",
                                verbose_name="User to invite",
                                help_text="Please select the User you want to play a game with.",
                                on_delete=models.CASCADE)
    message = models.CharField(max_length=300, blank=True,
                               verbose_name="Optional message",
                               help_text="It's always nice to add a friendly message!")
    timestamp = models.DateTimeField(auto_now_add=True)



