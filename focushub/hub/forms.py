from django import forms
from django.contrib.auth.models import User
from .models import Task, Habit

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

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
        task.is_done = False  # Habits are not marked as done
        if commit:
            task.save()
        return task