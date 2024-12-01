from time import sleep
import requests

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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import os

# Function to perform the search and fetch the image
def search_and_fetch_image(search_query, url, output_folder="data"):
    # Initialize WebDriver (replace with the appropriate driver for your browser)
    opt = webdriver.ChromeOptions()
    opt.headless = True

    driver = webdriver.Chrome(options=opt)  # Ensure you have ChromeDriver installed
    driver.get(url)

    try:
        # Locate the input field and enter the search query
        frame = driver.find_element(By.XPATH, "/html/frameset/frameset/frame")
        driver.switch_to.frame(frame)

        search_input = driver.find_element(By.CSS_SELECTOR, "input[name='search']")
        search_input.send_keys(search_query)
        search_input.send_keys(Keys.RETURN)

        driver.implicitly_wait(5)

        driver.switch_to.parent_frame()

        frame = driver.find_element(By.XPATH, "/html/frameset/frameset[2]/frame")
        driver.switch_to.frame(frame)

        image = driver.find_element(By.XPATH, "/html/body/img")
        image_url = image.get_attribute("src")

        if not image_url:
            raise ValueError("No image URL found for the given selector.")

        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()

        # Save the image locally
        os.makedirs(output_folder, exist_ok=True)
        file_name = f"{output_folder}/{search_query.replace(' ', '_')}.jpg"
        with open(file_name, "wb") as file:
            file.write(response.content)

        print(f"Image saved successfully at {file_name}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

# Example usage
search_query = "2aa"
search_and_fetch_image(
    search_query=search_query,
    url="https://edt.grenoble-inp.fr/2024-2025/exterieur/jsp/standard/direct_planning.jsp",  # Replace with the target URL
)
