from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, TaskForm
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from .models import Task
from django.shortcuts import get_object_or_404

def home_redirect(request):
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def signup_view(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def todos_view(request):

    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('todos')
    else:
        form = TaskForm()

    tasks = Task.objects.filter(user=request.user, is_done=False).order_by('due_date')
    completed_tasks = Task.objects.filter(user=request.user, is_done=True).order_by('-due_date')
    return render(request, 'todos.html', {'form': form, 'tasks': tasks, 'completed_tasks': completed_tasks})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == 'POST':
        task.is_done = True
        task.save()
        return redirect('todos')
    
    return redirect('todos')