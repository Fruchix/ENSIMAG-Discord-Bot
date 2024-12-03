from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from enum import Enum


class DriverEnum(Enum):
    CHROME = "chrome"


class DriverFactory:
    @staticmethod
    def build(driver: DriverEnum, executable_path: str, options: list[str] = []):
        if driver == DriverEnum.CHROME:
            return ChromeDriver(executable_path, options).driver
        else:
            raise Exception(f"Driver {driver} not supported")


class ChromeDriver:
    def __init__(self, executable_path: str, options: list[str] = []) -> None:
        self.service = ChromeService(executable_path=executable_path)

        self.options = ChromeOptions()
        for option in options:
            self.options.add_argument(option)

        self.driver = webdriver.Chrome(service=self.service, options=self.options)
