from .models import TestCronjob

def test_cron_job():
    TestCronjob.objects.create(name='test')

