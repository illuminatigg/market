import datetime

from accounts.models import CustomUser
from market.models import Schedule


def check_client_is_active(request):
    try:
        client = CustomUser.objects.get(username=request.data.get('telegram_id'), is_active=True)
        return client
    except Exception as ex:
        print(ex)


def work_time(time):
    schedule = Schedule.objects.first()
    start = schedule.start_time
    end = schedule.end_time
    if start <= time <= end:
        return True
    else:
        return False
