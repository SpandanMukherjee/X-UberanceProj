from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, TaskForm, HabitForm
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from .models import Task, Habit, HabitLog
from django.shortcuts import get_object_or_404
from datetime import date, timedelta, datetime, time

def home_redirect(request):
    return redirect('login')

@login_required
def dashboard(request):
    today = date.today()
    user = request.user
    habits = Habit.objects.filter(user=user)

    for habit in habits:
        should_create = False

        if habit.frequency == 'daily':
            should_create = not HabitLog.objects.filter(habit=habit, date=today).exists()
        elif habit.frequency == 'weekly':
            start_of_week = today - timedelta(days=6)
            should_create = not HabitLog.objects.filter(habit=habit, date__range=(start_of_week, today)).exists()

        if should_create:
            HabitLog.objects.create(habit=habit, date=today, completed=False)
            has_task = Task.objects.filter(user=user, from_habit=habit, due_date__date=today, is_done=False).exists()

            if not has_task:

                if habit.frequency == 'daily':
                    due_day = today
                elif habit.frequency == 'weekly':
                    days_ahead = 6 - today.weekday()
                    due_day = today + timedelta(days=days_ahead)

                due_datetime = datetime.combine(due_day, time(hour=23, minute=59, second=59))
                Task.objects.create(user=user, title=f"{habit.name} (Habit)", due_date=due_datetime, from_habit=habit)

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

        if task.from_habit:
            HabitLog.objects.filter(habit=task.from_habit, date=task.due_date.date()).update(completed=True)
    
    return redirect('todos')

@login_required
def habits_view(request):

    if request.method == 'POST':
        form = HabitForm(request.POST)

        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            return redirect('dashboard')
    else:
        form = HabitForm()

    habits = Habit.objects.filter(user=request.user)
    return render(request, 'habits.html', {'form': form, 'habits': habits})