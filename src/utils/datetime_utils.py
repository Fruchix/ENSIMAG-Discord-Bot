import datetime

def select_current_semaine() -> datetime.date:
    """Select the first day of the current week. If it is the weekend, select the first day of the next week."""

    # get first day of the week
    deb_sem = datetime.date.today() - datetime.timedelta(datetime.date.today().weekday())

    # if on the weekend, select the first day of the next week
    if datetime.date.today().weekday() > 4:
        deb_sem = deb_sem + datetime.timedelta(7)

    return deb_sem

def get_week_id(start_date: datetime.date, selected_date: datetime.date) -> int:
    """Get the week id of the given date, starting from the start_date."""
    return (selected_date - start_date).days // 7
