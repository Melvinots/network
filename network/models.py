from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False,  blank=True, related_name='following_users')
    following = models.ManyToManyField('self', symmetrical=False,  blank=True, related_name='followers_users')

    def __str__(self):
        return self.username

class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User,  blank=True, related_name='liked_posts')

    def __str__(self):
        return f"Poster: {self.poster}"
    
    def serialize(self, current_user):
        return {
            "id": self.id,
            "poster": self.poster.username,
            "content": self.content,
            "date_time": self.date_time.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes.count(),
            "is_poster": self.poster == current_user,
            "is_liked": current_user in self.likes.all()
        }

