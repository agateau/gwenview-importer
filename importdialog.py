import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

from ui_progresspage import Ui_ProgressPage
from ui_importdialog import Ui_ImportDialog


class ImportDialog(KAssistantDialog):
    def __init__(self, dstUrl):
        KAssistantDialog.__init__(self)

        self.dstBaseUrl = KUrl(dstUrl)
        year = str(time.gmtime().tm_year)
        self.dstBaseUrl.addPath(year)

        # Destination
        self.destinationPage = QWidget(self)
        self.destinationUi = Ui_ImportDialog()
        self.destinationUi.setupUi(self.destinationPage)
        self.destinationPage.layout().setMargin(0)
        self.destinationPageItem = self.addPage(self.destinationPage, i18n("Destination"))

        # Progress
        self.progressPage = QWidget(self)
        self.progressUi = Ui_ProgressPage()
        self.progressUi.setupUi(self.progressPage)
        self.progressPage.layout().setMargin(0)
        self.progressPageItem = self.addPage(self.progressPage, i18n("Progress"))

        QObject.connect(self.destinationUi.eventComboBox, SIGNAL("editTextChanged(QString)"), \
            self.updateDstLabel)

        self.destinationUi.eventComboBox.setFocus()
        self.updateDstLabel()


    def showProgressPage(self, count):
        self.progressUi.progressBar.setRange(0, count)
        self.progressUi.progressBar.setValue(0)
        self.setCurrentPage(self.progressPageItem)


    def increaseProgressValue(self):
        bar = self.progressUi.progressBar
        bar.setValue(bar.value() + 1)


    def sizeHint(self):
        sh = KDialog.sizeHint(self)
        sh.setWidth(400)
        return sh


    def updateDstLabel(self):
        url = self.dstUrl()
        self.destinationUi.dstLabel.setText(url.pathOrUrl())


    def dstUrl(self):
        url = KUrl(self.dstBaseUrl)
        url.addPath(self.destinationUi.eventComboBox.currentText())
        return url


# vi: ts=4 sw=4 et
