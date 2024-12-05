import datetime
import requests

from enum import Enum

from src.utils.datetime_utils import select_current_semaine, get_week_id


class EdtGrenobleInpGroups(Enum):
    Group2AA = {"name": "2AA", "resource": 9314}


class EdtGrenobleInpOptions:
    DEFAULT_WIDTH = 793
    DEFAULT_HEIGHT = 851
    DEFAULT_ID_PIANO_DAY = "0,1,2,3,4,5,6"
    DEFAULT_RESOURCE = EdtGrenobleInpGroups.Group2AA.value["resource"]

    # default values that should not be changed
    PROJECT_ID = 13
    DISPLAY_MODE = 1057855
    LUNCH_NAME = "REPAS"
    SHOW_LOAD = False
    DISPLAY_CONFIG_ID = 15

    FIRST_WEEK_ID = 0
    FIRST_WEEK_MONDAY_DATETIME = datetime.date.fromisoformat("2024-08-05")

    def __init__(self) -> None:
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT
        self.id_piano_day = self.DEFAULT_ID_PIANO_DAY
        self.resource = self.DEFAULT_RESOURCE
        # get the current week by default
        self.set_week_starting_from_current(0)

    def set_width(self, width: int) -> None:
        self.width = width

    def set_height(self, height: int) -> None:
        self.height = height

    def set_week_starting_from_current(self, week: int = 0) -> None:
        """Set the week starting from the current week.

        Args:
            week (int, optional): number of weeks to shift from the current. Defaults to 0.
        """
        self.week = (
            get_week_id(self.FIRST_WEEK_MONDAY_DATETIME, select_current_semaine())
            + week
        )

    def set_resource(self, resource: EdtGrenobleInpGroups) -> None:
        self.resource = resource

    def get_dict(self):
        return {
            "idPianoWeek": self.week,
            "idPianoDay": self.id_piano_day,
            "idTree": self.resource.value["resource"],
            "width": self.width,
            "height": self.height,
            "projectId": self.PROJECT_ID,
            "lunchName": self.LUNCH_NAME,
            "displayMode": self.DISPLAY_MODE,
            "showLoad": self.SHOW_LOAD,
            "displayConfId": self.DISPLAY_CONFIG_ID,
        }


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

    def _init_identifier(self):
        self.session.get(
            "https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/custom/modules/plannings/direct_planning.jsp?resources=9314"
        )
        r = self.session.get(
            "https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/custom/modules/plannings/imagemap.jsp?resources=9314&projectId=13&clearTree=false&width=842&height=851"
        )

        self.identifier = r.text.split("identifier=")[1].split("&")[0]

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

    def download_edt(self, resource: EdtGrenobleInpGroups, week: int) -> None:
        self.options.set_resource(resource)
        self.options.set_week_starting_from_current(week)

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

        with open(f"data/edt-{resource.name}-{self.options.week}.png", "wb") as f:
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
                return None
            return r.content


edt = EdtGrenobleInpClient()
edt.download_edt(EdtGrenobleInpGroups.Group2AA, 0)
edt.download_edt(EdtGrenobleInpGroups.Group2AA, 1)
edt.download_edt(EdtGrenobleInpGroups.Group2AA, 2)
edt.download_edt(EdtGrenobleInpGroups.Group2AA, 3)
