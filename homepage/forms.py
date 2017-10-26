from django import forms
from .models import Candidate,Sale

class CandForm(forms.ModelForm):

    class Meta:
        model=Candidate
        fields='__all__'


class StripeForm(forms.Form):
    stripe_token = forms.CharField()



from datetime import date, datetime
from calendar import monthrange


# class CreditCardField(forms.IntegerField):
#     def clean(self, value):
#         """Check if given CC number is valid and one of the
#            card types we accept"""
#         if value and (len(value) & lt; 13 or len(value) & gt; 16):
#             raise forms.ValidationError("Please enter in a valid " + \
#                                         "credit card number.")
#         return super(CreditCardField, self).clean(value)


class CCExpWidget(forms.MultiWidget):

    def decompress(self, value):
        return [value.month, value.year] if value else [None, None]

    def format_output(self, rendered_widgets):
        html = u' / '.join(rendered_widgets)
        return u'<span style="white-space: nowrap;">%s</span>' % html


class CCExpField(forms.MultiValueField):
    EXP_MONTH = [(x, x) for x in range(1, 13)]
    EXP_YEAR = [(x, x) for x in range(date.today().year,
                                       date.today().year + 15)]
    default_error_messages = {
        'invalid_month': u'Enter a valid month.',
        'invalid_year': u'Enter a valid year.',
    }

    def __init__(self, *args, **kwargs):
        errors = self.default_error_messages.copy()
        if 'error_messages' in kwargs:
            errors.update(kwargs['error_messages'])
        fields = (
            forms.ChoiceField(choices=self.EXP_MONTH,
                              error_messages={'invalid': errors['invalid_month']}),
            forms.ChoiceField(choices=self.EXP_YEAR,
                              error_messages={'invalid': errors['invalid_year']}),
        )
        super(CCExpField, self).__init__(fields, *args, **kwargs)
        self.widget = CCExpWidget(widgets=
                                  [fields[0].widget, fields[1].widget])


    def compress(self, data_list):
        if data_list:
            if data_list[1] in forms.fields.EMPTY_VALUES:
                error = self.error_messages['invalid_year']
                raise forms.ValidationError(error)
            if data_list[0] in forms.fields.EMPTY_VALUES:
                error = self.error_messages['invalid_month']
                raise forms.ValidationError(error)
            year = int(data_list[1])
            month = int(data_list[0])
            # find last day of the month
            day = monthrange(year, month)[1]
            return date(year, month, day)
        return None


class SalePaymentForm(forms.Form):
    number = forms.IntegerField(required=True, label="Card Number", initial=4242424242424242)
    expiration = CCExpField(required=True, label="Expiration")
    cvc = forms.IntegerField(required=True, label="CCV Number",
                             max_value=9999, widget=forms.TextInput(attrs={'size': '4'}))

    def clean(self):
        """
        The clean method will effectively charge the card and create a new
        Sale instance. If it fails, it simply raises the error given from
        Stripe's library as a standard ValidationError for proper feedback.
        """
        cleaned = super(SalePaymentForm, self).clean()

        if not self.errors:

            number = self.cleaned_data["number"]
            exp_month = self.cleaned_data["expiration"].month
            exp_year = self.cleaned_data["expiration"].year
            cvc = self.cleaned_data["cvc"]
            import pdb
            pdb.set_trace()
            token = form['stripeToken']
            print(token)
            sale = Sale()

            success, instance = sale.charge(1000, number, exp_month, exp_year, cvc)

            if not success:
                raise forms.ValidationError("Error: %s" % instance.get('message'))
            else:
                instance.save()
                # we were successful! do whatever you will here...
                # perhaps you'd like to send an email...
                pass

        return cleaned