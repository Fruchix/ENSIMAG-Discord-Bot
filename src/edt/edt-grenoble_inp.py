from time import sleep
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class EdtGrenobleINP:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.get("https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/standard/direct_planning.jsp")

    def get_identifier(self):
        # https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/custom/modules/plannings/imagemap.jsp?projectId=13&clearTree=false&week=17&reset=true&width=1032&height=851
        params = {
            "projectId": 13,
            "clearTree": False,
            "week": 17,
            "reset": True,
            "width": 1032,
            "height": 851
        }
        self.session.get("https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/standard/gui/tree.jsp?selectId=9314&reset=true&forceLoad=false&scroll=0")
        response = self.session.get("https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/custom/modules/plannings/imagemap.jsp", params=params)
        # print(response.text)
        # response = self.session.post("https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/standard/gui/tree.jsp", data={"search": "2aa"})
        print(response.text)
        return 


RESOURCES = {
    "2AA": 9314
}

URL = "https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/imageEt"

PARAMETERS = {
    "identifier": "4f0ccc108e86a9d4b55dcd19950b59abw7601",
    "projectId": 13,
    "idPianoWeek": 18,
    "idPianoDay": "0,1,2,3,4,5,6",
    "idTree": 9314,
    "width": 793,
    "height": 851,
    "lunchName": "REPAS",
    "displayMode": 1057855,
    "showLoad": False,
    "ttl": 1733072846848,
    "displayConfId": 15
}

PARAMETERS = {
    "identifier": "4f0ccc108e86a9d4b55dcd19950b59abw7601",
    "projectId": 13,
    "idPianoWeek": 18,
    "idPianoDay": "0,1,2,3,4,5,6",
    "idTree": 9314,
    "width": 793,
    "height": 851,
    "lunchName": "REPAS",
    "displayMode": 1057855,
    "showLoad": False,
    "ttl": 1733072846848,
    "displayConfId": 15
}

# edt = EdtGrenobleINP()
# edt.get_identifier()

def get_identifier():
    opt = webdriver.FirefoxOptions()
    opt.headless = True

    driver = webdriver.Firefox(options=opt)
    driver.get("https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/standard/direct_planning.jsp")
    try:
        driver.implicitly_wait(2)
        driver.switch_to.frame("tree")

        # search a group that exists -> need to produce an image
        search_input = driver.find_element(By.CSS_SELECTOR, "input[name='search']")
        search_input.send_keys("2aa")
        search_input.send_keys(Keys.RETURN)

        driver.implicitly_wait(3)
        driver.switch_to.parent_frame()
        driver.switch_to.frame("et")

        image = driver.find_element(By.XPATH, "/html/body/img")
        image_url = image.get_attribute("src")

        print(image_url)
    finally:
        driver.quit()

    return image_url.split("identifier=")[1].split("&")[0]
