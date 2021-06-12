from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView

class PostListView(ListView):
    # Использовать переопределенный QuerySet модели вместо получения всех объектов.
    # Вместо задания атрибута QuerySet мы могли бы указать модель model=Post, и тогда Django,
    # используя стандартный менеджер мо-дели, получал бы объекты как Post.objects.all()
    queryset = Post.published.all()

    # Использовать posts в качестве переменной контекста HTML-шаблона, в которой будет храниться список объектов.
    # Если не указать атрибут con-text_object_name, по умолчанию используется переменная object_list
    context_object_name = 'posts'

    # Использовать постраничное отображение по три объекта на странице
    paginate_by = 3

    # Использовать указанный шаблон для формирования страницы.
    # Если бы мы не указали template_name, то базовый класс ListView использовал бы шаблон blog/post_list.html
    template_name = 'blog/post/list.html'

# обработчик для списка постов
def post_list(request):
    # с помощью менеджера модели, получаем все опубликованные посты
    # posts = Post.published.all()

    object_list = Post.published.all()

    # Постраничное отображение работает следующим образом:

    # 1) мы инициализируем объект класса Paginator, указав количество объектов на одной странице
    # по 3 статьи на каждой станице
    paginator = Paginator(object_list, 3)

    # 2) извлекаем из запроса GET-параметр page, который указывает текущую страницу;
    page = request.GET.get('page')
    try:
        # 3) получаем список объектов на нужной странице с помощью метода page()класса Paginator
        posts = paginator.page(page)
    except PageNotAnInteger:
        # 4.1) если указанный параметр page не является целым числом, обращаемся к первой странице.
        posts = paginator.page(1)
    except EmptyPage:
        # 4.2) если page больше, чем общее количество страниц, то возвращаем последнюю
        posts = paginator.page(paginator.num_pages)

    # 5) передаем номер страницы и полученные объекты в шаблон через render(... {'page': page, ...})

    # Используем функцию render() для формирования шабло-на со списком статей
    # Она принимает объект запроса request, путь к шаблону и переменные контекста для этого шаблона
    # В ответ вернется объект HttpRe-sponse со сформированным текстом
    # Функция render()использует переданный контекст при формировании шаблона, поэтому любая переменная контекста будет доступна в шаблоне
    # Процессоры контекста – это вызываемые функции, которые добавляют в контекст переменные
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})

# обработчик страницы поста
# Он принимает на вход аргументы year, month, day и post для получения статьи по указанным слагу и дате
def post_detail(request, year, month, day, post):

    # функция возвращает объект, который подходит по указанным параметрам, или вызывает исключение HTTP 404
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)

    return render(request, 'blog/post/detail.html', {'post': post})
