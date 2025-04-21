import graphene
from graphene_django import DjangoObjectType

from blog.models import Category, Post


class CategoryType(DjangoObjectType):
    class Meta:
         model = Category
         fields = ("id", "name", "posts", "level", "slug", "parent")
         interfaces = (graphene.relay.Node,)
         filter_fields = {
            'name': ['exact', 'icontains'],
            'level': ['exact'],
            'parent': ['exact'],
         }
        
        
class PostType(DjangoObjectType):
    class Meta:
         model = Post
         interfaces = (graphene.relay.Node,)
         filter_fields = {
            'title': ['exact', 'icontains'],
            'author__username': ['exact', 'icontains'],
            'category__name': ['exact', 'icontains'],
        }