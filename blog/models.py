from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    # заголовки статьи
    title = models.CharField(max_length=250)

    # используется для формирования URL`ов
    # unique_for_date - формировать уникальные URL’ы, ис-пользуя дату публикации статей и slug
    slug = models.SlugField(max_length=250, unique_for_date='publish')

    # поле явл. внешним ключом, отношение "один ко многим"
    # on_delete=models.CASCADE при удалении связанного пользователя база данных также удаляла написанные им статьи.
    # related name - обратная связь от User к Post
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts') 

    # основное содержание статьи, тип Text
    body = models.TextField()

    # дата публикации статьи
    publish = models.DateTimeField(default=timezone.now)

    # дата создания статьи
    created = models.DateTimeField(auto_now_add=True)

    # указывает на период, когда статья была отредактирована
    updated = models.DateTimeField(auto_now=True)

    # статус статьи
    # chises - ограничивает возможные значения из указанного списка
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # класс содержит метаданные
    class Meta:
        # способ сортировки по убыванию даты публикации "-publish"
        ordering = ('-publish',)

    # Метод __str__() возвращает отображение объекта, понятное человеку.
    # Django использует его во многих случаях, например на сайте администрирования
    def __str__(self):
        return self.title
