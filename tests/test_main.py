import main
import datetime
import pytest


def test_init_WorkDay_required_inputs():
    """Checks that with the required inputs, the class is successfully 
    initialised
    """

    date = datetime.date(2020, 1, 7)
    start, end = datetime.time(9, 15), datetime.time(17, 0)

    work_day = main.WorkDay(date, start, end)

    assert work_day.date == date
    exp_start = datetime.datetime.combine(date, start)
    exp_end = datetime.datetime.combine(date, end)
    assert work_day.start == exp_start
    assert work_day.end == exp_end
    assert work_day.lunch_start is None
    assert work_day.lunch_end is None


def test_init_WorkDay_end_before_start_checked():
    """Ensure the end time is checked to be after the start
    """

    date = datetime.date(2020, 1, 7)
    start, end = datetime.time(9, 15), datetime.time(17, 0)
    with pytest.raises(ValueError):
        main.WorkDay(date, start=end, end=start)


def test_init_WorkDay_lunch_specified():
    """Checks that if lunch times are specified, they are stored accordingly
    """

    date = datetime.date(2020, 1, 7)
    start, end = datetime.time(9, 15), datetime.time(17, 0)
    l_start, l_end = datetime.time(12, 0), datetime.time(13, 0)

    work_day = main.WorkDay(date, start, end, (l_start, l_end))

    assert work_day.date == date
    exp_start = datetime.datetime.combine(date, start)
    exp_end = datetime.datetime.combine(date, end)
    assert work_day.start == exp_start
    assert work_day.end == exp_end
    exp_l_start = datetime.datetime.combine(date, l_start)
    exp_l_end = datetime.datetime.combine(date, l_end)
    assert work_day.lunch_start == exp_l_start
    assert work_day.lunch_end == exp_l_end


def test_init_WorkDay_lunch_start_before_day_start():
    """Checks that the validity of the lunch duration is checked
    """

    date = datetime.date(2020, 1, 7)
    start, end = datetime.time(9, 15), datetime.time(17, 0)
    l_start, l_end = datetime.time(8, 0), datetime.time(13, 0)
    with pytest.raises(ValueError):
        main.WorkDay(date, start, end, (l_start, l_end))


def test_init_WorkDay_lunch_start_after_day_end():
    """Checks that the validity of the lunch duration is checked
    """

    date = datetime.date(2020, 1, 7)
    start, end = datetime.time(9, 15), datetime.time(17, 0)
    l_start, l_end = datetime.time(18, 0), datetime.time(13, 0)
    with pytest.raises(ValueError):
        main.WorkDay(date, start, end, (l_start, l_end))


def test_init_WorkDay_lunch_end_before_lunch_start():
    """Checks that the validity of the lunch duration is checked
    """

    date = datetime.date(2020, 1, 7)
    start, end = datetime.time(9, 15), datetime.time(17, 0)
    l_start, l_end = datetime.time(13, 0), datetime.time(12, 0)
    with pytest.raises(ValueError):
        main.WorkDay(date, start, end, (l_start, l_end))


def test_init_WorkDay_lunch_end_after_day_end():
    """Checks that the validity of the lunch duration is checked
    """

    date = datetime.date(2020, 1, 7)
    start, end = datetime.time(9, 15), datetime.time(17, 0)
    l_start, l_end = datetime.time(12, 0), datetime.time(18, 0)
    with pytest.raises(ValueError):
        main.WorkDay(date, start, end, (l_start, l_end))


@pytest.fixture
def mock_WorkDay():
    """Creates a random piv Image
    """
    date = datetime.date(2020, 1, 7)
    start, end = datetime.time(9, 15), datetime.time(17, 30)
    l_start, l_end = datetime.time(12, 30), datetime.time(13, 30)
    return main.WorkDay(date, start, end, (l_start, l_end))

def test_WorkDay_lunch_duration(mock_WorkDay):
    """Test that the currect duration is returned for lunch if there is one
    """

    exp_tdelta = datetime.timedelta(0, 3600)
    assert mock_WorkDay.lunch_duration() == exp_tdelta

def test_WorkDay_lunch_duration_no_lunch(mock_WorkDay):
    """Check that lunch duration returns 0 seconds if there is no lunch data
    """    

    # modify mock object to have no lunch
    mock_WorkDay.lunch_start, mock_WorkDay.lunch_end = None, None

    exp_tdelta = datetime.timedelta(0, 0)
    assert mock_WorkDay.lunch_duration() == exp_tdelta

def test_WorkDay_work_hours(mock_WorkDay):
    """Test the duration of the day is correct, and accounts for lunch
    """

    # 9:15 - 17:30 with 1 hour for lunch = 7h15 = 26100s
    exp_tdelta = datetime.timedelta(seconds=26100)
    assert mock_WorkDay.work_hours() == exp_tdelta




    
