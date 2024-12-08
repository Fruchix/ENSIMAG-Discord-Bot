import datetime
import requests
import os

from enum import Enum
from pathlib import Path

from src.utils.datetime_utils import (
    get_week_id_relative_to_current,
    get_first_day_of_week,
)
from src.utils.logging_utils import init_logger

from src.config import LOG_FILE_EDT, EDT_DIR


logger = init_logger(LOG_FILE_EDT, "ensimag-bot.edt")


class EdtGrenobleInpGroupsEnum(Enum):
    Group1AA = {"name": "1AA", "resource": 6388}
    Group2AA = {"name": "2AA", "resource": 9314}

    Group1AG1 = {"name": "1A_G1", "resource": 9364}
    Group1AG2 = {"name": "1A_G2", "resource": 9362}
    Group1AG3 = {"name": "1A_G3", "resource": 9363}
    Group1AG4 = {"name": "1A_G4", "resource": 9367}
    Group1AG5 = {"name": "1A_G5", "resource": 9368}
    Group1AG6 = {"name": "1A_G6", "resource": 9365}
    Group1AG7 = {"name": "1A_G7", "resource": 9366}
    Group1AG8 = {"name": "1A_G8", "resource": 9369}

    GroupIF2A_G1 = {"name": "IF2A_G1", "resource": 9358}
    GroupIF2A_G2 = {"name": "IF2A_G2", "resource": 9359}

    GroupISI2A_G1 = {"name": "ISI2A_G1", "resource": 9353}
    GroupISI2A_G2 = {"name": "ISI2A_G2", "resource": 9351}
    GroupISI2A_G3 = {"name": "ISI2A_G3", "resource": 9352}
    GroupISI2A_G4 = {"name": "ISI2A_G4", "resource": 9350}

    GroupMMIS2A_G1 = {"name": "MMIS2A_G1", "resource": 9355}
    GroupMMIS2A_G2 = {"name": "MMIS2A_G2", "resource": 5579}
    GroupMMIS2A_G3 = {"name": "MMIS2A_G3", "resource": 9356}

    GroupSEOC2A_ENSIMAG = {"name": "SEOC2A_ENSIMAG", "resource": 9347}
    GroupSEOC2A_G1 = {"name": "SEOC2A_G1", "resource": 9348}
    GroupSEOC2A_PHELMA = {"name": "SEOC2A_PHELMA", "resource": 9345}

    # GroupIF3A_I2MF = {"name": "IF3A_I2MF", "resource": 9322}
    # GroupIF3A_MEQA = {"name": "IF3A_MEQA", "resource": 9321}
    # GroupISI3A = {"name": "ISI3A", "resource": 9318}
    # GroupMMIS3A = {"name": "MMIS3A", "resource": 9317}
    # GroupSEOC3A = {"name": "SEOC3A", "resource": 9319}


class EdtGrenobleInpOptions:
    DEFAULT_WIDTH = 900
    DEFAULT_HEIGHT = 900
    DEFAULT_ID_PIANO_DAY = "0,1,2,3,4"
    DEFAULT_GROUP = EdtGrenobleInpGroupsEnum.Group2AA

    # default values that should not be changed
    PROJECT_ID = 13
    DISPLAY_MODE = 1057855
    LUNCH_NAME = "REPAS"
    SHOW_LOAD = False
    DISPLAY_CONFIG_ID = 15

    FIRST_WEEK_ID = 0
    FIRST_WEEK_MONDAY: datetime.date = datetime.date.fromisoformat("2024-08-05")

    def __init__(self) -> None:
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT
        self.id_piano_day = self.DEFAULT_ID_PIANO_DAY
        self.group = self.DEFAULT_GROUP
        # get the current week by default
        self.set_week_id_relative_to_current(0)

    def set_width(self, width: int) -> None:
        self.width = width

    def set_height(self, height: int) -> None:
        self.height = height

    def set_week_id_relative_to_current(self, selected_week: int = 0) -> None:
        """Set the week id (from ADE) by selecting a week relative to the current week.

        :param current_week: number of weeks to shift from the current, defaults to 0
        :type current_week: int, optional
        """
        self.week_id = get_week_id_relative_to_current(
            self.FIRST_WEEK_MONDAY, selected_week
        )

    def set_group(self, group: EdtGrenobleInpGroupsEnum) -> None:
        self.group = group

    def get_dict(self):
        return {
            "idPianoWeek": self.week_id,
            "idPianoDay": self.id_piano_day,
            "idTree": self.group.value["resource"],
            "width": self.width,
            "height": self.height,
            "projectId": self.PROJECT_ID,
            "lunchName": self.LUNCH_NAME,
            "displayMode": self.DISPLAY_MODE,
            "showLoad": self.SHOW_LOAD,
            "displayConfId": self.DISPLAY_CONFIG_ID,
        }

    def get_pretty_week(self) -> str:
        fd = get_first_day_of_week(self.FIRST_WEEK_MONDAY, self.week_id)
        ld = fd + datetime.timedelta(days=4)
        return f"Du {fd.strftime('%d-%m-%Y')} au {ld.strftime('%d-%m-%Y')}."


class EdtGrenobleInpClient:
    def __init__(self) -> None:
        self.options = EdtGrenobleInpOptions()
        self.identifier = None

    def _init_session(self):
        self.session = requests.Session()
        self.session.get(
            "https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/standard/direct_planning.jsp"
        )
        self._init_identifier()
        logger.info(
            f"Created new Session for client with: JSESSIONID='{self.session.cookies.get_dict()['JSESSIONID']}'."
        )

    def _init_identifier(self):
        self.session.get(
            "https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/custom/modules/plannings/direct_planning.jsp?resources=9314"
        )
        r = self.session.get(
            "https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/custom/modules/plannings/imagemap.jsp?resources=9314&projectId=13&clearTree=false&width=842&height=851"
        )

        self.identifier = r.text.split("identifier=")[1].split("&")[0]
        logger.info(f"Client's identifier is now: identifier='{self.identifier}'.")

    def request(self, func_request_method, *args, **kwargs) -> requests.Response:
        """Wrapper to any http method from the requests module.
        Initialize the session and the identifier if they aren't already.

        :param func_request_method: an existing method from the requests module
        :type func_request_method: function
        :return: the request's response
        :rtype: requests.Response
        """
        r: requests.Response
        if self.identifier is None:
            self._init_session()

        r = func_request_method(*args, **kwargs)

        if r.status_code in [302, 404]:
            self._init_session()
            r = func_request_method(*args, **kwargs)
        return r

    def download_edt(self, group: EdtGrenobleInpGroupsEnum, selected_week: int) -> None:
        """Download the calendar according to the selected week.

        :param group: the group identifying wich timetable to get
        :type group: EdtGrenobleInpGroupsEnum
        :param selected_week: relatively to the current week being 0
        :type selected_week: int
        """
        self.options.set_group(group)
        self.options.set_week_id_relative_to_current(selected_week)

        filename = Path(EDT_DIR, f"edt-{group.name}-{self.options.week_id}.png")

        logger.info(
            f"Downloading {filename}: week='{self.options.week_id}',group='{self.options.group}' with identifier='{self.identifier}'."
        )

        # download the file only if it was downloaded more than a day ago,
        # or if it was downloaded more than a hour ago but is for the current week
        if Path(filename).is_file():
            mtime = datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)
            threshold = (
                datetime.timedelta(hours=1)
                if selected_week == 0
                else datetime.timedelta(days=1)
            )
            if mtime > datetime.datetime.now() - threshold:
                logger.info(
                    f"{filename} was already downloaded within the threshold='{threshold}'."
                )
                return

        try:
            edt = self.get_edt()
        except requests.exceptions.RequestException as e:
            # TODO: log instead of print
            print(e)
            return
        except Exception as e:  # bad practice to catch all exceptions
            # TODO: log instead of print
            print(e)
            return

        if edt is None:
            return

        with open(filename, "wb") as f:
            f.write(edt)

    def get_edt(self) -> bytes | None:
        """Get the edt identified by the current EdtGrenobleInpOptions."""
        if self.identifier is None:
            self._init_session()

        params = self.options.get_dict()
        params.update({"identifier": self.identifier})

        with self.request(
            self.session.get,
            "https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/imageEt",
            params=params,
            stream=True,
        ) as r:
            if r.status_code != 200 or r.headers["Content-Type"] != "image/gif":
                logger.error(
                    f"Failed edt request: week='{self.options.week_id}',group='{self.options.group}' with identifier='{self.identifier}'."
                )
                return None
            logger.info(
                f"Successful edt request: week='{self.options.week_id}',group='{self.options.group}' with identifier='{self.identifier}'."
            )
            return r.content
