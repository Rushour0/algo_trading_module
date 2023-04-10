import datetime
import json
from allTypes.strategy import ExpiryType


def next_expiry_date(expiry_type: ExpiryType, date=datetime.date.today()):
    next_expiry = next_thursday(date)
    next_to_next_expiry = next_thursday(
        next_expiry + datetime.timedelta(days=1))
    if holiday_checking(next_to_next_expiry):
        next_to_next_expiry = next_to_next_expiry - datetime.timedelta(days=1)

    return next_expiry


def next_expiry_date_kite(expiry_type: ExpiryType, date=datetime.date.today()):
    next_expiry = next_thursday(date)
    next_to_next_expiry = next_thursday(
        next_expiry + datetime.timedelta(days=1))

    if holiday_checking(next_to_next_expiry):
        next_to_next_expiry = next_to_next_expiry - datetime.timedelta(days=1)

    if next_to_next_expiry.month != next_expiry.month:
        return f"{next_expiry.year % 100}{next_expiry.strftime('%b').upper()}"

    return f"{next_expiry.year % 100}{translate_month_kite(next_expiry.month)}{'0' + str(next_expiry.day) if next_expiry.day < 10  else next_expiry.day}"


def next_expiry_date_shoonya(expiry_type: ExpiryType, date=datetime.date.today()):
    next_expiry = next_thursday(date)
    next_to_next_expiry = next_thursday(
        next_expiry + datetime.timedelta(days=1))

    if holiday_checking(next_to_next_expiry):
        next_to_next_expiry = next_to_next_expiry - datetime.timedelta(days=1)

    return f"{'0' + str(next_expiry.day) if next_expiry.day < 10  else next_expiry.day}{translate_month_shoonya(next_expiry.month)}{next_expiry.year % 100}"


def translate_month_kite(month: int):
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, "O", "N", "D"]
    return months[month-1]


def translate_month_shoonya(month: int):
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    return months[month-1]


def shoonya_to_kite_expiry(expiry: str):
    shoonya_months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                      "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    kite_months = [1, 2, 3, 4, 5, 6, 7, 8, 9, "O", "N", "D"]

    for month in shoonya_months:
        if month in expiry:
            start_index = expiry.index(month)
            expiry = expiry[:start_index - 2] + expiry[start_index + 3:start_index + 5] + str(
                kite_months[shoonya_months.index(month)]) + expiry[start_index - 2:start_index] + expiry[start_index + 5:]

            return expiry.replace(month, str(kite_months[shoonya_months.index(month)]))


def next_thursday(date=datetime.date.today()):
    if date.weekday() == 3:
        thursday = date + datetime.timedelta(days=7)
    else:
        thursday = date + datetime.timedelta((3 - date.weekday()) % 7)

    if holiday_checking(thursday):
        return date + datetime.timedelta((2 - date.weekday()) % 7)
    return thursday


def holiday_checking(date=datetime.date.today()):
    # download data from https://www.nseindia.com/api/holiday-master?type=trading
    holidays = get_holidays()

    if date in holidays:

        return True
    return False


def get_holidays():

    try:
        with open('holidays.json', 'r') as f:
            raw_holidays = json.load(f)

            holidays = [datetime.datetime.strptime(
                holiday, '%d-%b-%Y').date() for holiday in raw_holidays['holidays']]

            if datetime.date.today().year != holidays[0].year:
                raise Exception("Holidays are not updated")
            return holidays

    except Exception as e:

        holidays = [holiday['tradingDate'] for holiday in raw_holidays['CM']]
        json.dump({'holidays': holidays}, open('holidays.json', 'w'))

    return holidays


if __name__ == "__main__":
    holiday_checking()
