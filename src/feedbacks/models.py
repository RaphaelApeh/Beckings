from django.db import models
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class FeedBackManager(models.Manager):
    

    def create_for_user(self, user, **kwargs):
        if not user:
            obj = self.create(**kwargs)
            return None, obj
        
        email = user.email
        user_pk = user.pk
        kwargs.update(
            email=email,
            user_id=user_pk
        )
        obj = self.create(**kwargs)
        return obj.get_user(), obj


class ComplainType(models.TextChoices):

    ORDER = "order", "Order"
    OTHER = "other", "Other"
    

class FeedBack(models.Model):

    email = models.EmailField()
    user_id = models.CharField(
        max_length=300,
        default=""
    )
    complain = models.TextField()
    complain_type = models.CharField(
        max_length=20,
        choices=ComplainType.choices,
        default=ComplainType.OTHER 
    )
    resolved = models.BooleanField(default=False)
    timestamp = models.DateField(auto_now=True)

    objects = FeedBackManager()


    def __str__(self):
        return self.email


    def get_user(self):
        if not self.user_id:
            return
        pk = UserModel._meta.pk.to_python(self.user_id)
        try:
            return UserModel._default_manager.get(pk=pk, email=self.email)
        except UserModel.DoesNotExist:
            return