from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from users.models import Profile

User = get_user_model()


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'placeholder': "Your Username",
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': "Enter Password",
            'class': 'form-control',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'password')


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': "Your Email",
            'class': 'form-control',
        })
    )
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'placeholder': "Your Username",
            'class': 'form-control',
        })
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        help_text=UserCreationForm().fields['password1'].help_text,
        widget=forms.PasswordInput(attrs={
            'placeholder': "Enter Password",
            'class': 'form-control',
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        help_text=UserCreationForm().fields['password2'].help_text,
        widget=forms.PasswordInput(attrs={
            'placeholder': "Confirm Password",
            'class': 'form-control',
        })
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')


class UserInfoForm(UserChangeForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'readonly': True,
            'class': 'form-control',
        })
    )
    username = forms.CharField(
        label="Username",
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': "Your Username",
            'class': 'form-control',
        })
    )
    first_name = forms.CharField(
        label="First Name",
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': "Your First Name",
            'class': 'form-control',
        })
    )
    last_name = forms.CharField(
        label="Last Name",
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': "Your Last Name",
            'class': 'form-control',
        })
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(id=self.instance.id).filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


class UserProfileForm(forms.ModelForm):
    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': "Your description",
            'class': 'form-control',
        })
    )

    class Meta:
        model = Profile
        fields = ('description',)
