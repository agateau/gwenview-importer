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
from PyKDE4.solid import *

from importdialog import ImportDialog


EXTENSIONS = [".jpg", ".jpeg", ".png", ".tif", ".tiff"]

DEFAULT_BASE_DST_FOLDER = "~/photos"


def pathFromUdi(udi):
    print udi


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


def main():
    app = QApplication(sys.argv)

    parser = OptionParser(usage="%prog <options>")
    parser.add_option("--udi", dest="udi",
                      help="Import from device whose udi is UDI", metavar="UDI")
    parser.add_option("--src", dest="src",
                      help="Import from folder PATH", metavar="PATH")
    parser.add_option("--base-dst", dest="baseDst", default=DEFAULT_BASE_DST_FOLDER,
                      help="Import to folder PATH/<year>/<event>", metavar="PATH")
    (options, args) = parser.parse_args()

    if not options.udi and not options.src:
        parser.print_help()
        return 1

    if options.udi:
        src = pathFromUdi(options.udi)
        if not src:
            print "Could not open device"
            return 2
    else:
        src = options.src

    baseDst = os.path.expanduser(options.baseDst)
    dlg = ImportDialog(KUrl(baseDst))
    if not dlg.exec_():
        return 0

    dstDirUrl = dlg.dstUrl()

    dir = unicode(dstDirUrl.path())
    if not os.path.exists(dir):
        os.makedirs(dir)

    urlList = listImages(src)
    for url in urlList:
        name = getNameForUrl(url)
        dstUrl = KUrl(dstDirUrl)
        dstUrl.addPath(name)
        job = KIO.copy(url, dstUrl)
        if not job.exec_():
            KMessageBox.information(i18n("<b>Transfer failed</b><br>%1", job.errorString()))
            return 0

    answer = KMessageBox.questionYesNo(
        None, i18n("Delete imported images from card?"),
        QString(),
        KStandardGuiItem.del_(),
        KStandardGuiItem.close())

    if answer == KMessageBox.Yes:
        job = KIO.del_(KUrl.List(urlList))
        job.exec_()

    os.execlp("gwenview", "gwenview", unicode(dstUrl.url()))

    return 0


if __name__=="__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
