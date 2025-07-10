from django.shortcuts import redirect
from .models import FocusSession

def enforce_focus_lock(view_func):

    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            session = FocusSession.objects.filter(user=request.user, end_time__isnull=True).first()
            allowed_paths = ['/focus/', '/confirm_completion/', '/logout/']

            if session and request.path not in allowed_paths:
                return redirect('focus')

        return view_func(request, *args, **kwargs)
    
    return wrapper
