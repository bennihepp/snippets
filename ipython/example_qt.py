import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ipython_view_qt import *

#import platform
#if platform.system()=="Windows":
#    FONT = "Lucida Console 9"
#else:
#    FONT = "Luxi Mono 10"

app = QApplication(sys.argv)

#W = QWidget()
#W.resize(QSize(750,550))
#W.set_resizable(True)
#S = gtk.ScrolledWindow()
#S.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
V = IPythonView(allow_close=True)
V.resize(QSize(750,550))
#V.modify_font(pango.FontDescription(FONT))
#V.set_wrap_mode(gtk.WRAP_CHAR)
V.show()
#S.add(V)
#S.show()
#vbox = QVBoxLayout()
#vbox.addWidget(V)
#W.setLayout(vbox)
#W.add(S)
#W.show()

#W.connect('delete_event',lambda x,y:False)
#W.connect('destroy',lambda x:gtk.main_quit())
#W.connect('closed', close)
#W.connect('destroy', quit)

app.exec_()
V.close()
