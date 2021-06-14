from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


# класс реализующий своего менеджера модулей
# он возвращает все опубликованные посты
class PublishedManager(models.Manager):
    # Метод менеджера get_queryset() возвращает QuerySet, который будет вы-полняться.
    # Мы переопределили его и добавили фильтр над результирующим QuerySet’ом
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Post(models.Model):
    # Менеджер по умолчанию
    objects = models.Manager()

    # Наш новый менеджер
    published = PublishedManager()

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

    # метод возвращает канонический URL объекта
    # для реализции поведения используем фyнкцию reverse(), которая дает возможность получать URL, указав имя шаблона и параметы
    # мы будем использовать метод get_absolute_url() в HTML-шаблонах, чтобы получать ссылку на статью
    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.publish.year, self.publish.month, self.publish.day, self.slug]
        )

class Comment(models.Model):
    # Атрибут related_name позволяет получить доступ к комментариям конкретной статьи.
    # Теперь мы сможем обращаться к статье из комментария, используя запись comment.post,
    # и к комментариям статьи при помощи post.comments.all()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Мы добавили булевое поле active, для того чтобы была возможность скрыть некоторые комментарии
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)
