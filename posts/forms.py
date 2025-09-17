from django import forms
from posts.models import Post


class PostForm(forms.ModelForm):
    text = forms.CharField(
        label='Post Text',
        widget=forms.Textarea(attrs={
            'placeholder': 'What’s on your mind?',
            'rows': 3,
            'class': 'form-control'
        }),
    )
    tags = forms.CharField(
        required=False,
        label='Tags',
        help_text='Enter tags separated by commas: travel, summer, beach',
        widget=forms.TextInput(attrs={
            'placeholder': 'travel, summer',
            'class': 'form-control'
        }),
    )

    class Meta:
        model = Post
        fields = ('text', 'tags')


class AddTagsForm(forms.Form):
    tags = forms.CharField(
        required=True,
        label='Add Tags',
        widget=forms.TextInput(attrs={
            'placeholder': 'New tags, comma separated',
            'class': 'form-control'
        }),
    )
