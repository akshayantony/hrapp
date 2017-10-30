from django import forms
from .models import Candidate,Tokens,Jobs
from django.core.exceptions import ValidationError
from datetime import date

class CandForm(forms.ModelForm):

    class Meta:
        model=Candidate
        fields=['name', 'email', 'phone_number', 'college','department','experience','n_attempts','result']


class StripeForm(forms.Form):
    email = forms.EmailField(required=True)
    number = forms.IntegerField(required=True, label="Card Number", initial=4242424242424242)
    exp_month = forms.IntegerField(initial=12)
    exp_year = forms.IntegerField(initial=2019,required=True)
    cvc = forms.IntegerField(required=True, label="CCV Number", max_value=9999, widget=forms.TextInput(attrs={'size': '4'}))
    stripe_token = forms.CharField()

    def clean(self):
        cleaned = super(StripeForm, self).clean()
        exp_month = self.cleaned_data["exp_month"]
        if exp_month not in range(1, 13):
            raise ValidationError("enter a valid date")
        exp_year = self.cleaned_data["exp_year"]
        if exp_year not in range(date.today().year, date.today().year + 15):
            raise ValidationError("enter a valid date")

        if not self.errors:
            email = self.cleaned_data["email"]
            number = self.cleaned_data["number"]
            cvc = self.cleaned_data["cvc"]
            token = self.cleaned_data["stripe_token"]
            tokenobj = Tokens()

            success, instance = tokenobj.charge(1000, number, exp_month, exp_year, cvc, token)

            if not success:
                raise forms.ValidationError("Error: %s" % instance.get('message'))
            else:
                instance.save()
                pass

        return cleaned

class JobForm(forms.ModelForm):
    class Meta:
        model=Jobs
        fields='__all__'

class Revisitform(forms.Form):
    email_field=forms.CharField(max_length=150)

    class Meta:
        fields=['email_field',]


