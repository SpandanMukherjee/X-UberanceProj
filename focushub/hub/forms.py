from django import forms
from django.contrib.auth.models import User
from .models import Task, Habit
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'username', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'password', 'placeholder': 'Password'})

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'password', 'placeholder': 'Password'
    }), required=True)
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'confirm_password', 'placeholder': 'Confirm Password'
    }), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'username', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'email', 'placeholder': 'Email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user

class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['title', 'due_date']
        widgets = {'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})}

class HabitForm(forms.ModelForm):

    class Meta:
        model = Habit
        fields = ['name', 'frequency']
        widgets = {'frequency': forms.Select(choices=Habit._meta.get_field('frequency').choices)}

    def save(self, commit=True):
        task = super().save(commit=False)
        task.is_done = False

        if commit:
            task.save()
        return task