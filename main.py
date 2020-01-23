from datetime import datetime as dtime
from datetime import timedelta
import json
import csv


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
        """Return the number of hours worked, accounting for lunch, as a
        timedelta
        """
        return self.end - self.start - self.lunch_duration()


class WorkHistory():
    def __init__(self, work_days, allowed_leave=None):
        """Manages the full dataset of working hours and provides insights into 
        aggregate data such as average working time, lunch time, etc  

        Args:
            work_days (WorkDay, list): List of WorkDay objects with the start
                                      and end times for each day.
            allows_leave (float): The number of days allocated for leave in a 
                                  calendar year. This includes sick days.
                                  Defaults to 38.5 which is equivalent to the 
                                  national average of 33.5 days of annual leave
                                  and 5 days of sick leave.
        """

        self.all_days = work_days

        if allowed_leave is None:
            self.allowed_leave = 38.5
        else:
            self.allowed_leave = allowed_leave

    @property
    def n_days(self):
        """Gets the number of days worked
        """
        return len(self.all_days)

    def average_work_duration(self):
        """Return the simple average number of hours worked per day. That is, 
        On all of the days worked, what was the average number of hours. 

        This is susceptible to bias from e.g. half days or working a couple 
        of hours on a weekend and so is a poor measure

        """

        tot_hours = timedelta(seconds=0)
        for day in self.all_days:
            tot_hours += day.work_hours()

        return tot_hours / self.n_days


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

        for row in xls_data:
            # get the date from the datevalue
            date = (dtime(1899, 12, 30)
                    + timedelta(days=int(row[2]))).date()
            time = dtime(1900, 1, 1, hour=int(
                row[3]), minute=int(row[4])).time()
            if row[5] == "Work Start":
                t_start = time
            elif row[5] == "Lunch Start":
                t_l_start = time
            elif row[5] == "Lunch End":
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

    work_hist = WorkHistory(all_days)
    print(work_hist.average_work_duration())
