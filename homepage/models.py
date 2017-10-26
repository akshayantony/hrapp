from __future__ import unicode_literals
from django.core.validators import RegexValidator
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from hr import settings

res_choices=(
        ('p','Pass'),
        ('f','fail'),
        ('w','waiting_list'),
    )

dept_choices = (
    ('An', 'Android'),
    ('Py', 'Python Django'),
    ('BA', 'Business Analyst'),
    ('HR', 'HR'),
)

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                             message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

@python_2_unicode_compatible
class Candidate(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    phone_number = models.CharField(validators=[phone_regex], max_length=15)
    college=models.CharField(max_length=100)
    department = models.CharField(max_length=100, choices=dept_choices,blank=True)
    member=models.BooleanField(default=False)
    experience=models.IntegerField()
    n_attempts=models.IntegerField(null=True)
    result=models.CharField(max_length=100,choices=res_choices,blank=True)

    def __str__(self):
        return self.name


class Sale(models.Model):
    def __init__(self, *args, **kwargs):
        super(Sale, self).__init__(*args, **kwargs)

        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        self.stripe = stripe

    charge_id = models.CharField(max_length=32)

    def charge(self, price_in_cents, number, exp_month, exp_year, cvc):

        if self.charge_id:
            return False, Exception(message="Already charged.")

        try:
            response = self.stripe.Charge.create(
                amount=1000,
                currency="usd",
                card={
                    "number": number,
                    "exp_month": exp_month,
                    "exp_year": exp_year,
                    "cvc": cvc,
                },
                description='Thank you for your purchase!')

            self.charge_id = response.id

        # except self.stripe.CardError, ce:
        #     return False, ce
        except self.stripe.CardError:
            return False, {'message': 'failed'}

        return True, response