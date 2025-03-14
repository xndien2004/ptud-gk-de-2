from django.utils import timezone
from .models import Task

def overdue_tasks_count(request):
    if request.user.is_authenticated:
        count = Task.objects.filter(
            user=request.user,
            deadline__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        return {'overdue_tasks_count': count}
    return {'overdue_tasks_count': 0} 