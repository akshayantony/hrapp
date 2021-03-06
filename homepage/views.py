from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic, View
from django.contrib import messages

from .models import Candidate,Tokens,Jobs
from .forms import CandidateForm,StripeForm,JobForm,Revisitform

class CandidateFormView(View):
    """view for candidate form in homepage of app"""
    model = Candidate
    form_class=CandidateForm
    template_name='homepage/candidate.html'

    def get(self,request):
        form=self.form_class()
        return render(request,self.template_name,{'form':form})

    def post(self,request):
        print(self.request)
        form=self.form_class(request.POST)

        if(form.is_valid()):
            form.save()
            return render(request,'homepage/response.html')
        else:
            pass
        return render(request,self.template_name,{'form':form})

class ChargeView(generic.FormView):
    """view for making payments using stripes. token generated using javascript and charge
    function call done in clean()
    """
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
                messages.success(request, 'Success we have charged 50 cents. Thankyou')
                return render(request,'homepage/statusmsg.html', {'form': form})
            else:
                messages.success(request, 'Sorry! attempt failed.. try again later')
                return render(request, 'homepage/statusmsg.html', {'form': form})

        else:
            messages.success(request, 'Kindly enter your details in candidate details form first')
            return render(request,'homepage/statusmsg.html', {'form': form})

        return render(request, self.template_name, {'form': form})


class JobFormView(generic.FormView):
    """View for HR to send job updates to candidates. After updating details and clicking submit,
     Emails are sent to payed members
     """
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
            return redirect('homepage:candidate_form')
        else:
            return HttpResponse("invalid form")
        return render(request, self.template_name, {'form': form})

class Revisit(View):
    """View for accepting email of candidates who already attended company
    interviews in the past, and number of attempts of these candidates are incremented
    for each visit
    """
    def get(self, request):
        return redirect('homepage:candidate_form')

    def post(self, request):
        form = Revisitform(request.POST)
        email = request.POST['email_field']
        candidate = Candidate.objects.filter(email=email)

        if candidate.count() > 0:
            if (form.is_valid()):
                for cand in candidate:
                    n_attempts=cand.n_attempts+1
                    candidate.update(n_attempts=n_attempts)
        else:
            messages.info(request, 'Email not found. please fill in the candidate form X')
            return redirect('homepage:candidate_form')
        return render(request, 'homepage/response.html')