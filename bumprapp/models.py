from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import constants


class Plate(models.Model):
    plate_text = models.CharField(max_length=8, blank=False)
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    first_recorded = models.DateTimeField('Date of first lookup/review/rating', default=timezone.now)
    driver = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    claimed = models.BooleanField(default=False)

    state = models.CharField(
        max_length=2,
        choices=constants.STATES,
        blank=False
    )

    car_color = models.CharField(
        max_length=3,
        choices=constants.CAR_COLORS,
        default='UNS',
        blank=False
    )

    def __str__(self):
        return self.plate_text

    def get_absolute_url(self):
        '''Return detail URL for Plate object. This allows us to use redirect(Plate)'''
        return reverse('plate_detail', args=[self.state, self.plate_text])

    def get_state_disp(self):
        for tups in constants.STATES:
            if self.state.upper() == tups[0]:
                return tups[1]
        return 'Undefined State'

    def get_rating(self):
        if self.upvotes+self.downvotes == 0:
            return 0
        return "{0:.2f}".format(self.upvotes/(self.upvotes+self.downvotes)*100)

    def net_votes(self):
        ''' Return total net votes '''
        return self.upvotes - self.downvotes

    def is_pos(self):
        '''Returns true if net votes are positive'''
        return self.net_votes() > 0

    def is_neg(self):
        '''Returns true if net votes are negative'''
        return self.net_votes() < 0

    def number_of_votes(self):
        '''Return total number of votes made'''
        return self.upvotes + self.downvotes


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    plate = models.ForeignKey(Plate, on_delete=models.CASCADE, blank=False, null=False)
    comment_text = models.CharField(max_length=140)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.comment_text


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.__str__()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
