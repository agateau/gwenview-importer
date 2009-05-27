#!/usr/bin/env python
import os
import os.path
import sys
from optparse import OptionParser

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *
from PyKDE4.kio import *

from importdialog import ImportDialog


EXTENSIONS = [".jpg", ".jpeg", ".png", ".tif", ".tiff"]

DEFAULT_BASE_DST_FOLDER = "~/photos"


def listImages(path):
    urlList = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1].lower() in EXTENSIONS:
                url = KUrl.fromPath(os.path.join(root, file))
                urlList.append(url)
    return urlList

# for x in os.listdir("."): name=main.getNameForUrl(KUrl.fromPath(os.getcwd() + '/' + x)); os.rename(x,name)


def getNameForUrl(url):
    path = unicode(url.path())
    dateTime = getShootingDateTimeForUrl(url)
    if not dateTime:
        stamp = int(os.stat(path).st_mtime)
        dateTime = KDateTime(QDateTime.fromTime_t(stamp))

    name = dateTime.toString()
    name.replace(":", "-")
    # Get rid of timezone
    name = name.section("+", 0, 0)
    ext = os.path.splitext(path)[1].lower()
    return unicode(name) + ext


def getShootingDateTimeForUrl(url):
    info = KFileMetaInfo(url)
    if not info.isValid():
        return None
    mii = info.item("http://www.semanticdesktop.org/ontologies/2007/01/19/nie#contentCreated");
    dt = KDateTime(mii.value().toDateTime())
    if dt.isValid():
        return dt
    else:
        return None


class Controller(QObject):
    def __init__(self, src, baseDst):
        QObject.__init__(self)
        self.src = src
        self.dlg = ImportDialog(KUrl(baseDst))


    def run(self):
        if not self.dlg.exec_():
            return False

        self.dstDirUrl = self.dlg.dstUrl()

        self.progressDlg = KProgressDialog()
        self.progressDlg.setLabelText(i18n("Initializing..."))
        self.progressDlg.setMinimumDuration(0)
        qApp.processEvents()

        dir = unicode(self.dstDirUrl.path())
        if not os.path.exists(dir):
            os.makedirs(dir)

        self.progressDlg.setLabelText(i18n("Importing pictures..."))
        self.urlList = listImages(self.src)
        if not self.urlList:
            KMessageBox.information(None, i18n("No picture to import."))
            return False
        self.progressDlg.progressBar().setRange(0, len(self.urlList))
        self.copyOneUrl()
        return True


    def copyOneUrl(self):
        url = self.urlList.pop()
        name = getNameForUrl(url)
        dstUrl = KUrl(self.dstDirUrl)
        dstUrl.addPath(name)
        job = KIO.copy(url, dstUrl, KIO.HideProgressInfo)
        QObject.connect(job, SIGNAL("result(KJob*)"), self.slotJobResult)


    def slotJobResult(self, job):
        if job.error() != 0:
            job.uiDelegate().showErrorMessage()
            self.progressDlg.close()
            return

        bar = self.progressDlg.progressBar()
        bar.setValue(bar.value() + 1)
        if self.urlList:
            self.copyOneUrl()
        else:
            self.progressDlg.close()
            self.deleteFromCard()


    def deleteFromCard(self):
        answer = KMessageBox.questionYesNo(
            None, i18n("Pictures have been imported. Delete them from card?"),
            QString(),
            KStandardGuiItem.del_(),
            KStandardGuiItem.close())

        if answer == KMessageBox.Yes:
            job = KIO.del_(KUrl.List(urlList))
            job.exec_()

        os.execlp("gwenview", "gwenview", unicode(self.dstDirUrl.url()))


def main():
    app = QApplication(sys.argv)

    parser = OptionParser(usage="%prog <options>")
    parser.add_option("--src", dest="src",
                      help="Import from folder PATH", metavar="PATH")
    parser.add_option("--base-dst", dest="baseDst", default=DEFAULT_BASE_DST_FOLDER,
                      help="Import to folder PATH/<year>/<event>", metavar="PATH")
    (options, args) = parser.parse_args()

    if not options.src:
        parser.print_help()
        return 1

    src = options.src

    baseDst = os.path.expanduser(options.baseDst)
    controller = Controller(src, baseDst)
    if not controller.run():
        return 1
    app.exec_()
    return 0


if __name__=="__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
