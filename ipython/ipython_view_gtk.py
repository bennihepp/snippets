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

import gtk, gobject
import re
import pango
from StringIO import StringIO

from ipshell import IterableIPShell

# Mapping of terminal colors to X11 names.
ANSI_COLORS =  {'0;30': 'Black',
                '0;31': 'Red',
                '0;32': 'Green',
                '0;33': 'Brown',
                '0;34': 'Blue',
                '0;35': 'Purple',
                '0;36': 'Cyan',
                '0;37': 'LightGray',
                '1;30': 'DarkGray',
                '1;31': 'DarkRed',
                '1;32': 'SeaGreen',
                '1;33': 'Yellow',
                '1;34': 'LightBlue',
                '1;35': 'MediumPurple',
                '1;36': 'LightCyan',
                '1;37': 'White'}

class ConsoleView(gtk.TextView):
    '''
    Specialized text view for console-like workflow.

    @ivar text_buffer: Widget's text buffer.
    @type text_buffer: gtk.TextBuffer
    @ivar color_pat: Regex of terminal color pattern
    @type color_pat: _sre.SRE_Pattern
    @ivar mark: Scroll mark for automatic scrolling on input.
    @type mark: gtk.TextMark
    @ivar line_start: Start of command line mark.
    @type line_start: gtk.TextMark
    '''
    def __init__(self):
        '''
        Initialize console view.
        '''
        gtk.TextView.__init__(self)
        self.modify_font(pango.FontDescription('Mono'))
        self.set_cursor_visible(True)
        self.text_buffer = self.get_buffer()
        self.mark = self.text_buffer.create_mark('scroll_mark', 
                                                 self.text_buffer.get_end_iter(),
                                                 False)
        for code in ANSI_COLORS:
            self.text_buffer.create_tag(code, 
                                        foreground=ANSI_COLORS[code], 
                                        weight=700)
        self.text_buffer.create_tag('0')
        self.text_buffer.create_tag('notouch', editable=False)
        self.color_pat = re.compile('\x01?\x1b\[(.*?)m\x02?')
        self.line_start = \
            self.text_buffer.create_mark('line_start', 
                                         self.text_buffer.get_end_iter(), True)
        self.connect('key-press-event', self.onKeyPress)

    def write(self, text, editable=False):
        gobject.idle_add(self._write, text, editable)

    def _write(self, text, editable=False):
        '''
        Write given text to buffer.

        @param text: Text to append.
        @type text: string
        @param editable: If true, added text is editable.
        @type editable: boolean
        '''
        segments = self.color_pat.split(text)
        segment = segments.pop(0)
        start_mark = self.text_buffer.create_mark(None, 
                                                  self.text_buffer.get_end_iter(), 
                                                  True)
        self.text_buffer.insert(self.text_buffer.get_end_iter(), segment)

        if segments:
            ansi_tags = self.color_pat.findall(text)
            for tag in ansi_tags:
                i = segments.index(tag)
                self.text_buffer.insert_with_tags_by_name(self.text_buffer.get_end_iter(),
                                                          segments[i+1], tag)
                segments.pop(i)
        if not editable:
            self.text_buffer.apply_tag_by_name('notouch',
                                               self.text_buffer.get_iter_at_mark(start_mark),
                                               self.text_buffer.get_end_iter())
        self.text_buffer.delete_mark(start_mark)
        self.scroll_mark_onscreen(self.mark)


    def showPrompt(self, prompt):
        gobject.idle_add(self._showPrompt, prompt)

    def _showPrompt(self, prompt):
        '''
        Prints prompt at start of line.

        @param prompt: Prompt to print.
        @type prompt: string
        '''
        self._write(prompt)
        self.text_buffer.move_mark(self.line_start,
                                   self.text_buffer.get_end_iter())

    def changeLine(self, text):
        gobject.idle_add(self._changeLine, text)

    def _changeLine(self, text):
        '''
        Replace currently entered command line with given text.

        @param text: Text to use as replacement.
        @type text: string
        '''
        iter = self.text_buffer.get_iter_at_mark(self.line_start)
        iter.forward_to_line_end()
        self.text_buffer.delete(self.text_buffer.get_iter_at_mark(self.line_start), iter)
        self._write(text, True)

    def getCurrentLine(self):
        '''
        Get text in current command line.

        @return: Text of current command line.
        @rtype: string
        '''
        rv = self.text_buffer.get_slice(
            self.text_buffer.get_iter_at_mark(self.line_start),
            self.text_buffer.get_end_iter(), False)
        return rv

    def showReturned(self, text):
        gobject.idle_add(self._showReturned, text)

    def _showReturned(self, text):
        '''
        Show returned text from last command and print new prompt.

        @param text: Text to show.
        @type text: string
        '''
        iter = self.text_buffer.get_iter_at_mark(self.line_start)
        iter.forward_to_line_end()
        self.text_buffer.apply_tag_by_name(
            'notouch', 
            self.text_buffer.get_iter_at_mark(self.line_start),
            iter)
        self._write('\n'+text)
        if text:
            self._write('\n')
        self._showPrompt(self.prompt)
        self.text_buffer.move_mark(self.line_start,self.text_buffer.get_end_iter())
        self.text_buffer.place_cursor(self.text_buffer.get_end_iter())

    def onKeyPress(self, widget, event):
        '''
        Key press callback used for correcting behavior for console-like 
        interfaces. For example 'home' should go to prompt, not to begining of
        line.

        @param widget: Widget that key press accored in.
        @type widget: gtk.Widget
        @param event: Event object
        @type event: gtk.gdk.Event

        @return: Return True if event should not trickle.
        @rtype: boolean
        '''
        insert_mark = self.text_buffer.get_insert()
        insert_iter = self.text_buffer.get_iter_at_mark(insert_mark)
        selection_mark = self.text_buffer.get_selection_bound()
        selection_iter = self.text_buffer.get_iter_at_mark(selection_mark)
        start_iter = self.text_buffer.get_iter_at_mark(self.line_start)
        if event.keyval == gtk.keysyms.Home:
            if event.state & gtk.gdk.CONTROL_MASK or event.state & gtk.gdk.MOD1_MASK:
                pass
            elif event.state & gtk.gdk.SHIFT_MASK:
                self.text_buffer.move_mark(insert_mark, start_iter)
                return True
            else:
                self.text_buffer.place_cursor(start_iter)
                return True
        elif event.keyval == gtk.keysyms.Left:
            insert_iter.backward_cursor_position()
            if not insert_iter.editable(True):
                return True
        elif not event.string:
            pass
        elif start_iter.compare(insert_iter) <= 0 and \
             start_iter.compare(selection_iter) <= 0:
            pass
        elif start_iter.compare(insert_iter) > 0 and \
             start_iter.compare(selection_iter) > 0:
            self.text_buffer.place_cursor(start_iter)
        elif insert_iter.compare(selection_iter) < 0:
            self.text_buffer.move_mark(insert_mark, start_iter)
        elif insert_iter.compare(selection_iter) > 0:
            self.text_buffer.move_mark(selection_mark, start_iter)             

        return self.onKeyPressExtend(event)

    def onKeyPressExtend(self, event):
        '''
        For some reason we can't extend onKeyPress directly (bug #500900).
        '''
        pass

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

    def onKeyPressExtend(self, event):
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
        if event.state & gtk.gdk.CONTROL_MASK and event.keyval == 99:
            self.interrupt = True
            self._processLine()
            return True
        elif event.keyval == gtk.keysyms.Return:
            self._processLine()
            return True
        elif event.keyval == gtk.keysyms.Up:
            self.changeLine(self.historyBack())
            return True
        elif event.keyval == gtk.keysyms.Down:
            self.changeLine(self.historyForward())
            return True
        elif event.keyval == gtk.keysyms.Tab:
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
