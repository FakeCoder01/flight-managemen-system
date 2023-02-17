from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import *
from requests import session
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect, render
from .serializers import FlightBookingSerializer
from django.contrib import messages


# Create your views here.

def search_flight(request):
    context = {
        "page_title" : "Search Flights | Luua",
        "airports" : Airport.objects.all()
    }
    return render(request, "booking/search-flights.html", context)


def login_user(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            # User is authenticated
            login(request, user)
            messages.success(request, "Login successful")
            if Profile.objects.filter(user=request.user, profile_active=True).exists():
                return redirect('/')
            return redirect(f'/profile?perform=new')
        messages.error(request, "Invalid credentials")        
        return redirect("/login?msg=invalid credentials")    
    return render(request, 'booking/authentication/login.html', {"page_title" : "Login to Luua"})


def signup_user(request):

    try:
        if request.method == 'POST':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']

            password = request.POST['password']
            confirm_password = request.POST['confirm_password']

            if confirm_password != password:
                messages.error(request, "Password did not match")
                return redirect("/signup?res=Password did not match")

            full_name = first_name+' '+last_name
            username = email

            # create a user account for the student
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                new_profile = Profile.objects.create(
                    user = user,
                    full_name = full_name
                )
                messages.success(request, 'Account has been created')
                return redirect(f'/profile?res=account created successfully&perform=new')

            messages.error(request, 'User not logged in')
            return redirect("/signup?res=User not activated")

        return render(request, "booking/authentication/sign-up.html", {"page_title" : "Sign up to Luua"})
    except Exception as err:
        ###
        print(err)
        messages.error(request, 'Account creation Failed')
        return redirect("/signup?res=Something went wrong")


@login_required(login_url="/login")
def manage_profile(request):
    profile_active = Profile.objects.get(user=request.user).profile_active
    try:
        if request.method == 'POST':

            gender = request.POST['gender']
            passport_number = request.POST['passport_number']
            citizenship = request.POST['citizenship']
            mobile_number = request.POST['mobile_number']

            # create/update a user profile for the user
            profile = request.user.userprofile
            profile.gender = gender
            profile.passport_number = passport_number.upper()
            profile.citizenship = citizenship
            profile.mobile_number = mobile_number
            

            if profile_active == True and 'full_name' in request.POST and request.POST['full_name'] != '':
                profile.full_name = request.POST['full_name']
            
            profile.profile_active = True
            profile.save()
     
            messages.success(request, 'Profile has been saved')
            return redirect(f'/profile?res=Profile saved successfully')
        context = {
            "page_title" : "Manage Profile | Luua",
            "profile_active" : profile_active,
            "tab_id" : "manage-profile"
        }
        return render(request, "booking/account/profile.html", context)
    except Exception as err:
        ###
        print(err)
        messages.error(request, 'Profile creation Failed')
        return redirect("/signup?res=Something went wrong")


def logout_user(request):
    logout(request)
    messages.success(request, 'Successfully logged out')
    return redirect('/')



def handle_seat_class_session(request):
    value = ""
    try :
        value = request.session.get('seat_class')
    except:
        value = ""    
    return value



@login_required(login_url="/login")
def flight_deatils(request, flight_id):
    if Flight.objects.filter(uid=flight_id).exists():
        flight = Flight.objects.get(uid=flight_id)
        try:
            del request.session['seat_class']
        except Exception as err:
            print(err)
        if request.method == 'POST' and 'seat_class' in request.POST and request.POST['seat_class'] != '':
            response = HttpResponseRedirect(f"/flight/{flight_id}/book/?seat_class={request.POST['seat_class']}")   
            request.session['seat_class'] = request.POST['seat_class']     
            return response
        context = {
            "page_title": flight.origin_airport.iata_code + ' to ' + flight.destination_airport.iata_code + ' (' + flight.flight_number +')', 
            "flight" : flight,
            "flight_info" : flight.get_flight_deatils()
        }
        
        return render(request, "booking/flights/flight-details.html", context)
    return Http404()



def get_flight_amount(request, flight):
    price = -1
    seat_catagory = handle_seat_class_session(request)
    if seat_catagory == 'economy_fare':
        price = Fare.objects.get(flight=flight).economy_fare
    elif seat_catagory == 'business_fare':
        price = Fare.objects.get(flight=flight).business_fare
    elif seat_catagory == 'first_fare':
        price = Fare.objects.get(flight=flight).first_fare
    else:  
        return price 

    return price    


@login_required(login_url="/login")
def fill_booking_details(request, flight_id):
    if Flight.objects.filter(uid=flight_id).exists():
        flight = Flight.objects.get(uid=flight_id)
        fare_amount = get_flight_amount(request, flight)
        if fare_amount == -1:
            return redirect('/')
        if request.method == 'POST':
            flight_booking = FlightBookingSerializer(data=request.POST or None)
            if flight_booking.is_valid():

                if 'flight_id' not in request.POST or 'seat_type' not in request.POST or 'fare_amount' not in request.POST:
                    return redirect(f"/flight/{flight_id}/?flight-params")

                if request.POST['flight_id'] != flight_id or float(request.POST['fare_amount']) != fare_amount:
                    return redirect(f"/flight/{flight_id}/?flight-params-2")

                if request.POST['seat_type'] == 'economy_fare':
                    seat_cat = "Economy"
                elif request.POST['seat_type'] == 'business_fare':
                    seat_cat = "Business"
                elif request.POST['seat_type'] == 'first_fare':
                    seat_cat =  "First"        
                else:
                    seat_cat =  "Error" 
                ## Book Flight
                new_flight_booking = Booking.objects.create(
                    flight = flight,
                    profile = request.user.userprofile,
                    person_name = request.POST['person_name'],
                    gender = request.POST['gender'],
                    passport_number = request.POST['passport_number'],
                    citizenship = request.POST['citizenship'],
                    mobile_number = request.POST['mobile_number'],
                    email = request.POST['email'],
                    seat_type = seat_cat,
                    fare_amount = fare_amount,
                    fare = Fare.objects.get(flight=flight),
                )
                try:
                    del request.session['seat_class']
                except:
                    pass    
                return redirect(f"/flight/{flight_id}/payment/{new_flight_booking.uid}/pay")
            return redirect('#?booked=False')
        context = {
            "page_title": flight.origin_airport.iata_code + ' to ' + flight.destination_airport.iata_code + ' (' + flight.flight_number +')', 
            "flight" : flight,
            "fare_amount" : fare_amount,
            "seat_class" : handle_seat_class_session(request)
        }
        return render(request, "booking/flights/book-flight.html", context)
    return Http404()



@login_required(login_url="/login")
def payments(request):
    context = {
        "payments" : Payment.objects.filter(profile=request.user.userprofile),
        "page_title" : "Payment History | Luua",
        "tab_id" : "payments",
    }
    return render(request, "booking/payment/all-payments.html", context)





@login_required(login_url="/login")
def invoice_payment(request, payment_id):
    if Payment.objects.filter(payment_id=payment_id, profile=request.user.userprofile).exists():
        payment = Payment.objects.get(payment_id=payment_id, profile=request.user.userprofile)
        context = {
            "payment" : payment,
            "page_title" : "Payment Detail | Luua",
            "tab_id" : "payments"
        }
        return render(request, "booking/payment/payment-details.html", context)
    return Http404()














@login_required(login_url="/login")
def book_flight(request, flight_id, booking_id):
    if Flight.objects.filter(uid=flight_id).exists() and Booking.objects.filter(uid=booking_id, flight=Flight.objects.get(uid=flight_id), profile=request.user.userprofile).exists():
        booking = Booking.objects.get(uid=booking_id)
        flight = Flight.objects.get(uid=flight_id)    
        context = {
            "page_title": 'Payment | ' + flight.origin_airport.iata_code + ' to ' + flight.destination_airport.iata_code + ' (' + flight.flight_number +')', 
            "flight" : flight,
            "booking" : booking
        }
        return render(request, "booking/flights/payment.html", context)
    return Http404()














































@login_required(login_url="/login")
def bookings(request):
    context = {
        "page_title" : "Flight Tickets| Luua",
        "tab_id" : "tickets",
        "bookings" : Booking.objects.filter(profile=request.user.userprofile)
    }
    return render(request, "booking/tickets/bookings.html", context)


@login_required(login_url="/login")
def booking_details(request, booking_id):
    if Booking.objects.filter(uid=booking_id, profile=request.user.userprofile).exists():
        booking = Booking.objects.get(uid=booking_id, profile=request.user.userprofile)
        context = {
            "booking" : booking,
            "page_title" : "Ticket Detail | Luua",
            "tab_id" : "tickets"
        }
        return render(request, "booking/tickets/booking-details.html", context)
    return Http404()

@login_required(login_url="/login")
def cancel_flight(request, booking_id):
    return


@login_required(login_url="/login")
def edit_booking(request, booking_id):
    return


@login_required(login_url="/login")
def privacy_security(request):
    context = {
        "page_title" : "Privacy & Security | Luua",
        "tab_id" : "privacy-security"
    }
    return render(request, "booking/account/privacy-security.html", context)


def homepage(request):
    return render(request, "booking/home-page.html")


