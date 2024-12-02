
from src.edt.edt_grenoble_inp import EdtGrenobleInpClient, EdtGrenobleInpResources

edt = EdtGrenobleInpClient()

edt.download_edt(EdtGrenobleInpResources.Group2AA, 1)
edt.download_edt(EdtGrenobleInpResources.Group2AA, -1)
edt.download_edt(EdtGrenobleInpResources.Group2AA, 2)
edt.download_edt(EdtGrenobleInpResources.Group2AA, 3)