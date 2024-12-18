import datetime


def select_current_week() -> datetime.date:
    """Select the first day of the current week. If it is the weekend, select the first day of the next week."""

    # get first day of the week
    deb_sem = datetime.date.today() - datetime.timedelta(
        datetime.date.today().weekday()
    )

    # if on the weekend, select the first day of the next week
    if datetime.date.today().weekday() > 4:
        deb_sem = deb_sem + datetime.timedelta(7)

    return deb_sem


def get_week_id(start_date: datetime.date, selected_date: datetime.date) -> int:
    """Get the week id of the given date, starting from the start_date."""
    return (selected_date - start_date).days // 7


def get_week_id_relative_to_current(start_date: datetime.date, relative_week: int) -> int:
    return get_week_id(start_date, select_current_week()) + relative_week


def get_first_day_of_week(start_date: datetime.date, week_id: int) -> datetime.date:
    """Get the date of the first day of the week starting from the start_date."""
    return start_date + datetime.timedelta(week_id * 7)
