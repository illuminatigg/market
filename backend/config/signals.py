from accounts.models import CustomUser, Profile, RegistrationRequest
from django.db.models.signals import post_save
from django.dispatch import receiver


# @receiver(post_save, sender=CustomUser)
# def creat_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)


# @receiver(post_save, sender=RegistrationRequest)
# def create_user
