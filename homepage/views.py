from __future__ import unicode_literals

from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.views import generic, View
from django.conf import settings

from .models import Candidate,Tokens,Jobs
from .forms import CandForm,StripeForm,JobForm,Revisitform

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
        else:
            pass
        if(form.is_valid()):
            form.save()
            return render(request,'homepage/response.html')
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

class Revisit(View):

    def post(self, request):
        form = Revisitform(request.POST)
        email = request.POST['email_field']
        queryset = Candidate.objects.filter(email=email)
        if queryset.count() > 0:
            if (form.is_valid()):
                for r in queryset:
                    n_attempts=r.n_attempts+1
                    queryset.update(n_attempts=n_attempts)
        else:
            return HttpResponse("Kindly register")
        return render(request, 'homepage/response.html')

    def get(self, request):
        form = Revisitform()
        return redirect('homepage:cform')