from django import forms
from django.forms import ModelForm, CharField, Form
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, ValidationError, PasswordChangeForm
from django.contrib.auth import password_validation
from .models import Projects, Tags, ProjectObjects


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


class UpdateUserForm(forms.ModelForm):

    user = None

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Nazwa użytkownika',
            'email': 'Email',
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exclude(id=self.user.id).exists():
            raise ValidationError('Użytkownik o tej samej nazwie już istnieje.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exclude(id=self.user.id).exists():
            raise ValidationError('Ten mail jest już w użyciu.')
        return email


class CustomPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['old_password'].label = 'Obecne hasło'
        self.fields['new_password1'].label = 'Nowe hasło'
        self.fields['new_password2'].label = 'Potwierdź nowe hasło'

    error_messages = {
        'password_mismatch': 'Nowe hasła nie zgadzają się.',
        'password_incorrect': 'Twoje stare hasło zostało źle wprowadzone.',
    }




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


class ProjectObjectAddConnectionForm(Form):

    def __init__(self, *args, project=None, object_to_view=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['connections'].queryset = ProjectObjects.objects.filter(project=project).exclude(id=object_to_view.id)
        self.fields['connections'].initial = object_to_view.connections.all()

    connections = forms.ModelMultipleChoiceField(queryset=ProjectObjects.objects.none(), widget=forms.CheckboxSelectMultiple, required=False)
