# -*- coding: utf-8 -*-

"""
Provides a interactive python session for PyQt.

@author: Benjamin Hepp
@copyright: Copyright (c) 2011 Benjamin Hepp
@license: BSD

All rights reserved. This program and the accompanying materials are made 
available under the terms of the FreeBSD which accompanies this distribution,
and is available at U{http://www.opensource.org/licenses/BSD-2-Clause}
"""
# this file is a modified version of source code from the Accerciser project
# http://live.gnome.org/accerciser

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import re
from cStringIO import StringIO

from pyqt.utils import PyQtSignalMapper

try:
    from ipshell import IterableIPShell
except:
    from pshell import IterablePShell as IterableIPShell

# Mapping of terminal colors to X11 names.
ANSI_COLORS =  {'0' : 'black',
                '1' : 'white',
                '0;30': 'black',
                '0;31': 'red',
                '0;32': 'green',
                '0;33': 'darkRed',
                '0;34': 'blue',
                '0;35': 'magenta',
                '0;36': 'cyan',
                '0;37': 'lightGray',
                '1;30': 'darkGray',
                '1;31': 'darkRed',
                '1;32': 'green',
                '1;33': 'yellow',
                '1;34': 'blue',
                '1;35': 'magenta',
                '1;36': 'darkCyan',
                '1;37': 'white'}

class ConsoleView(QTextEdit):
    '''
    Specialized text view for console-like workflow.

    @ivar text_document: Widget's text document.
    @type text_document: QTextDocument
    @ivar color_pat: Regex of terminal color pattern
    @type color_pat: _sre.SRE_Pattern
    @ivar mark: Scroll mark for automatic scrolling on input.
    @type mark: gtk.TextMark
    @ivar line_start: Start of command line mark.
    @type line_start: gtk.TextMark
    '''

    __pyqtSignals__ = ('closed',)

    def __init__(self, title, parent=None):
        '''
        Initialize console view.
        '''
        QTextEdit.__init__(self, parent)
        self.setWindowTitle(title)
        self.prompt_len = 0
        self.fixed_position = 0
        self.setFontFamily('monospace')
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_document = self.document()
        self.color_pat = re.compile('\x01?\x1b\[(.*?)m\x02?')
        self.qblack = QColor('black')
        def make_action(text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal='triggered()'):
            action = QAction(text, self)
            if icon is not None:
                action.setIcon(QIcon(icon))
            if shortcut is not None:
                action.setShortcut(shortcut)
            if tip is not None:
                action.setToolTip(tip)
                action.setStatusTip(tip)
            if slot is not None:
                self.connect(action, SIGNAL(signal), slot)
            if checkable:
                action.setCheckable(True)
            return action
        sm = PyQtSignalMapper(self)
        for text, shortcut in zip(*[('Cut', 'Copy', 'Paste', 'Select All', 'Clear'),
                                   ('Ctrl+X', 'Ctrl+Alt+C', 'Ctrl+V', 'Ctrl+W', 'Ctrl+L')]):
            action = make_action(text, slot=sm.map, shortcut=shortcut)
            self.addAction(action)
            sm.setMapping(action, text)
        sm.connect(sm, SIGNAL('mapped'), self.actionSlot)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def actionSlot(self, text):
        text = str(text)
        qtype = QEvent.KeyPress
        modifiers = Qt.ControlModifier
        if text == 'Cut':
            key, text = Qt.Key_X, 'x'
        elif text == 'Copy':
            modifiers = modifiers | Qt.ShiftModifier
            key, text = Qt.Key_C, 'c'
        elif text == 'Paste':
            key, text = Qt.Key_V, 'v'
        elif text == 'Select All':
            key, text = Qt.Key_A, 'a'
        elif text == 'Clear':
            key, text = Qt.Key_L, 'l'
        else:
            raise Exception('Unknown object ID:', text)
        keyEvent = QKeyEvent(qtype, key, modifiers, text)
        self.keyPressEvent(keyEvent)

    def closeEvent(self, event):
        event.accept()
        self.emit(SIGNAL('closed'))

    def clear(self):        
        line = self.getCurrentLine()
        self.setPlainText('')
        self.showPrompt(self.prompt)
        self.write(line)

    def write(self, text):
        '''
        Write given text to buffer.

        @param text: Text to append.
        @type text: string
        @param editable: If true, added text is editable.
        @type editable: boolean
        '''
        text_len = 0

        segments = self.color_pat.split(text)
        segment = segments.pop(0)
        self.textCursor().insertText(segment)
        text_len += len(segment)

        if segments:
            ansi_tags = self.color_pat.findall(text)
            for tag in ansi_tags:
                i = segments.index(tag)
                if tag in ANSI_COLORS:
                    self.setTextColor(QColor(ANSI_COLORS[tag]))
                else:
                    self.setTextColor(self.qblack)
                self.textCursor().insertText(segments[i+1])
                text_len += len(segments[i+1])
                segments.pop(i)
        self.ensureCursorVisible()

        return text_len

    def showPrompt(self, prompt):
        '''
        Prints prompt at start of line.

        @param prompt: Prompt to print.
        @type prompt: string
        '''
        self.prompt_len = self.write(prompt)
        line_start = self.textCursor()
        line_start.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        line_start.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
        self.fixed_position = line_start.position() + self.prompt_len

    def changeLine(self, text):
        '''
        Replace currently entered command line with given text.

        @param text: Text to use as replacement.
        @type text: string
        '''
        text_cursor = self.textCursor()
        text_cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        text_cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        text_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, self.prompt_len)
        text_cursor.removeSelectedText()
        self.setTextCursor(text_cursor)
        self.setTextColor(self.qblack)
        self.write(text)

    def getCurrentLine(self):
        '''
        Get text in current command line.

        @return: Text of current command line.
        @rtype: string
        '''
        text_cursor = self.textCursor()
        text_cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        text_cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        text_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, self.prompt_len)
        rv = str(text_cursor.selectedText())
        return rv

    def showReturned(self, text):
        '''
        Show returned text from last command and print new prompt.

        @param text: Text to show.
        @type text: string
        '''
        self.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        self.write('\n'+text)
        if text:
            self.write('\n')
        self.showPrompt(self.prompt)

    def gotoEnd(self, resetColor=True):
        self.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        self.setTextColor(self.qblack)

    def canInsertFromMimeData(self, source):
        if source.hasText():
            return True
        else:
            return False

    def insertFromMimeData(self, source):
        if source.hasText():
            text = source.text()
            self.gotoEnd()
            self.write(text)

    def keyPressEvent(self, event):
        '''
        Key press callback used for correcting behavior for console-like 
        interfaces. For example 'home' should go to prompt, not to begining of
        line.

        @return: Return True if event should not trickle.
        @rtype: boolean
        '''
        pass_up = False

        mode = QTextCursor.MoveAnchor
        if event.modifiers() & Qt.ShiftModifier:
            mode = QTextCursor.KeepAnchor

        if event.key() == Qt.Key_Home:
            if event.modifiers() & Qt.ControlModifier or event.modifiers() & Qt.AltModifier:
                pass
            else:
                self.moveCursor(QTextCursor.StartOfLine, mode)
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.NextCharacter, mode, self.prompt_len)
                self.setTextCursor(cursor)
                return
        elif event.key() == Qt.Key_End:
            if event.modifiers() & Qt.ControlModifier or event.modifiers() & Qt.AltModifier:
                pass
            else:
                self.moveCursor(QTextCursor.EndOfLine, mode)
                return
        elif event.modifiers() == (Qt.ShiftModifier | Qt.ControlModifier) and event.key() == Qt.Key_C:
            newEvent = QKeyEvent(event.type(), event.key(),
                                 event.modifiers() & (~Qt.ShiftModifier),
                                 event.text())
            event = newEvent
            pass_up = True
        #elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_X:
        #    tc = self.textCursor()
        #    if min(tc.position(), tc.anchor()) >= self.fixed_position:
        #        pass_up = True
        #    else:
        #        return
        #elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_A:
        #    pass_up = True
        #elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
        #    self.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        #    self.setTextColor(QColor('black'))
        #    pass_up = True
        elif event.key() == Qt.Key_Control or event.key() == Qt.Key_Shift \
             or event.key() == Qt.Key_Meta or event.key() == Qt.Key_Alt:
            pass_up = True
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_L:
            self.clear()
            return

        if pass_up:
            QTextEdit.keyPressEvent(self, event)
            return

        pass_up = not self.keyPressEventExtend(event)

        if pass_up:
            tc = self.textCursor()
            pos = tc.position()
            anc = tc.anchor()
            if min(pos, anc) < self.fixed_position:
                if max(pos, anc) < self.fixed_position:
                    self.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
                    #self.setTextColor(QColor('black'))
                else:
                    if pos < anc:
                        tc.setPosition(self.fixed_position, QTextCursor.KeepAnchor)
                    else:
                        tc.setPosition(self.fixed_position, QTextCursor.MoveAnchor)
                        tc.setPosition(pos, QTextCursor.KeepAnchor)
                    self.setTextCursor(tc)
            self.setTextColor(self.qblack)
            QTextEdit.keyPressEvent(self, event)

    def keyPressEventExtend(self, event):
        '''
        For some reason we can't extend onKeyPress directly (bug #500900).
        '''
        return False

class IPythonMdiView(QMdiSubWindow):
    def __init__(self, user_ns=None, user_global_ns=None, allow_close=False,
                 title='Interactive Python Session', parent=None):
        QMdiSubWindow.__init__(self, parent)
        self.ipython_view = IPythonView(user_ns, user_global_ns, allow_close, title, self)
        self.setWidget(self.ipython_view)
        self.setAttribute(Qt.WA_DeleteOnClose)

class IPythonView(ConsoleView, IterableIPShell):
    '''
    Sub-class of both modified IPython shell and L{ConsoleView} this makes
    a GTK+ IPython console.
    '''
    def __init__(self, user_ns=None, user_global_ns=None, allow_close=False,
                 title='Interactive Python Session', parent=None):
        '''
        Initialize. Redirect I/O to console.
        '''
        ConsoleView.__init__(self, title, parent)
        self.cout = StringIO()
        if allow_close:
            exit_func = self.close
        else:
            exit_func = None
        self.allow_close = allow_close
        self.interrupt = False
        IterableIPShell.__init__(self, user_ns=user_ns, user_global_ns=user_global_ns,
                                 cout=self.cout,cerr=self.cout, 
                                 input_func=self.raw_input, exit_func=self.close)
        self.execute()
        self.cout.truncate(0)
        self.showPrompt(self.prompt)

    def raw_input(self, prompt=''):
        '''
        Custom raw_input() replacement. Get's current line from console buffer.

        @param prompt: Prompt to print. Here for compatability as replacement.
        @type prompt: string

        @return: The current command line text.
        @rtype: string
        '''
        if self.interrupt:
            self.interrupt = False
            raise KeyboardInterrupt
        return self.getCurrentLine()

    def keyPressEventExtend(self, event):
        '''
        Key press callback with plenty of shell goodness, like history, 
        autocompletions, etc.

        @return: True if event should not trickle.
        @rtype: boolean
        '''
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_C:
            self.interrupt = True
            self.processLine()
            return True
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Q:
            if self.allow_close:
                self.close()
            return True
        elif event.key() == Qt.Key_Return:
            self.processLine()
            return True
        elif event.key() == Qt.Key_Up:
            self.changeLine(self.historyBack())
            return True
        elif event.key() == Qt.Key_Left:
            p = self.textCursor().position()
            return p <= self.fixed_position
        elif event.key() == Qt.Key_Down:
            self.changeLine(self.historyForward())
            return True
        elif event.key() == Qt.Key_Tab:
            if not self.getCurrentLine().strip():
                self.gotoEnd()
                self.write(4*' ')
            else:
                completed, possibilities = self.complete(self.getCurrentLine())
                if len(possibilities) > 1:
                    slice = self.getCurrentLine()
                    self.gotoEnd()
                    self.write('\n')
                    for symbol in possibilities:
                        self.write(symbol+'\n')
                    self.showPrompt(self.prompt)
                self.changeLine(completed or slice)
            return True
        return False

    def processLine(self):
        '''
        Process current command line.
        '''
        self.history_pos = 0
        self.execute()
        rv = self.cout.getvalue()
        if rv: rv = rv.strip('\n')
        self.showReturned(rv)
        self.cout.truncate(0)
