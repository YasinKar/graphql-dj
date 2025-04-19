from django.db import models
from users.models import User

class BaseModel(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    is_delete = models.BooleanField(default=False) # soft delete

    class Meta:
        abstract=True


class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='blogs')
    title = models.CharField(max_length=200)
    context = models.TextField()
    likes = models.IntegerField(default=0)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'title'], name='unique_blog_title_per_author')
        ]

    def __str__(self):
        return f"{self.author.username} - {self.title}"