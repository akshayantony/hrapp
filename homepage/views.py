from __future__ import unicode_literals

from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.views import generic, View
# from hr import settings
from django.conf import settings
from .models import Candidate,Sale
from .forms import CandForm,SalePaymentForm,StripeForm

import stripe

class CandidateFormView(View):
    model = Candidate
    form_class=CandForm
    template_name='homepage/candidate.html'


    def get(self,request):
        form=self.form_class()
        if not self.request.user.is_staff:
            form.fields.pop('result')
            form.fields.pop('n_attempts')
        return render(request,self.template_name,{'form':form})

    def post(self,request):
        print(self.request)
        form=self.form_class(request.POST)
        if not self.request.user.is_staff:
            form.fields.pop('result')
            form.fields.pop('n_attempts')
        else:
            pass
        if(form.is_valid()):
            form.save()
            return redirect('homepage:cform')
        else:
            pass
        return render(request,self.template_name,{'form':form})


class StripeMixin(object):
    def get_context_data(self, **kwargs):
        context = super(StripeMixin, self).get_context_data(**kwargs)
        context['publishable_key'] = settings.STRIPE_PUBLIC_KEY
        return context

class ChargeView(StripeMixin, generic.FormView):
    template_name = 'homepage/charge1.html'
    form_class = StripeForm

    def form_valid(self, form):
        import pdb
        pdb.set_trace()
        stripe.api_key = settings.STRIPE_SECRET_KEY

        customer_data = {
            'description': 'Some Customer Data',
            'card': form.cleaned_data['stripe_token']
        }
        return super(ChargeView, self).form_valid(form)


def charge(request):
    if request.method == "POST":
        import pdb
        pdb.set_trace()
        print(request.POST)
        form = SalePaymentForm(request.POST)

        if form.is_valid():
            token = request.form['stripeToken']
            print(token)
            return HttpResponse("Success! We've charged your card!")
    else:
        form = SalePaymentForm()

    return render(request, 'homepage/charge1.html', {'form': form})
    # return render_to_response('homepage/charge.html', RequestContext(request, {'form': form}))

