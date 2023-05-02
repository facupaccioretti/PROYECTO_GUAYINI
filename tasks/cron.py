from django_crontab import crontab

@crontab.minute
def test_cron_job():
    print("Django Crontab funciona!")
