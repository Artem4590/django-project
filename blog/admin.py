# регистрация моделей для отображения в админке
from django.contrib import admin
from .models import Post, Comment


# admin.site.register(Post)

# Декоратор @admin.register() выполняет те же действия, что и функция admin.site.register(): регистрирует декорируе-мый класс – наследник ModelAdmin
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # настройка отображения модели

    # озволяет перечислить поля модели, которые мы хотим отображать на странице списка
    list_display = ('title', 'slug', 'author', 'publish', 'status')

    # Справа на странице появился блок фильтрации  списка,  который  фильтрует  статьи  по  полям,  перечисленным в list_filter
    list_filter = ('status', 'created', 'publish', 'author')

    # Также появилась строка поиска. Она добавляется для моделей, для которых определен атрибут search_fields
    search_fields = ('title', 'body')

    # slug генерируется авто-матически из поля title с помощью атрибута prepopulated_fields
    prepopulated_fields = {'slug': ('title',)}

    # Также теперь поле author содержит поле поиска, что значительно упрощает выбор автора из выпадающего списка, когда в системе сотни пользователей
    raw_id_fields = ('author',)

    # Под поиском благодаря атрибу-ту date_hierarchy добавлены ссылки для навигации по датам
    date_hierarchy = 'publish'

    # По умолчанию статьи  отсортированы по полям status и publish. Эта настройка задается в атри-буте ordering
    ordering = ('status', 'publish')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
