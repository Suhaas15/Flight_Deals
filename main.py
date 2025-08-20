#This file will need to use the DataManager,FlightSearch, FlightData, NotificationManager classes to achieve the program requirements.
#Form responder link - https://docs.google.com/forms/d/e/1FAIpQLSf2K1UsAHuh7oVz_aV-DnjziWq9qBjEk2xE01y2zSlUISd0AQ/viewform?usp=dialog
from collections import defaultdict
from data_manager import DataManager
from flight_data import find_cheapest_flight
from flight_search import FlightSearch
from notification_manager import NotificationManager
from pprint import pprint
import time
from datetime import datetime,timedelta

EMAIL_KEY = 'email,SoYouCanSay “iSawItFirst”'
ORIGIN_KEY = 'whereAreWeTakingOffFrom?'

def build_users_by_origin(user_rows: list[dict]) -> dict[str,list[str]]:
    grouped=defaultdict(list)
    for row in user_rows:
        email = row[EMAIL_KEY].strip()
        origin = row[ORIGIN_KEY].strip().upper()
        grouped[origin].append(email)
    return grouped

def format_message(cheapest) -> str:
    if cheapest.stops==0:
        return (
            f"Low price alert! Only {cheapest.price} USD to fly direct "
            f"from {cheapest.origin_airport} to {cheapest.destination_airport}, "
            f"on {cheapest.out_date} until {cheapest.return_date}."
        )
    else:
        return (
            f"Low price alert! Only USD {cheapest.price} to fly "
            f"from {cheapest.origin_airport} to {cheapest.destination_airport}, "
            f"with {cheapest.stops} stop(s) departing on {cheapest.out_date} and returning on {cheapest.return_date}."
        )

def best_of_direct_and_indirect(flight_search: FlightSearch, origin_iata: str, dest_iata: str, dep_date: datetime, ret_date: datetime):
    direct_json = flight_search.check_flights(
        origin_iata, dest_iata, from_time=dep_date, to_time=ret_date, is_direct=True
    )
    indirect_json = flight_search.check_flights(
        origin_iata, dest_iata, from_time=dep_date, to_time=ret_date, is_direct=False
    )

    direct_best = find_cheapest_flight(direct_json) if direct_json else type("N", (), {"price": "N/A"})()
    indirect_best = find_cheapest_flight(indirect_json) if indirect_json else type("N", (), {"price": "N/A"})()

    if direct_best.price == "N/A" and indirect_best.price == "N/A":
        return direct_best
    if direct_best.price == "N/A":
        return indirect_best
    if indirect_best.price == "N/A":
        return direct_best
    return direct_best if direct_best.price<=indirect_best.price else indirect_best

# ---------- main flow ----------
if __name__ == "__main__":
    data_manager = DataManager()
    flight_search = FlightSearch()
    notification_manager = NotificationManager()

    sheet_data = data_manager.get_destination_data()
    # ORIGIN_CITY_IATA="SFO"

    for row in sheet_data:
        if not row.get("iataCode"):
            row["iataCode"] = flight_search.get_destination_code(row["city"])
            time.sleep(2)           #slowing down requests to avoid hitting rate limit
    pprint(f"sheet data:\n {sheet_data}")

    data_manager.destination_data = sheet_data
    data_manager.update_destination_codes()

    customer_rows = data_manager.get_customer_emails()
    users_by_origin = build_users_by_origin(customer_rows)
    print("Users grouped by origin:", dict(users_by_origin))

    tomorrow = datetime.now() + timedelta(days=1)
    six_months_from_today=datetime.now()+timedelta(days=(6*30))

    for origin_iata, email_list in users_by_origin.items():
        if not email_list:
            continue
        print(f"\n🔎 Searching routes for origin {origin_iata} (recipients: {len(email_list)})")
        for destination in sheet_data:
            dest_iata = destination["iataCode"]
            print(f"  → {destination['city']} ({dest_iata})")

            cheapest = best_of_direct_and_indirect(
                flight_search, origin_iata, dest_iata, dep_date=tomorrow, ret_date=six_months_from_today
            )
            print(f"     Cheapest found: USD {cheapest.price}")

            # Only notify if cheaper than user's configured threshold in the prices sheet
            if cheapest.price != "N/A" and cheapest.price < destination["lowestPrice"]:
                message = format_message(cheapest)
                print(f"     ✅ Sending email to {len(email_list)} users for {destination['city']}")
                notification_manager.send_emails(email_list=email_list, email_body=message)
                notification_manager.send_whatsapp(message_body=message)

            time.sleep(2)



