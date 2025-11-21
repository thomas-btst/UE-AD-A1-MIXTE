from ..BookingDBConnector import BookingDBConnector, Booking
import json

class BookingDBJsonConnector(BookingDBConnector):

    def __init__(self):
        self.db_path = '{}/data/bookings.json'.format(".")
        self.db_root_key = 'bookings'

        with open(self.db_path, "r") as jsf:
            self.bookings = json.load(jsf)[self.db_root_key]

    def write(self):
        with open(self.db_path, 'w') as f:
            full = {self.db_root_key: self.bookings}
            json.dump(full, f)

    def find_by_userid_or_none(self, userid: str) -> Booking | None:
        return next(filter(lambda _booking: _booking["userid"] == userid, self.bookings), None)

    def find_all(self) -> list[Booking]:
        return self.bookings

    def create(self, booking: Booking):
        self.bookings.append(booking)
        self.write()

    def update(self, booking: Booking):
        found_booking = self.find_by_userid_or_none(booking["userid"])
        found_booking["userid"] = booking["userid"]
        found_booking["dates"] = booking["dates"]
        self.write()

    def delete(self, userid: str):
        booking = self.find_by_userid_or_none(userid)
        self.bookings.remove(booking)
        self.write()

