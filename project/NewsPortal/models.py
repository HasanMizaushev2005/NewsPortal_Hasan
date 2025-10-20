from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse_lazy


class Author(models.Model):
    rating = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def update_rating(self):
        # суммарный рейтинг всех статей автора, умноженные на 3
        post_list = Post.objects.filter(author=self)
        post_rating_list = [post.rating for post in post_list]
        post_rating_sum = sum(post_rating_list) * 3

        # суммарный рейтинг всех комментариев автора
        comment_list = Comment.objects.filter(user=self.user)
        comment_rating_list = [comment.rating for comment in comment_list]
        comment_rating_sum = sum(comment_rating_list)

        # суммарный рейтинг всех комментариев к статьям автора
        author_posts = Post.objects.filter(author=self)
        author_post_ids = [post.id for post in author_posts]
        post_comments = Comment.objects.filter(post__id__in=author_post_ids)
        post_comment_rating_list = [comment.rating for comment in post_comments]
        post_comment_rating_sum = sum(post_comment_rating_list)

        # Итоговый расчет
        self.rating = post_rating_sum + comment_rating_sum + post_comment_rating_sum
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name_category = models.CharField(max_length=255, unique=True)
    subscribers = models.ManyToManyField(User, related_name='categories')

    def __str__(self):
        return self.name_category


class Post(models.Model):
    article = 'СТ'
    news = 'НВ'
    POSITIONS = [(article, 'статья'), (news, 'новость')]
    positions = models.CharField(max_length=2, choices=POSITIONS, default=news)
    datetime = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    author = models.ForeignKey("Author", on_delete=models.CASCADE)

    category = models.ManyToManyField("Category", through='PostCategory')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...' if len(self.text) > 124 else self.text

    def __str__(self):
        return f'{self.title}: {self.text}'

    def get_absolute_url(self):
        return reverse_lazy("post_detail", kwargs={"pk": self.pk})

class PostCategory(models.Model):
    post = models.ForeignKey(Category, on_delete=models.CASCADE)
    category = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField()
    datetime = models.DateTimeField(auto_now_add = True)
    rating = models.IntegerField(default=0)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()