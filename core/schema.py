import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from graphql_auth import mutations
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth.decorators import login_required

from blog.models import Category, Post
from blog.types import CategoryType, PostType


### Query ###

class InactiveOnlyConnectionField(DjangoFilterConnectionField):
    def resolve_queryset(self, connection, iterable, info, args, *a, **kw):
        queryset = super().resolve_queryset(connection, iterable, info, args, *a, **kw)
        return queryset.filter(is_delete=False)


class Query(UserQuery, MeQuery, graphene.ObjectType):
   all_categories = InactiveOnlyConnectionField(
      CategoryType,
   )
   category_by_name = graphene.Field(
      CategoryType,
      name=graphene.String(required=True)
   )
   all_posts = InactiveOnlyConnectionField(
      PostType
   )
   post_by_name = graphene.Field(
      PostType,
      author=graphene.ID(required=True),
      title=graphene.String(required=True)
   )
   
   def resolve_category_by_name(root, info, name):
      try:
         return Category.objects.get(name=name)
      except Category.DoesNotExist:
         return None
      
   def resolve_post_by_name(root, info, author, title):
        try:
            return Post.objects.get(author=author, title=title)
        except Post.DoesNotExist:
            return None


### Mutation ###

class AuthMutation(graphene.ObjectType):
   register = mutations.Register.Field()
   verify_account = mutations.VerifyAccount.Field()
   token_auth = mutations.ObtainJSONWebToken.Field()
   update_account = mutations.UpdateAccount.Field()
   resend_activation_email = mutations.ResendActivationEmail.Field()
   send_password_reset_email = mutations.SendPasswordResetEmail.Field()
   password_reset = mutations.PasswordReset.Field()
   password_change = mutations.PasswordChange.Field()


class CreatePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        category_id = graphene.ID(required=True)
        title = graphene.String(required=True)
        thumbnail = graphene.String(required=True)  # base64
        context = graphene.String(required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, category_id, title, thumbnail, context):
        user = info.context.user

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise GraphQLError("Category not found")

        post = Post.objects.create(
            author=user,
            category=category,
            title=title,
            thumbnail=thumbnail,
            context=context
        )
        return CreatePost(post=post)


class UpdatePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        post_id = graphene.ID(required=True)
        title = graphene.String()
        context = graphene.String()
        thumbnail = graphene.String()
        category_id = graphene.ID()

    @classmethod
    @login_required
    def mutate(cls, root, info, post_id, title=None, context=None, thumbnail=None, category_id=None):
        user = info.context.user

        try:
            post = Post.objects.get(id=post_id, author=user)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found or you do not have permission to edit.")

        if title:
            post.title = title
        if context:
            post.context = context
        if thumbnail:
            post.thumbnail = thumbnail
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                post.category = category
            except Category.DoesNotExist:
                raise GraphQLError("Category not found")

        post.save()
        return UpdatePost(post=post)


class DeletePost(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        post_id = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, post_id):
        user = info.context.user
        try:
            post = Post.objects.get(id=post_id, author=user)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found or you do not have permission to delete.")

        post.delete()
        return DeletePost(ok=True)


class Mutation(AuthMutation, graphene.ObjectType):
   create_post = CreatePost.Field()
   update_post = UpdatePost.Field()
   delete_post = DeletePost.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)