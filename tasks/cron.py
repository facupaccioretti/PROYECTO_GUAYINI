from .models import Test

def test_cron_job():
    Test.objects.create(name='test')

