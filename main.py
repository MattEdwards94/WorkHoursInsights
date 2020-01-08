from datetime import datetime as dtime
from datetime import timedelta
import json
import csv
import itertools


class DayHours():
    def __init__(self, time_dict):
        """Initialises a 'DayHours' object from dictionary based data

        Required format:
            date: dd/mm/yyyy
            start: hh:mm
            end: hh:mm
            lunch_start (optional): hh:mm
            lunch_end (optional): hh:mm

        Checks the validity of the times:
                start < end
                lunch start > start
                lunch start < end
                lunch end > lunch start
                lunch end < end
        """

        self.date = dtime.strptime(time_dict['date'], "%d/%m/%Y").date()
        self.start = dtime.strptime(time_dict['start'], "%H:%M")
        self.end = dtime.strptime(time_dict['end'], "%H:%M")

        # attempt to parse lunch data. If no lunch start time is given, then we
        # don't require an end either.
        # Yet if one but not the other is given, this should raise an error
        try:
            self.lunch_start = dtime.strptime(time_dict['lunch_start'],
                                              "%H:%M")
        except KeyError:
            self.lunch_start = None

        try:
            self.lunch_end = dtime.strptime(time_dict['lunch_end'],
                                            "%H:%M")
            # upon succesful parsing of lunch end, we should check if we
            # have a lunch start
            if self.lunch_start is None:
                raise KeyError("Lunch end found, but no lunch start")
        except KeyError:
            if self.lunch_start is not None:
                # there is a start, but no end
                raise KeyError("Lunch end not found")
            # otherwise, they both don't exist so just continue.

        # Now we need to check the times are valid and make sense
        if self.start > self.end:
            raise ValueError("Day ended before it started")

        if self.lunch_start is not None:
            if self.lunch_start < self.start:
                raise ValueError("Lunch started before day started")
            if self.lunch_start > self.end:
                raise ValueError("Lunch started after day ended")
            if self.lunch_end < self.lunch_start:
                raise ValueError("Lunch ended before it started")
            if self.lunch_end > self.end:
                raise ValueError("Lunch ended after the day ended")

    def lunch_duration(self):
        """Return the length of the lunch break for the day
        """
        if self.lunch_start is None:
            return timedelta(seconds=0)
        else:
            return self.lunch_end - self.lunch_start

    def work_hours(self):
        """Return the number of hours worked, accounting for lunch
        """
        return self.end - self.start - self.lunch_duration()


def parse_work_json_data(filename):
    """Parses the specified JSON file to gather the various start and end times.

    Required format:
        {
            "date": "dd/mm/yyyy"
            "start": "hh:mm"
            "end": "hh:mm"
            "lunch_start": (optional): "hh:mm"
            "lunch_end": (optional): "hh:mm"
        },
        {
            "date": "dd/mm/yyyy"
            "start": "hh:mm"
            "end": "hh:mm"
            "lunch_start": (optional): "hh:mm"
            "lunch_end": (optional): "hh:mm"
        },
        ...



    Arguments:
        filename {string} -- The location of the json file containing
                             start and end times

    Returns:
        all_days {list, DayHours} -- a list of DayHours objects
    """

    with open(filename) as file:
        raw_data = json.load(file)

    # convert dictionary data into more convenient form
    all_days = []
    for day in raw_data:
        all_days.append(DayHours(day))

    return all_days


def parse_csv_data(csv_file_in, file_out):
    """Quick script to extract all the data presently stored in a csv file,
    and format into more useable json file.

    writes the output json to 'file_out'

    Example csv file:
    June 19, 2018 at 09:32AM, entered, 43270, 9, 32, Work Start, Tuesday
    June 19, 2018 at 12:34PM, exited, 43270, 12, 34, Lunch Start, Tuesday
    June 19, 2018 at 01:55PM, entered, 43270, 13, 55, Lunch End, Tuesday
    June 19, 2018 at 06:50PM, exited, 43270, 18, 50, Work End, Tuesday

    """
    dict_list = []

    with open(csv_file_in) as xls_file:
        xls_data = csv.reader(xls_file)
        t_start, t_l_start, t_l_end, t_end = None, None, None, None

        for row in itertools.islice(xls_data, 0, 12):
            # get the date from the datevalue
            date = (dtime(1899, 12, 30)
                    + timedelta(days=int(row[4]))).date()
            time = dtime(1900, 1, 1, hour=int(
                row[5]), minute=int(row[6])).time()
            if row[7] == "Work Start":
                t_start = time
            elif row[7] == "Lunch Start":
                t_l_start = time
            elif row[7] == "Lunch End":
                t_l_end = time
            else:
                # Work end:
                t_end = time

                # construct dict
                t_dict = {"date": date.strftime("%d/%m/%Y"),
                          "start": t_start.strftime("%H:%M"),
                          "end": t_end.strftime("%H:%M"), }
                if t_l_start is not None:
                    t_dict["lunch_start"] = t_l_start.strftime("%H:%M")
                if t_l_end is not None:
                    t_dict["lunch_end"] = t_l_end.strftime("%H:%M")
                print(t_dict)
                dict_list.append(t_dict)
                # reset values for next 'day'
                t_start, t_l_start, t_l_end, t_end = None, None, None, None
                t_dict = None

    # now we need to export the list of dh objects into a json file
    with open(file_out, 'w') as out_file:
        json.dump(dict_list, out_file)


if __name__ == "__main__":
    # data = parse_work_json_data('mock_data.json')

    # for day in data:
    #     print(day.date)
    #     print(day.lunch_duration())
    #     print(day.work_hours())

    parse_csv_data('work_hours.csv', 'all_data.json')
    all_days = parse_work_json_data('all_data.json')

    for dh in all_days:
        print(dh.work_hours())
