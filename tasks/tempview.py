from django.utils.timezone import now
from datetime import datetime, timedelta
import calendar

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the current month and year from query parameters or use today's date
    current_month = int(request.GET.get('month', now().month))
    current_year = int(request.GET.get('year', now().year))

    # Get the first day of the current month and calculate next/previous months
    first_day_of_month = datetime(current_year, current_month, 1)
    _, last_day = calendar.monthrange(current_year, current_month)

    # Calculate the previous and next months
    previous_month = current_month - 1 if current_month > 1 else 12
    previous_year = current_year if current_month > 1 else current_year - 1
    next_month = current_month + 1 if current_month < 12 else 1
    next_year = current_year if current_month < 12 else current_year + 1

    # Get tasks for the user
    tasks = Task.objects.filter(user=request.user)

    # Calculate padding days for the first week
    first_weekday = first_day_of_month.weekday()  # Monday = 0, Sunday = 6
    days_in_month = []

    # Padding for the empty days before the first day
    for _ in range(first_weekday):
        days_in_month.append({'day': None, 'tasks': []})

    # Add actual days with tasks
    for day in range(1, last_day + 1):
        date = datetime(current_year, current_month, day)
        day_tasks = tasks.filter(due_date=date)

        # Convert day_tasks queryset to a list of dictionaries
        task_list = []
        for task in day_tasks:
            task_list.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'is_completed': task.is_completed,
            })

        days_in_month.append({
            'day': day,
            'tasks': task_list
        })

    context = {
        'tasks': tasks,
        'days_in_month': days_in_month,
        'current_month': first_day_of_month.strftime('%B'),
        'current_year': current_year,
        'previous_month': previous_month,
        'previous_year': previous_year,
        'next_month': next_month,
        'next_year': next_year,
    }

    return render(request, 'dashboard.html', context)
