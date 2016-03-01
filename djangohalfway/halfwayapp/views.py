from django.shortcuts import render, redirect
#import googlemaps
import csv
import time
import json
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms
from . import models



class EnterIDForm(forms.Form):
    meeting_id = forms.CharField()
    def validate_trip_id(self):
        cleaned_id = self.cleaned_data
        if models.Meeting.objects.filter(trip_id = cleaned_id['meeting_id']):
            return cleaned_id['meeting_id']
        else:
            return None
            # raise forms.ValidationError("Please enter a valid Meeting Trip ID number.")



class AddAddress(forms.ModelForm):
    class Meta:
        model = models.Address
        fields = ["street", "city", "state", "zip_code"]



class AddParticipant(forms.ModelForm):
    class Meta:
        model = models.Participant
        fields = ["transit_mode"]
        widgets = {
            'transit_mode': forms.Select(),
        }


class AddMeeting(forms.ModelForm):
    class Meta:
        model = models.Meeting
        fields = ["business_type"]
        widgets = {
            'business_type': forms.Select(),
        }

def home(request):
    if request.method == 'POST':
        if "PersonA_submit" in request.POST:
            address = AddAddress(request.POST)
            participant = AddParticipant(request.POST)
            meeting = AddMeeting(request.POST)
            if address.is_valid() and participant.is_valid() and meeting.is_valid():
                c = personA(request, address, participant, meeting)
                return render(request,'halfwayapp/response.html',c)
        elif 'Enter_trip_id' in request.POST:
            trip_id = EnterIDForm(request.POST)
            if trip_id.is_valid():
                valid_trip_id = trip_id.validate_trip_id()
                if valid_trip_id:
                    return redirect('test:participant_two', valid_trip_id)
                else:
                    return HttpResponse("Invalid trip id")

    address = AddAddress()
    participant = AddParticipant()
    meeting = AddMeeting()
    trip_id = EnterIDForm()

    c = {
        'forms': [address, participant, meeting],
        'trip_id_form': trip_id
    }

    return render(request, 'halfwayapp/home.html', c)


def personA(request, address, participant, meeting):
    address_obj = address.save()
    part_obj = participant.save()
    part_obj.starting_location = address_obj
    part_obj.save()
    meeting_obj = meeting.save()
    meeting_obj.participant_one = part_obj
    meeting_obj.trip_id = meeting_obj.random_words()
    meeting_obj.save()

    c =  {
        'uniq': meeting_obj.trip_id
    }

    return c

def participant_two(request, meeting_id):
    if request.method == 'POST':
        address = AddAddress(request.POST)
        participant = AddParticipant(request.POST)
        if address.is_valid() and participant.is_valid():
            address_obj = address.save()
            part_obj = participant.save()
            part_obj.starting_location = address_obj
            part_obj.save()
            meeting = models.Meeting.objects.get(trip_id = meeting_id)
            meeting.participant_two = part_obj
            meeting.save()
            #call midway function with meeting attributes
            return redirect('test:results', meeting.trip_id)
    address = AddAddress()
    participant = AddParticipant()

    c = {
        'forms': [address, participant],
        'uniq': meeting_id
    }

    return render(request, "halfwayapp/person2.html", c)

    # enter_id = trip_id.validate_trip_id()
    # if enter_id:
    #     return HttpResponse("The trip is in the database")
    # else:
    #     return HttpResponse("Invalid trip id")
    #
    # c = {
    #     'forms': [GetMeetingID]
    # }
def results(request, meeting_id):
    return HttpResponse("Results page")
