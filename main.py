#This file will need to use the DataManager,FlightSearch, FlightData, NotificationManager classes to achieve the program requirements.
#Form responder link - https://docs.google.com/forms/d/e/1FAIpQLSf2K1UsAHuh7oVz_aV-DnjziWq9qBjEk2xE01y2zSlUISd0AQ/viewform?usp=dialog

from data_manager import DataManager
from flight_data import find_cheapest_flight
from flight_search import FlightSearch
from notification_manager import NotificationManager
from pprint import pprint
import time
from datetime import datetime,timedelta

data_manager = DataManager()
sheet_data = data_manager.get_destination_data()
# pprint(sheet_data)
flight_search = FlightSearch()
notification_manager = NotificationManager()

ORIGIN_CITY_IATA="SJC"

for row in sheet_data:
    if row["iataCode"]=="":
        row["iataCode"] = flight_search.get_destination_code(row["city"])
        time.sleep(2)           #slowing down requests to avoid hitting rate limit
pprint(f"sheet data:\n {sheet_data}")

data_manager.destination_data = sheet_data
data_manager.update_destination_codes()

customer_data = data_manager.get_customer_emails()
pprint(customer_data)
customer_email_list = [row["whereShouldWeSendYourBoardingPass?"] for row in customer_data]
pprint(f"customer data:\n {customer_email_list}")

tomorrow = datetime.now() + timedelta(days=1)
six_months_from_today=datetime.now()+timedelta(days=(6*30))

def check_and_send_email(cheapest_flight):
    if cheapest_flight.price != "N/A" and cheapest_flight.price < destination["lowestPrice"]:
        if cheapest_flight.stops == 0:
            message = f"Low price alert! Only USD {cheapest_flight.price} to fly direct " \
                      f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, " \
                      f"on {cheapest_flight.out_date} until {cheapest_flight.return_date}."
        else:
            message = f"Low price alert! Only USD {cheapest_flight.price} to fly " \
                      f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, " \
                      f"with {cheapest_flight.stops} stop(s) " \
                      f"departing on {cheapest_flight.out_date} and returning on {cheapest_flight.return_date}."
        print(f"Check your email. Lower price flight found to {destination['city']}!!")
        notification_manager.send_whatsapp(message_body=message)
        notification_manager.send_emails(email_list=customer_email_list, email_body=message)
    elif cheapest_flight.price == "N/A":
        print(f"No direct flight to {destination['city']}. Looking for indirect flights...")
        stopover_flights = flight_search.check_flights(
            ORIGIN_CITY_IATA,
            destination["iataCode"],
            from_time=tomorrow,
            to_time=six_months_from_today,
            is_direct=False,
        )
        cheapest_flight = find_cheapest_flight(stopover_flights)
        print(f"Cheapest indirect flight price is: ${cheapest_flight.price}")
        check_and_send_email(cheapest_flight)


for destination in sheet_data:
    print(f"Getting flights for {destination['city']}...")
    flights=flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination["iataCode"],
        from_time=tomorrow,
        to_time=six_months_from_today,
    )
    cheapest_flight=find_cheapest_flight(flights)
    print(f"{destination['city']}: ${cheapest_flight.price}")
    time.sleep(2)
    check_and_send_email(cheapest_flight)



