from datetime import datetime as dtime
from datetime import timedelta
import json
import csv
import itertools


class WorkDay():
    def __init__(self, date, start, end, lunch_start_end=None):
        """Initialises a 'WorkDay' object to track working hours

        Checks the validity of the times:
                start < end
                lunch start > start
                lunch start < end
                lunch end > lunch start
                lunch end < end
        
        Arguments:
            date {datetime.date}: The date of the day being considered
            start {datetime.time}: The time of day that work started
            end {datetime.time}: The time of day that work ended
                                   Must be after the start time
            lunch_start_end {tuple, datetime.time}: Contains both the start
                                                    and end times for lunch
                                                    if desired. Must be entirely
                                                    within the day start and end 
                                                    times for the day, and the
                                                    lunch end must come after 
                                                    the lunch start                                                     
        """
        
        # note no input checking.
        self.date = date
        self.start = dtime.combine(self.date, start)
        if end > start:
            self.end = dtime.combine(self.date, end)
        else:
            raise ValueError("End must come after start")
        
        self.lunch_start, self.lunch_end = None, None
        if lunch_start_end is not None:
            if not len(lunch_start_end) == 2:
                raise ValueError("Both lunch start and end must be specified")
            else:
                self.lunch_start = dtime.combine(self.date, lunch_start_end[0])
                self.lunch_end = dtime.combine(self.date, lunch_start_end[1])
                if self.lunch_start < self.start:
                    raise ValueError("Lunch started before day started")
                if self.lunch_start > self.end:
                    raise ValueError("Lunch started after day ended")
                if self.lunch_end < self.lunch_start:
                    raise ValueError("Lunch ended before it started")
                if self.lunch_end > self.end:
                    raise ValueError("Lunch ended after the day ended")
    
    def __str__(self):
        out = f"On {self.date}, you started work at {self.start.time()} and " 
        out += f"worked for {self.work_hours()}hrs and had "
        out += f"{self.lunch_duration()}hrs for lunch."
        return out

    def lunch_duration(self):
        """Return the length of the lunch break for the day as a timedelta
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
        all_days {list, WorkDay} -- a list of WorkDay objects
    """

    with open(filename) as file:
        raw_data = json.load(file)

    # convert dictionary data into more convenient form
    all_days = []
    for day in raw_data:
        date = dtime.strptime(day['date'], "%d/%m/%Y").date()
        start = dtime.strptime(day['start'], "%H:%M").time()
        end = dtime.strptime(day['end'], "%H:%M").time()
        try:
            lunch_start = dtime.strptime(day['lunch_start'], "%H:%M").time()
            lunch_end = dtime.strptime(day['lunch_end'], "%H:%M").time()
            lunch_start_end = (lunch_start, lunch_end)
        except KeyError:
            lunch_start_end = None
                   
        all_days.append(WorkDay(date, start, end, lunch_start_end))

    return all_days


def convert_csv_data_to_json(csv_file_in, file_out):
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

    convert_csv_data_to_json('work_hours.csv', 'all_data.json')
    all_days = parse_work_json_data('all_data.json')

    for dh in all_days:
        print(dh)
