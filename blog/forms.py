from django import forms
from django.forms import fields
from .models import Comment

# создали класс формы, унаследованный от Form
class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()

    # required=False - поле является необязательным
    comments = forms.CharField(required=False, widget=forms.Textarea)

# Все, что нужно для создания формы из модели, – указать, какую модель использовать в опциях класса Meta.
# Django найдет нужную модель и автоматически построит форму.
# Каждое поле модели будет сопоставлено полю формы соответствующего типа.
# По умолчанию Django использует все поля модели.
# Но мы можем явно указать, какие использовать, а какие – нет.
# Для этого доста-точно определить списки fields или exclude соответственно.
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
