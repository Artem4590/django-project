from django.core.checks import messages
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.timezone import activate
from django.views.generic import ListView
from django.core.mail import send_mail
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm

class PostListView(ListView):
    # Использовать переопределенный QuerySet модели вместо получения всех объектов.
    # Вместо задания атрибута QuerySet мы могли бы указать модель model=Post, и тогда Django,
    # используя стандартный менеджер мо-дели, получал бы объекты как Post.objects.all()
    queryset = Post.published.all()

    # Использовать posts в качестве переменной контекста HTML-шаблона, в которой будет храниться список объектов.
    # Если не указать атрибут context_object_name, по умолчанию используется переменная object_list
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

    # Список активных комментариев для этой статьи
    # Мы создали объект QuerySet, используя объект статьи post и менеджер связанных объектов comments,
    #   определенный в модели Comment в аргументе related_name
    comments = post.comments.filter(active=True)
    new_comment = None
    comment_form = None
    if request.method == 'POST':
        # Пользователь оставил комментарий
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создаем комментарий, но пока не сохраняем в базе данных
            # Метод save() создает объект модели, с которой связана форма, и сохраняет его в базу данных.
            # Если в качестве аргумента метода передать commit=False, то объект будет создан, но не будет сохранен в базу данных.
            # Это может быть полезным, когда перед сохранением объекта вам нужно каким-либо образом его изменить
            new_comment = comment_form.save(commit=False)

            # Привязываем комментарий к текущей статье
            # Благодаря этому мы связываем созданный комментарий с текущей статьей
            new_comment.post = post

            # Сохраняем комментарий в базе данных
            new_comment.save()
        else:
            comment_form = CommentForm()

    return render(request, 'blog/post/detail.html',{
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
    })

# Определяем функцию post_share, которая принимает объект запроса request и параметр post_id
def post_share(request, post_id):
    # Вызываем функцию get_object_or_404() для получения опубликованной статьи с указанным идентификатором
    post = get_object_or_404(Post, id=post_id, status='published')

    sent = False

    # Пользователь заполняет форму и отправляет POST-запросом.
    # Мы создаем объект формы, используя полученные из request.POST данные
    if request.method == 'POST':
        # Форма была отправлена на сохранение
        form = EmailPostForm(request.POST)

        # После этого выполняется проверка введенных данных с помощью метода формы is_valid().
        # Он валидирует все описанные поля формы и возвращает True, если ошибок не найдено.
        # Если хотя бы одно поле содержит неверное значение, возвращается False. Список полей с ошибками можно посмотреть в form.errors
        if form.is_valid():
            # Если форма валидна, мы получаем введенные данные с помощью form.cleaned_data.
            # Этот атрибут является словарем с полями формы и их значениями
            cd = form.cleaned_data

            # Подготовка шаблона для отправки почты 
            # Каждый параметр может быть индивидуальным
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])

            sent = True

            # Отправка электронной почты
            send_mail(subject, message, 'lavryha4590@gmail.com', [cd['to']])

            #Если форма не проходит валидацию, то в атрибут cleaned_data попадут только корректные поля
    else:
        # Когда обработчик выполняется первый раз с GET-запросом, мы создаем объект form, который будет отображен в шаблоне как пустая форма
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
