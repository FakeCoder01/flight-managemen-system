from django.shortcuts import render


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from core.models import Flight, Airport
from .serializers import SearchFlightSerializer
# Create your views here.

"""
{
    flights_found,
    flights : [
        {

            flight_number,

            origin_airport = {
                'airport_name',
                'airport_city',
                'airport_country',
                'iata_code',
                'icao_code',
                'airport_type'
            },

            destination_airport = {
                'airport_name',
                'airport_city',
                'airport_country',
                'iata_code',
                'icao_code',
                'airport_type'
            },

            departure_date,
            departure_time,
            arrival_date,
            arrival_time,
            available_tickets,
            flight_price,
            seat_class,

        },
    ]

}

"""

@api_view(['GET'])
def ApiOverview(request):
    api_urls = {
        'search_airports': '/api/search/airports/',
        'search_flights': '/api/search/flights/',
    }
    return Response(api_urls)



@api_view(['GET'])
def SearchFlight(request):

    search_params = SearchFlightSerializer(data=request.GET or None)
    if search_params.is_valid():
        seat_class = request.GET['seat_class']
        origin = request.GET['origin']
        destination = request.GET['destination']
        departure_date = request.GET['departure_date']

        if not Airport.objects.filter(iata_code=origin.upper()).exists():
            return Response({"error":"origin not valid"})
        if not Airport.objects.filter(iata_code=destination.upper()).exists():
            return Response({"error":"destination not valid"})

        origin = Airport.objects.get(iata_code=origin.upper())
        destination = Airport.objects.get(iata_code=destination.upper())

        flights = [ x.search_flight_result(seat_class) for x in Flight.objects.filter(origin_airport=origin, destination_airport=destination, departure_date=departure_date) ]


        sort_key = ''
        if 'sort_key' in request.GET and request.GET['sort_key'] != '':
            sort_key = request.GET['sort_key']

        if sort_key == 'price':
            flights = sorted(flights, key=lambda k: k['flight_price'])

        elif sort_key == 'time':
            flights = sorted(flights, key=lambda k: k['flight_duration'])

        elif sort_key == 'stops':
            flights = flights
            
        else:
            flights = flights

        payload = {
            "status_code" : 200,
            "flights_found" : len(flights),
            "seat_class" : seat_class,
            "flights" : flights
        }
        return Response(payload)
    return Response({"error":"not valid"})

@api_view(['GET'])
def AirportFillUp(request):
    airports = Airport.objects.all().defer("created_at", "updated_at").values()
    if 'airport_search' in request.GET and request.GET['airport_search'] != '':
        airport_search = request.GET['airport_search']
        airports = Airport.objects.filter(
            Q(airport_name__icontains=airport_search) |
            Q(airport_city__icontains=airport_search) |
            Q(airport_country__icontains=airport_search) |
            Q(iata_code__icontains=airport_search) |
            Q(icao_code__icontains=airport_search) 
        ).defer("created_at", "updated_at").values()

    return Response({"airports":airports})    