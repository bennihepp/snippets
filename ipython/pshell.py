# -*- coding: utf-8 -*-

"""
Provides a replacement for ipshell.py when IPython is not available.

@author: Benjamin Hepp
@copyright: Copyright (c) 2011 Benjamin Hepp
@license: BSD

All rights reserved. This program and the accompanying materials are made 
available under the terms of the FreeBSD which accompanies this distribution,
and is available at U{http://www.opensource.org/licenses/BSD-2-Clause}
"""

import re
import sys
import os


class InteractiveSession(object):

    def __init__(self, local_ns, global_ns, stdout=sys.stdout, stderr=sys.stderr, *args, **kwargs):
        super(InteractiveSession, self).__init__(*args, **kwargs)
        self.__hooks = []
        self.__local_ns = local_ns
        self.__global_ns = global_ns
        self.__stdout = stdout
        self.__stderr = stderr
        self.__line_stack = []

    def add_hook(self, callback):
        self.__hooks.append(callback)

    def remove_hook(self, callback):
        self.__hooks.remove(callback)

    def push(self, line):
        l = line.strip()
        self.__line_stack.append(l)
        if l.endswith(':') or l.endswith('\\'):
            return True
        elif len(self.__line_stack) == 1 or len(l) == 0:
            self.execute(self.__line_stack)
            self.__line_stack = []
            return False
        else:
            return True

    def execute(self, lines):
        lines = '\n'.join(lines)
        try:
            orig_stdout = sys.stdout
            orig_stderr = sys.stderr
            sys.stdout = self.__stdout
            sys.stderr = self.__stderr
            try:
                tmp = None
                if '_' in self.__local_ns:
                    tmp = [ self.__local_ns[ '_' ] ]
                if '_' in self.__global_ns:
                    tmp = [ self.__global_ns[ '_' ] ]
                lines2 = '_ = ' + lines
                exec lines2 in self.__global_ns, self.__local_ns
                print >> self.__stdout, self.__local_ns[ '_' ]
                self.__stdout.flush()
                if tmp is not None:
                    self.__local_ns[ '_' ] = tmp
            except Exception, e:
                exec lines in self.__global_ns, self.__local_ns
        except Exception, e:
            print >> self.__stderr, 'Exception:', e
            self.__stderr.flush()
        finally:
            for hook in self.__hooks:
                hook()
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr

    def parse(self, line):
        self.execute([line.strip()])

#try:
    #import IPython

    #class ICmd(IPython.core.interactiveshell.InteractiveShell, Thread):
        #import sys, os, tempfile

        #def __init__(self, local_ns, global_ns, stdout=sys.stdout, stderr=sys.stderr, *args, **kwargs):
            #self.__old_io = [sys.stdout, sys.stderr]
            #self.__handle, filename = tempfile.mkstemp()
            #os.mkfifo(filename)
            #sys.stdout = open(filename, os.O_WRONLY)
            #sys.stderr = sys.stdout
            #sys.stdin = open(filename, os.O_RDONLY)
            #kwargs['user_ns'] = local_ns
            #kwargs['user_global_ns'] = global_ns
            #super(ICmd, self).__init__(*args, **kwargs)
            #sys.stdin, sys.stdout, sys.stderr = self.__old_io
            ##Thread.__init__(self)
            #if self.thread_support():
                #self.start_method(self.__loop)

        #def __loop(self):
            
            #os.close(self.__handle)

class IterablePShell:
    '''
    Create a basic interactive Python instance.

    @ivar iter_more: Indicates if the line executed was a complete command,
    or we should wait for more.
    @type iter_more: integer
    @ivar history_level: The place in history where we currently are 
    when pressing up/down.
    @type history_level: integer
    '''
    def __init__(self, argv=[], user_ns=None, user_global_ns=None,
                 cin=None, cout=None,cerr=None, input_func=None,
                 exit_func=None):
        '''
        @param argv: Command line options for IPython
        @type argv: list
        @param user_ns: User namespace.
        @type user_ns: dictionary
        @param user_global_ns: User global namespace.
        @type user_global_ns: dictionary.
        @param cin: Console standard input.
        @type cin: IO stream
        @param cout: Console standard output.
        @type cout: IO stream 
        @param cerr: Console standard error.
        @type cerr: IO stream
        @param input_func: Replacement for builtin raw_input()
        @type input_func: function
        '''
        if user_ns is None:
            user_ns = {}
        if user_global_ns is None:
            user_global_ns = {}

        self.raw_input = input_func
        self.cin = cin
        self.cout = cout
        self.cerr = cerr
        self.exit_func = exit_func

        self.isession = InteractiveSession(user_ns, user_global_ns, stdout=cout, stderr=cout)

        self.user_ns = user_ns
        self.user_global_ns = user_global_ns
        self.iter_more = 0
        self.history = []
        self.history_level = 0
        os.environ['TERM'] = 'dumb'

        self.prompt = '>>> '

    def execute(self):
        '''
        Executes the current line provided by the shell object.
        '''
        self.history_level = 0
        #orig_stdout = sys.stdout
        #sys.stdout = self.cout
        try:
            #line = self.raw_input(None, self.iter_more)
            line = self.raw_input()
        except KeyboardInterrupt:
            self.write('\nKeyboardInterrupt')
            #self.IP.resetbuffer()
            # keep cache in sync with the prompt counter:
            #self.IP.outputcache.prompt_count -= 1

            #if self.IP.autoindent:
            #    self.IP.indent_current_nsp = 0
            self.iter_more = 0
        #except:
        #    self.IP.showtraceback()
        else:
            if not self.iter_more and line.startswith('!'):
                orig_stdout = sys.stdout
                orig_stderr = sys.stderr
                sys.stdout = self.cerr
                sys.stderr = self.cout
                self.shell(line[1:])
                sys.stdout = orig_stdout
                sys.stderr = orig_stderr
            else:
                self.iter_more = self.isession.push(line)
            #if (self.IP.SyntaxTB.last_syntax_error and
            #    self.IP.rc.autoedit_syntax):
            #    self.IP.edit_syntax_error()
        if self.iter_more:
            #self.prompt = str(self.IP.outputcache.prompt2).strip()
            #if self.IP.autoindent:
            #    self.IP.readline_startup_hook(self.IP.pre_readline)
            self.prompt ='... '
        else:
            #self.prompt = str(self.IP.outputcache.prompt1).strip()
            self.prompt = '>>> '
        #sys.stdout = orig_stdout

    def historyBack(self):
        '''
        Provides one history command back.

        @return: The command string.
        @rtype: string
        '''
        if -self.history_level < len(self.history):
            self.history_level -= 1
        return self._getHistory()

    def historyForward(self):
        '''
        Provides one history command forward.

        @return: The command string.
        @rtype: string
        '''
        if self.history_level < 0:
            self.history_level += 1
        return self._getHistory()

    def _getHistory(self):
        '''
        Get's the command string of the current history level.

        @return: Historic command string.
        @rtype: string
        '''
        try:
            rv = self.history[self.history_level].strip('\n')
        except IndexError:
            self.history_level = 0
            rv = ''
        return rv

    def updateNamespace(self, ns_dict):
        '''
        Add the current dictionary to the shell namespace.

        @param ns_dict: A dictionary of symbol-values.
        @type ns_dict: dictionary
        '''
        self.user_ns.update(ns_dict)

    def updateGlobalNamespace(self, ns_dict):
        '''
        Add the current dictionary to the global shell namespace.

        @param ns_dict: A dictionary of symbol-values.
        @type ns_dict: dictionary
        '''
        self.user_global_ns.update(ns_dict)

    def complete(self, line):
        '''
        Returns an auto completed line and/or posibilities for completion.

        @param line: Given line so far.
        @type line: string

        @return: Line completed as for as possible, 
        and possible further completions.
        @rtype: tuple
        '''
        return line, []

    def shell(self, cmd, verbose=0, debug=0, header=''):
        '''
        Replacement method to allow shell commands without them blocking.

        @param cmd: Shell command to execute.
        @type cmd: string
        @param verbose: Verbosity
        @type verbose: integer
        @param debug: Debug level
        @type debug: integer
        @param header: Header to be printed before output
        @type header: string
        '''
        stat = 0
        if verbose or debug: print header+cmd
        # flush stdout so we don't mangle python's buffering
        if not debug:
            input, output = os.popen4(cmd)
            print output.read()
            output.close()
            input.close()
