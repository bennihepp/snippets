#!/usr/bin/python
'''
Provides IPython console widget.

@author: Eitan Isaacson
@organization: IBM Corporation
@copyright: Copyright (c) 2007 IBM Corporation
@license: BSD

All rights reserved. This program and the accompanying materials are made 
available under the terms of the BSD which accompanies this distribution, and 
is available at U{http://www.opensource.org/licenses/bsd-license.php}
'''
# this file is a modified version of source code from the Accerciser project
# http://live.gnome.org/accerciser

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import re
from StringIO import StringIO

from ipshell import IterableIPShell

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

    def __init__(self, parent=None):
        '''
        Initialize console view.
        '''
        QTextEdit.__init__(self, parent)
        self.prompt_len = 0
        self.setFontFamily('monospace')
        #self.modify_font(pango.FontDescription('Mono'))
        #self.set_cursor_visible(True)
        #self.setTextInteractionFlags(Qt.TextSelectableByMouse or Qt.TextSelectableByKeyboard)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_document = self.document()
        self.text_cursor = QTextCursor(self.text_document)
        self.line_start = QTextCursor(self.text_document)
        #self.mark = self.text_buffer.create_mark('scroll_mark', 
        #                                         self.text_buffer.get_end_iter(),
        #                                         False)
        #for code in ANSI_COLORS:
        #    self.text_buffer.create_tag(code,
        #                                foreground=ANSI_COLORS[code], 
        #                                weight=700)
        #self.text_buffer.create_tag('0')
        #self.text_buffer.create_tag('notouch', editable=False)
        self.color_pat = re.compile('\x01?\x1b\[(.*?)m\x02?')
        self.line_start = QTextCursor(self.text_document)
        self.line_start.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        #self.line_start = \
        #    self.text_buffer.create_mark('line_start', 
        #                                 self.text_buffer.get_end_iter(), True)
        #self.connect('key-press-event', self.onKeyPress)

    def closeEvent(self, event):
        event.accept()
        self.emit(SIGNAL('closed'))

    def write(self, text):
        self._write(text)
        #gobject.idle_add(self._write, text, editable)

    def _write(self, text):
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
        #start_mark = self.text_buffer.create_mark(None, 
        #                                          self.text_buffer.get_end_iter(), 
        #                                          True)
        #self.text_buffer.insert(self.text_buffer.get_end_iter(), segment)
        #self.text_cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        self.textCursor().insertText(segment)
        text_len += len(segment)

        if segments:
            ansi_tags = self.color_pat.findall(text)
            for tag in ansi_tags:
                i = segments.index(tag)
                #self.text_cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
                if tag in ANSI_COLORS:
                    self.setTextColor(QColor(ANSI_COLORS[tag]))
                self.textCursor().insertText(segments[i+1])
                #self.text_buffer.insert_with_tags_by_name(self.text_buffer.get_end_iter(),
                #                                          segments[i+1], tag)
                text_len += len(segments[i+1])
                segments.pop(i)
        #if not editable:
        #    self.text_buffer.apply_tag_by_name('notouch',
        #                                       self.text_buffer.get_iter_at_mark(start_mark),
        #                                       self.text_buffer.get_end_iter())
        #self.text_buffer.delete_mark(start_mark)
        #self.scroll_mark_onscreen(self.mark)
        #self.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        #self.setTextCursor(self.text_cursor)
        self.ensureCursorVisible()

        return text_len

    def showPrompt(self, prompt):
        self._showPrompt(prompt)
        #gobject.idle_add(self._showPrompt, prompt)

    def _showPrompt(self, prompt):
        '''
        Prints prompt at start of line.

        @param prompt: Prompt to print.
        @type prompt: string
        '''
        self.prompt_len = self._write(prompt)
        self.line_start.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        self.line_start.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
        self.line_start.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, self.prompt_len)

    def changeLine(self, text):
        self._changeLine(text)
        #gobject.idle_add(self._changeLine, text)

    def _changeLine(self, text):
        '''
        Replace currently entered command line with given text.

        @param text: Text to use as replacement.
        @type text: string
        '''
        self.text_cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        text_cursor = self.textCursor()
        text_cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        text_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, self.prompt_len)
        text_cursor.removeSelectedText()
        #text_cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        self.setTextCursor(text_cursor)
        #self.line_start.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        #self.line_start.removeSelectedText()
        #self.line_start.movePosition(QTextCursor.PreviousCharacter, QTextCursor.MoveAnchor)
        #iter = self.text_buffer.get_iter_at_mark(self.line_start)
        #iter.forward_to_line_end()
        #self.text_buffer.delete(self.text_buffer.get_iter_at_mark(self.line_start), iter)
        self.setTextColor(QColor('black'))
        self._write(text)

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
        self._showReturned(text)
        #gobject.idle_add(self._showReturned, text)

    def _showReturned(self, text):
        '''
        Show returned text from last command and print new prompt.

        @param text: Text to show.
        @type text: string
        '''
        #iter = self.text_buffer.get_iter_at_mark(self.line_start)
        #iter.forward_to_line_end()
        #self.text_buffer.apply_tag_by_name(
        #    'notouch', 
        #    self.text_buffer.get_iter_at_mark(self.line_start),
        #    iter)
        self._write('\n'+text)
        if text:
            self._write('\n')
        self._showPrompt(self.prompt)
        #self.text_buffer.move_mark(self.line_start,self.text_buffer.get_end_iter())
        #self.text_buffer.place_cursor(self.text_buffer.get_end_iter())

    def keyPressEvent(self, event):
        '''
        Key press callback used for correcting behavior for console-like 
        interfaces. For example 'home' should go to prompt, not to begining of
        line.

        @param event: Event object
        @type event: gtk.gdk.Event

        @return: Return True if event should not trickle.
        @rtype: boolean
        '''
        #insert_mark = self.text_buffer.get_insert()
        #insert_iter = self.text_buffer.get_iter_at_mark(insert_mark)
        #selection_mark = self.text_buffer.get_selection_bound()
        #selection_iter = self.text_buffer.get_iter_at_mark(selection_mark)
        #start_iter = self.text_buffer.get_iter_at_mark(self.line_start)

        mode = QTextCursor.MoveAnchor
        if event.modifiers() & Qt.ShiftModifier:
            mode = QTextCursor.KeepAnchor

        #if event.text().length() > 0 and QChar(event.text()[0]).isPrint():
        #    self.write(event.text())
        if event.key() == Qt.Key_Home:
            if event.modifiers() & Qt.ControlModifier or event.modifiers() & Qt.AltModifier:
                pass
            else:
                self.moveCursor(QTextCursor.StartOfLine, mode)
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.NextCharacter, mode, self.prompt_len)
                self.setTextCursor(cursor)
                #self.text_cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
                #self.text_buffer.move_mark(insert_mark, start_iter)
                return
        elif event.key() == Qt.Key_End:
            if event.modifiers() & Qt.ControlModifier or event.modifiers() & Qt.AltModifier:
                pass
            else:
                self.moveCursor(QTextCursor.EndOfLine, mode)
                #self.text_cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
                #self.text_buffer.move_mark(insert_mark, start_iter)
                return
        #elif event.key() == Qt.Key_Left:
        #    if self.textCursor().position() > self.line_start.position():
        #        self.moveCursor(QTextCursor.PreviousCharacter, mode)
        #    return
        #elif event.key() == Qt.Key_Right:
        #    self.moveCursor(QTextCursor.NextCharacter, mode)
        #    return
            #insert_iter.backward_cursor_position()
            #if not insert_iter.editable(True):
            #    return True
        #elif not event.string:
            #pass
        #elif start_iter.compare(insert_iter) <= 0 and \
             #start_iter.compare(selection_iter) <= 0:
            #pass
        #elif start_iter.compare(insert_iter) > 0 and \
             #start_iter.compare(selection_iter) > 0:
            #self.text_buffer.place_cursor(start_iter)
        #elif insert_iter.compare(selection_iter) < 0:
            #self.text_buffer.move_mark(insert_mark, start_iter)
        #elif insert_iter.compare(selection_iter) > 0:
            #self.text_buffer.move_mark(selection_mark, start_iter)             

        rv = self.keyPressEventExtend(event)

        if not rv:
            QTextEdit.keyPressEvent(self, event)

    def keyPressEventExtend(self, event):
        '''
        For some reason we can't extend onKeyPress directly (bug #500900).
        '''
        return False

class IPythonView(ConsoleView, IterableIPShell):
    '''
    Sub-class of both modified IPython shell and L{ConsoleView} this makes
    a GTK+ IPython console.
    '''
    def __init__(self, exit_func=None):
        '''
        Initialize. Redirect I/O to console.
        '''
        ConsoleView.__init__(self)
        self.cout = StringIO()
        IterableIPShell.__init__(self, cout=self.cout,cerr=self.cout, 
                                 input_func=self.raw_input, exit_func=exit_func)
#    self.connect('key_press_event', self.keyPress)
        self.execute()
        self.cout.truncate(0)
        self.showPrompt(self.prompt)
        self.interrupt = False

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

        @param widget: Widget that key press occured in.
        @type widget: gtk.Widget
        @param event: Event object.
        @type event: gtk.gdk.Event

        @return: True if event should not trickle.
        @rtype: boolean
        '''
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_C:
            if event.modifiers() & Qt.ShiftModifier:
                self.interrupt = True
                self._processLine()
                return True
            else:
                return False
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Q:
            self.close()
            return True
        elif event.key() == Qt.Key_Return:
            self.moveCursor(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            self._processLine()
            return True
        elif event.key() == Qt.Key_Up:
            self.moveCursor(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            self.changeLine(self.historyBack())
            return True
        elif event.key() == Qt.Key_Down:
            self.moveCursor(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            self.changeLine(self.historyForward())
            return True
        elif event.key() == Qt.Key_Tab:
            if not self.getCurrentLine().strip():
                return False
            completed, possibilities = self.complete(self.getCurrentLine())
            if len(possibilities) > 1:
                slice = self.getCurrentLine()
                self.write('\n')
                for symbol in possibilities:
                    self.write(symbol+'\n')
                self.showPrompt(self.prompt)
            self.changeLine(completed or slice)
            return True
        return False

    def _processLine(self):
        '''
        Process current command line.
        '''
        self.history_pos = 0
        self.execute()
        rv = self.cout.getvalue()
        if rv: rv = rv.strip('\n')
        self.showReturned(rv)
        self.cout.truncate(0)
