# -*- coding: utf-8 -*-

"""
Provides some helpers for PyQt related stuff.

@author: Benjamin Hepp
@copyright: Copyright (c) 2011 Benjamin Hepp
@license: BSD

All rights reserved. This program and the accompanying materials are made 
available under the terms of the FreeBSD which accompanies this distribution,
and is available at U{http://www.opensource.org/licenses/BSD-2-Clause}
"""


from PyQt4.QtCore import QObject, SIGNAL
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *

class PyQtSignalMapper(QObject):

    __pyqtSignals__ = ('mapped',)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.__mapping = {}
    def setMapping(self, obj, value):
        self.__mapping[obj] = value
    def removeMapping(self, obj):
        del self.__mapping[obj]
    def mapping(self, obj):
        return self.__mapping[obj]
    def map(self, obj=None):
        if obj is None:
            self.map(self.sender())
        else:
            self.emit(SIGNAL('mapped'), self.mapping(obj))
