from django.db import models
from users.models import User
from mptt.models import TreeForeignKey, MPTTModel
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    is_delete = models.BooleanField(default=False) # soft delete

    class Meta:
        abstract=True

class Category(MPTTModel, BaseModel):
    name = models.CharField(
        verbose_name=_("Category Name"),
        help_text=_("Required and unique"),
        max_length=255,
        unique=True,
    )
    slug = models.SlugField(verbose_name=_("Category safe URL"), max_length=255, unique=True)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_name="posts")
    title = models.CharField(max_length=200, verbose_name=_("title"), help_text=_("Required"),)
    thumbnail = models.ImageField(upload_to='blogs')
    context = models.TextField()
    likes = models.IntegerField(default=0)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'title'], name='unique_blog_title_per_author')
        ]

    def __str__(self):
        return f"{self.author.username} - {self.title}"