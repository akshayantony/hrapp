from __future__ import unicode_literals
from django.core.validators import RegexValidator
from django.utils.encoding import python_2_unicode_compatible
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template import loader
from django.db import models

from hr import settings

RES_CHOICES=(
        ('p','Pass'),
        ('f','fail'),
        ('w','waiting_list'),
    )

DEPT_CHOICES = (
    ('Android', 'Android'),
    ('Python', 'Python Django'),
    ('Tester','Tester'),
    ('Business Analyst', 'Business Analyst'),
    ('HR', 'HR'),
)

EXP_CHOICES = (
    ('0', 'Freshers'),
    ('1', 'One'),
    ('2', 'Two'),
    ('3', 'Three'),
    ('3+','Three plus')
)

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                             message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

@python_2_unicode_compatible
class Candidate(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(primary_key=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=15)
    college=models.CharField(max_length=100)
    department = models.CharField(max_length=100, choices=DEPT_CHOICES,blank=True)
    member=models.BooleanField(default=False)
    experience=models.IntegerField()
    n_attempts=models.IntegerField(default=1, blank=True, null=True)
    result=models.CharField(max_length=100,choices=RES_CHOICES,blank=True)

    def __str__(self):
        return self.name


class Tokens(models.Model):
    charge_id = models.CharField(max_length=32,blank=True)

    def __init__(self, *args, **kwargs):
        super(Tokens, self).__init__(*args, **kwargs)

        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe = stripe

    def charge(self, price_in_cents, number, exp_month, exp_year, cvc, token):
        if self.charge_id:
            return False, Exception(message="Already charged.")

        try:
            response = self.stripe.Charge.create(
                amount=1000,
                currency="usd",
                source=token,
                description='Thank you for your purchase!')

            self.charge_id = response.id

        except self.stripe.CardError:
            return False, {'message': 'failed'}

        return True, response

class Jobs(models.Model):
    department = models.CharField(max_length=100, choices=DEPT_CHOICES)
    experience=models.CharField(max_length=100,choices=EXP_CHOICES)
    education=models.CharField(max_length=100,blank=True)

    def __str__(self):
        return self.department

@receiver(post_save, dispatch_uid="news_update", sender=Jobs)
def subscription_handler(instance,**kwargs):
    subscribers=Candidate.objects.filter(member=True)
    vacancy_temp=loader.get_template('homepage/vacancyinfo.html')
    context={ 'instance':instance }
    message=vacancy_temp.render(context)
    send_mail(
        'Job Opening in Sayone',
        message,
        'dailycirclenews@gmail.com',
        [sub.email for sub in subscribers ],
        fail_silently=False,
    )
    return HttpResponse("Entered Signal")

post_save.connect(subscription_handler, sender=Jobs, dispatch_uid="subscription_handler")

