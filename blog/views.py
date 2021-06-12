from django.shortcuts import render, get_object_or_404
from .models import Post


# обработчик для списка постов
def post_list(request):
    # с помощью менеджера модели, получаем все опубликованные посты
    posts = Post.published.all()

    # Используем функцию render() для формирования шабло-на со списком статей
    # Она принимает объект запроса request, путь к шаблону и переменные контекста для этого шаблона
    # В ответ вернется объект HttpRe-sponse со сформированным текстом
    # Функция render()использует переданный контекст при формировании шаблона, поэтому любая переменная контекста будет доступна в шаблоне
    # Процессоры контекста – это вызываемые функции, которые добавляют в контекст переменные
    return render(request, 'blog/post/list.html', {'posts': posts})

# обработчик страницы поста
# Он принимает на вход аргументы year, month, day и post для получения статьи по указанным слагу и дате
def post_detail(request, year, month, day, post):
    
    # функция возвращает объект, который подходит по указанным параметрам, или вызывает исключение HTTP 404
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)

    return render(request, 'blog/post/detail.html', {'post': post})
