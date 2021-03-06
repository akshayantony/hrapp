from django import forms
from django.core.exceptions import ValidationError

from .models import Candidate,Tokens,Jobs

from datetime import date

class CandidateForm(forms.ModelForm):

    class Meta:
        model=Candidate
        fields='__all__'


class StripeForm(forms.Form):
    email = forms.EmailField(required=True)
    number = forms.IntegerField(required=True, label="Card Number")
    exp_month = forms.IntegerField(initial=12,required=True)
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
            token = self.cleaned_data["stripe_token"]
            tokenobj = Tokens()
            success, instance = tokenobj.charge(token)

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


