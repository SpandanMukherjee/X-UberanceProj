from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, TaskForm, HabitForm
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from .models import Task, Habit, HabitLog, FocusSession
from django.shortcuts import get_object_or_404
from datetime import date, timedelta, datetime, time
from .utils import enforce_focus_lock

@enforce_focus_lock
def home_redirect(request):

    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return redirect('login')

@enforce_focus_lock
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

@enforce_focus_lock
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
    session = FocusSession.objects.filter(user=request.user, end_time__isnull=True).first()

    if session:
        session.end_session()
        session.task_completed = False
        session.save()

    logout(request)
    return redirect('login')

@enforce_focus_lock
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

@enforce_focus_lock
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

@login_required
def focus_view(request):
    user = request.user
    current_session = FocusSession.objects.filter(user=user, end_time__isnull=True).first()

    if request.method == 'POST' and not current_session:
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, id=task_id, user=user, is_done=False)
        current_session = FocusSession.objects.create(user=user, task=task)
        return redirect('focus')

    if request.method == 'POST' and 'end_session' in request.POST and current_session:
        current_session.end_session()
        return redirect('confirm_focus_completion')

    tasks = Task.objects.filter(user=user, is_done=False)
    return render(request, 'focus.html', {'current_session': current_session, 'tasks': tasks})


@login_required
def confirm_focus_completion(request):
    user = request.user
    session = FocusSession.objects.filter(user=user, end_time__isnull=False, task_completed=False).last()

    if not session:
        return redirect('focus')

    if request.method == 'POST':
        decision = request.POST.get('completed')
        if decision == 'yes':
            session.task_completed = True
            session.save()

            if session.task:
                session.task.is_done = True
                session.task.save()

                if session.task.from_habit:
                    HabitLog.objects.filter(
                        habit=session.task.from_habit,
                        date=session.task.due_date.date()
                    ).update(completed=True)

        return redirect('todos')

    return render(request, 'confirm_completion.html', {'session': session})
