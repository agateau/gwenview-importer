import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

from ui_importdialog import Ui_ImportDialog


class ImportDialog(KDialog):
    def __init__(self, dstUrl):
        KDialog.__init__(self)

        self.dstBaseUrl = KUrl(dstUrl)
        year = str(time.gmtime().tm_year)
        self.dstBaseUrl.addPath(year)

        # Destination
        widget = QWidget(self)
        self.ui = Ui_ImportDialog()
        self.ui.setupUi(widget)
        widget.layout().setMargin(0)
        self.setMainWidget(widget)
        self.showButtonSeparator(True)

        QObject.connect(self.ui.eventComboBox, SIGNAL("editTextChanged(QString)"), \
            self.updateDstLabel)

        self.ui.eventComboBox.setFocus()
        font = self.ui.dstLabel.font()
        font.setItalic(True)
        self.ui.dstLabel.setFont(font)
        self.updateDstLabel()


    def sizeHint(self):
        sh = KDialog.sizeHint(self)
        sh.setWidth(400)
        return sh


    def updateDstLabel(self):
        url = self.dstUrl()
        text = i18n("Pictures will be imported in:\n%1", url.pathOrUrl())
        self.ui.dstLabel.setText(text)
        self.adjustSize()


    def dstUrl(self):
        url = KUrl(self.dstBaseUrl)
        url.addPath(self.ui.eventComboBox.currentText())
        return url


# vi: ts=4 sw=4 et
