# -*- coding: utf-8 -*-

"""
Provides an interactive python shell based on IPython.

@author: Benjamin Hepp
@copyright: Copyright (c) 2011 Benjamin Hepp
@license: BSD

All rights reserved. This program and the accompanying materials are made 
available under the terms of the FreeBSD which accompanies this distribution,
and is available at U{http://www.opensource.org/licenses/BSD-2-Clause}
"""
# this file is a modified version of source code from the Accerciser project
# http://live.gnome.org/accerciser

import re
import sys
import os

try:
    import IPython
except ImportError, e:
    raise Exception("Error importing IPython (%s)" % str(e))

class IterableIPShell:
    '''
    Create an IPython instance. Does not start a blocking event loop,
    instead allow single iterations. This allows embedding in GTK+ 
    without blockage.

    @ivar IP: IPython instance.
    @type IP: IPython.iplib.InteractiveShell
    @ivar iter_more: Indicates if the line executed was a complete command,
    or we should wait for more.
    @type iter_more: integer
    @ivar history_level: The place in history where we currently are 
    when pressing up/down.
    @type history_level: integer
    @ivar complete_sep: Seperation delimeters for completion function.
    @type complete_sep: _sre.SRE_Pattern
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
        if input_func:
            IPython.iplib.raw_input_original = input_func
        if cin:
            IPython.Shell.Term.cin = cin
        if cout:
            IPython.Shell.Term.cout = cout
        if cerr:
            IPython.Shell.Term.cerr = cerr

        if argv is None:
            argv = []

        self.exit_func = exit_func

        # This is to get rid of the blockage that accurs during 
        # IPython.Shell.InteractiveShell.user_setup()
        IPython.iplib.raw_input = lambda x: None

        self.term = IPython.genutils.IOTerm(cin=cin, cout=cout, cerr=cerr)
        os.environ['TERM'] = 'dumb'
        excepthook = sys.excepthook 
        self.IP = IPython.Shell.make_IPython(
            argv,user_ns=user_ns,
            user_global_ns=user_global_ns,
            embedded=True,
            shell_class=IPython.Shell.InteractiveShell)
        self.IP.system = lambda cmd: self.shell(self.IP.var_expand(cmd),
                                                header='IPython system call: ',
                                                verbose=self.IP.rc.system_verbose)
        self.IP.api.system = self.IP.system
        self.IP.autoindent = True
        self.IP.rc.confirm_exit = False
        sys.excepthook = excepthook
        self.iter_more = 0
        self.history_level = 0
        self.complete_sep =  re.compile('[\s\{\}\[\]\(\)]')

    def execute(self):
        '''
        Executes the current line provided by the shell object.
        '''
        self.history_level = 0
        orig_stdout = sys.stdout
        sys.stdout = IPython.Shell.Term.cout
        try:
            line = self.IP.raw_input(None, self.iter_more)
            if self.IP.autoindent:
                self.IP.readline_startup_hook(None)
        except KeyboardInterrupt:
            self.IP.write('\nKeyboardInterrupt\n')
            self.IP.resetbuffer()
            # keep cache in sync with the prompt counter:
            self.IP.outputcache.prompt_count -= 1

            if self.IP.autoindent:
                self.IP.indent_current_nsp = 0
            self.iter_more = 0
        except:
            self.IP.showtraceback()
        else:
            self.iter_more = self.IP.push(line)
            if (self.IP.SyntaxTB.last_syntax_error and
                self.IP.rc.autoedit_syntax):
                self.IP.edit_syntax_error()
        if self.iter_more:
            self.prompt = str(self.IP.outputcache.prompt2).strip()
            if self.IP.autoindent:
                self.IP.readline_startup_hook(self.IP.pre_readline)
        else:
            self.prompt = str(self.IP.outputcache.prompt1).strip()
        sys.stdout = orig_stdout
        if self.IP.exit_now:
            if self.exit_func is not None:
                self.exit_func()

    def historyBack(self):
        '''
        Provides one history command back.

        @return: The command string.
        @rtype: string
        '''
        if -self.history_level < len(self.IP.user_ns['In']):
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
            rv = self.IP.user_ns['In'][self.history_level].strip('\n')
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
        self.IP.user_ns.update(ns_dict)

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
        split_line = self.complete_sep.split(line)
        possibilities = self.IP.complete(split_line[-1])
        if possibilities:
            def _commonPrefix(str1, str2):
                '''
                Reduction function. returns common prefix of two given strings.

                @param str1: First string.
                @type str1: string
                @param str2: Second string
                @type str2: string

                @return: Common prefix to both strings.
                @rtype: string
                '''
                for i in range(len(str1)):
                    if not str2.startswith(str1[:i+1]):
                        return str1[:i]
                return str1
            common_prefix = reduce(_commonPrefix, possibilities)
            completed = line[:-len(split_line[-1])]+common_prefix
        else:
            completed = line
        return completed, possibilities

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
