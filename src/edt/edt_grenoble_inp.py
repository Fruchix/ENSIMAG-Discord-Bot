import datetime
import requests

from src.utils.datetime_utils import select_current_semaine, get_week_id
from src.utils.selenium_utils import DriverFactory, DriverEnum

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from enum import Enum

class EdtGrenobleInpResources(Enum):
    Group2AA = 9314

class EdtGrenobleInpOptions:
    DEFAULT_WIDTH = 793
    DEFAULT_HEIGHT = 851
    DEFAULT_ID_PIANO_DAY = "0,1,2,3,4,5,6"
    DEFAULT_RESOURCE = EdtGrenobleInpResources.Group2AA
    
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
        self.week = get_week_id(self.FIRST_WEEK_MONDAY_DATETIME, select_current_semaine()) + week
    
    def set_resource(self, resource: EdtGrenobleInpResources) -> None:
        self.resource = resource
    
    def get_dict(self):
        return {
            "idPianoWeek": self.week,
            "idPianoDay": self.id_piano_day,
            "idTree": self.resource.value,
            "width": self.width,
            "height": self.height,
            "projectId": self.PROJECT_ID,
            "lunchName": self.LUNCH_NAME,
            "displayMode": self.DISPLAY_MODE,
            "showLoad": self.SHOW_LOAD,
            "displayConfId": self.DISPLAY_CONFIG_ID
        }


class EdtGrenobleInpClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self._init_cookies_and_identifier()
        self.options = EdtGrenobleInpOptions()

    def _init_cookies_and_identifier(self) -> None:
        driver = DriverFactory.build(
            DriverEnum.CHROME,
            executable_path='/usr/bin/chromedriver',
            options=["--headless"]
        )

        driver.get("https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/standard/direct_planning.jsp")

        # set session cookies
        self.session.cookies.set("JSESSIONID", driver.get_cookie("JSESSIONID")["value"])
        self.session.cookies.set("BIGipServer~ADE~pool_ade-inp-ro", driver.get_cookie("BIGipServer~ADE~pool_ade-inp-ro")["value"])

        try:
            driver.implicitly_wait(2)
            driver.switch_to.frame("tree")

            # search a group that exists: need to produce an image
            search_input = driver.find_element(By.CSS_SELECTOR, "input[name='search']")
            search_input.send_keys("2aa")
            search_input.send_keys(Keys.RETURN)

            driver.implicitly_wait(3)
            driver.switch_to.parent_frame()
            driver.switch_to.frame("et")

            image = driver.find_element(By.XPATH, "/html/body/img")
            image_url = image.get_attribute("src")
        except Exception as e: # bad practice to catch all exceptions
            # TODO: log instead of print
            print(e)
        finally:
            driver.quit()
        
        self.identifier = image_url.split("identifier=")[1].split("&")[0]

    def download_edt(self, resource: EdtGrenobleInpResources, week: int):
        self.options.set_resource(resource)
        self.options.set_week_starting_from_current(week)

        try:
            edt = self.get_edt()
        except requests.exceptions.RequestException as e:
            # TODO: log instead of print
            print(e)
            return
        except Exception as e: # bad practice to catch all exceptions
            # TODO: log instead of print
            print(e)
            return

        with open(f"data/edt-{resource.name}-{self.options.week}.png", "wb") as f:
            f.write(edt)
    
    def get_edt(self) -> bytes:
        """Get the edt identified by the current EdtGrenobleInpOptions."""
        params = self.options.get_dict()
        params.update({"identifier": self.identifier})
        
        return self.session.get("https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/imageEt", params=params).content
