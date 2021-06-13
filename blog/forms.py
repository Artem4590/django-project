from django import forms

# создали класс формы, унаследованный от Form
class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()

    # required=False - поле является необязательным
    comments = forms.CharField(required=False, widget=forms.Textarea)
