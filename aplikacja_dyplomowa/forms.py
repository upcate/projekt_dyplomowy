from django import forms
from django.forms import ModelForm, CharField, Form
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, ValidationError
from django.contrib.auth import password_validation
from .models import Projects, Tags, ProjectObjects
# from django_select2 import forms as s2forms


class CreateUserForm(UserCreationForm):

    password1 = forms.CharField(
        label='Hasło',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label='Potwierdź hasło',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='Enter the same password as before, for verification.',
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nazwa użytkownika',
            'email': 'Email',
        }

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise ValidationError('Użytkownik o tej samej nazwie już istnieje.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise ValidationError('Ten mail jest już w użyciu.')
        return email


class ProjectForm(ModelForm):
    class Meta:
        model = Projects
        fields = ['project_name']
        labels = {
            'project_name': 'Nazwa projektu'
        }


class TagForm(ModelForm):
    class Meta:
        model = Tags
        fields = ['tag_name']
        labels = {
            'tag_name': 'Nazwa tagu'
        }


class ProjectObjectForm(ModelForm):

    class Meta:
        model = ProjectObjects
        fields = ['object_name', 'object_description']
        labels = {
            'object_name': 'Nazwa obiektu',
            'object_description': 'Opis obiektu',
            'tags': 'Tagi'
        }
        widgets = {
            'object_description': forms.Textarea(attrs={'rows': 3, 'cols': 20}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['object_description'].required = False


class ProjectObjectAddTagForm(Form):

    def __init__(self, *args, project=None, object_to_view=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tags.objects.filter(project=project)
        self.fields['tags'].initial = object_to_view.tags.all()

    tags = forms.ModelMultipleChoiceField(queryset=Tags.objects.none(), widget=forms.CheckboxSelectMultiple, required=False)

# class Meta:
    #     model = ProjectObjects
    #     fields = ['tags']
    #     labels = {
    #         'tags': 'Tagi',
    #     }
