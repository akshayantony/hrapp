from __future__ import unicode_literals

from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.views import generic, View
# from hr import settings
from django.conf import settings
from .models import Candidate,Tokens,Jobs
from .forms import CandForm,StripeForm,JobForm

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
    template_name = 'homepage/charge.html'
    form_class = StripeForm
    model = Tokens

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})


    def post(self, request):
        form = self.form_class(request.POST)

        email = request.POST['email']
        queryset = Candidate.objects.filter(email=email)
        if queryset.count()>0:
            if (form.is_valid()):
                queryset.update(member='True')
                return HttpResponse("Success! We've charged your card!")
            else:
                return HttpResponse("Sorry! attempt failed.. try again later")
        else:
            return HttpResponse("Kindly enter your details in candidate details form first")
        return render(request, self.template_name, {'form': form})


class JobFormView(generic.FormView):
    template_name = 'homepage/jobupdates.html'
    form_class = JobForm
    model=Jobs


    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})


    def post(self, request):
        form = self.form_class(request.POST)

        if (form.is_valid()):
            form.save()
            return redirect('homepage:cform')
        else:
            return HttpResponse("invalid form")

        return render(request, self.template_name, {'form': form})










# def charge(request):
#     if request.method == "POST":
#         import pdb
#         pdb.set_trace()
#         print(request.POST)
#         form = SalePaymentForm(request.POST)
#
#         if form.is_valid():
#             token = request.form['stripeToken']
#             print(token)
#             return HttpResponse("Success! We've charged your card!")
#     else:
#         form = SalePaymentForm()
#
#     return render(request, 'homepage/charge1.html', {'form': form})
#     return render_to_response('homepage/charge.html', RequestContext(request, {'form': form}))
#
