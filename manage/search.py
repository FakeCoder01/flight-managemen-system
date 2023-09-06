from django.shortcuts import render, redirect
from core.models import Flight, Profile, Airport, Payment, Booking
from django.db.models import Q 
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import logging

logger = logging.getLogger(__name__)


@login_required(login_url='/manage/login')    
@staff_member_required(login_url='/manage/login')
def global_search(request):
    try:
        if 'search_query' in request.GET and request.GET['search_query'] != '':
            query = request.GET['search_query'] 

            flights = Flight.objects.filter(
                Q(uid__icontains=query)  |
                Q(flight_number__icontains=query)  |

                Q(origin_airport__airport_name__icontains=query)  |
                Q(origin_airport__airport_city__icontains=query) |
                Q(origin_airport__airport_country__icontains=query) |
                Q(origin_airport__iata_code__icontains=query) |
                Q(origin_airport__icao_code__icontains=query) |
                Q(origin_airport__airport_type__icontains=query) |
                
                Q(destination_airport__airport_name__icontains=query)  |
                Q(destination_airport__airport_city__icontains=query) |
                Q(destination_airport__airport_country__icontains=query) |
                Q(destination_airport__iata_code__icontains=query) |
                Q(destination_airport__icao_code__icontains=query) |
                Q(destination_airport__airport_type__icontains=query) |

                Q(departure_date__icontains=query)  |
                Q(departure_time__icontains=query)  |
                Q(arrival_date__icontains=query)  |
                Q(arrival_time__icontains=query)  
            )

            airports = Airport.objects.filter(
                Q(uid__icontains=query)  |
                Q(airport_name__icontains=query)  |
                Q(airport_city__icontains=query) |
                Q(airport_country__icontains=query) |
                Q(iata_code__icontains=query) |
                Q(icao_code__icontains=query) |
                Q(airport_type__icontains=query)
            )

            profiles = Profile.objects.filter(
                Q(uid__icontains=query)  |
                Q(full_name__icontains=query)  |
                Q(gender__icontains=query) |
                Q(passport_number__icontains=query) |
                Q(citizenship__icontains=query) |
                Q(mobile_number__icontains=query) |
                Q(user__email__icontains=query)
            )

            bookings = Booking.objects.filter(
                Q(uid__icontains=query)  |
                Q(person_name__icontains=query)  |
                Q(gender__icontains=query) |
                Q(passport_number__icontains=query) |
                Q(citizenship__icontains=query) |
                Q(mobile_number__icontains=query) |
                Q(email__icontains=query) |

                Q(pnr_code__icontains=query) |
                Q(fare_amount__icontains=query) |

                Q(profile__uid__icontains=query)  |
                Q(profile__full_name__icontains=query)  |
                Q(profile__gender__icontains=query) |
                Q(profile__passport_number__icontains=query) |
                Q(profile__citizenship__icontains=query) |
                Q(profile__mobile_number__icontains=query) |
                Q(profile__user__email__icontains=query) |

                Q(flight__uid__icontains=query)  |
                Q(flight__flight_number__icontains=query)  |

                Q(flight__origin_airport__airport_name__icontains=query)  |
                Q(flight__origin_airport__airport_city__icontains=query) |
                Q(flight__origin_airport__airport_country__icontains=query) |
                Q(flight__origin_airport__iata_code__icontains=query) |
                Q(flight__origin_airport__icao_code__icontains=query) |
                Q(flight__origin_airport__airport_type__icontains=query) |
                
                Q(flight__destination_airport__airport_name__icontains=query)  |
                Q(flight__destination_airport__airport_city__icontains=query) |
                Q(flight__destination_airport__airport_country__icontains=query) |
                Q(flight__destination_airport__iata_code__icontains=query) |
                Q(flight__destination_airport__icao_code__icontains=query) |
                Q(flight__destination_airport__airport_type__icontains=query) |

                Q(flight__departure_date__icontains=query)  |
                Q(flight__departure_time__icontains=query)  |
                Q(flight__arrival_date__icontains=query)  |
                Q(flight__arrival_time__icontains=query)  
            )

            payments = Payment.objects.filter(
                Q(payment_id__icontains=query)  |
                Q(amount__icontains=query)  |
                Q(created_at__icontains=query)  |
                Q(updated_at__icontains=query)  |

                Q(booking__person_name__icontains=query)  |
                Q(booking__gender__icontains=query) |
                Q(booking__passport_number__icontains=query) |
                Q(booking__citizenship__icontains=query) |
                Q(booking__mobile_number__icontains=query) |
                Q(booking__email__icontains=query) |

                Q(booking__pnr_code__icontains=query) |
                Q(booking__fare_amount__icontains=query) |

                Q(profile__uid__icontains=query)  |
                Q(profile__full_name__icontains=query)  |
                Q(profile__gender__icontains=query) |
                Q(profile__passport_number__icontains=query) |
                Q(profile__citizenship__icontains=query) |
                Q(profile__mobile_number__icontains=query) |
                Q(profile__user__email__icontains=query) |

                Q(flight__uid__icontains=query)  |
                Q(flight__flight_number__icontains=query)  |

                Q(flight__origin_airport__airport_name__icontains=query)  |
                Q(flight__origin_airport__airport_city__icontains=query) |
                Q(flight__origin_airport__airport_country__icontains=query) |
                Q(flight__origin_airport__iata_code__icontains=query) |
                Q(flight__origin_airport__icao_code__icontains=query) |
                Q(flight__origin_airport__airport_type__icontains=query) |
                
                Q(flight__destination_airport__airport_name__icontains=query)  |
                Q(flight__destination_airport__airport_city__icontains=query) |
                Q(flight__destination_airport__airport_country__icontains=query) |
                Q(flight__destination_airport__iata_code__icontains=query) |
                Q(flight__destination_airport__icao_code__icontains=query) |
                Q(flight__destination_airport__airport_type__icontains=query) |

                Q(flight__departure_date__icontains=query)  |
                Q(flight__departure_time__icontains=query)  |
                Q(flight__arrival_date__icontains=query)  |
                Q(flight__arrival_time__icontains=query)  
            )

            context = {
                'search_query' : query,
                "flight_result" : len(flights),
                "flights" : flights,
                "airport_result" : len(airports),
                "airports" : airports,
                "profile_result" : len(profiles),
                "profiles" : profiles,
                "booking_result" : len(bookings),
                "bookings" : bookings,
                "payment_result" : len(payments),
                "payments" : payments,
            }

            return render(request, "manage/search.html", context)
        return redirect('/manage/?no-query')
    except Exception as err:
        logger.error(err)