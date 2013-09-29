# Fedora Developer Shell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors: Luke Macken <lmacken@redhat.com>
#          Yaakov M. Nemoy <ynemoy@redhat.com>
#
import logging
import os

from inspect import isclass
from collections import deque
from os.path import join, dirname


from devshell.base.module import Module
from devshell.base.vars import __description__, __version__, header, prompt
from devshell.base.exceptions import ModuleError, ExecutionException


log = logging.getLogger('devshell')
modules = {}

def print_docstrings(module=None):
    """
    Print out the docstrings for all methods in the specified module.
    If no module is specified, then display docstrings for all modules.
    
    Arguments:
    module: an object subclassing Module (optional)
    """
    def _print_docstrings(name, module):
        log.info(header(name))
        for prop in filter(lambda x: x[0] != '_', dir(module)):
            if callable(getattr(module, prop)) and hasattr(module, '__doc__') \
               and getattr(module, prop).__doc__:
                log.info("   |- [%s] %s" % (prop,
                         getattr(module, prop).__doc__.strip()))
    if not module:
        for name, module in modules.items():
            _print_docstrings(name, module)
    else:
        _print_docstrings(str(module.__class__).split('.')[-1], module)

def load_modules():
    global modules
    import devshell.modules as mods
    log.debug("Loading modules")
    #TODO: better way to find modules
    for f in os.listdir(dirname(mods.__file__)):
        module_name, ext = os.path.splitext(f)
        if ext == '.py':
            exec "from devshell.modules import %s as module" % module_name
            for item in dir(module):
                obj = getattr(module, item)
                if item[0] != '_' and isclass(obj) and issubclass(obj, Module) \
                    and obj is not Module:
                    modules[item.lower()] = obj
                    log.info(" * %s" % item)
            del module

def load_module(name, data=[]):
    top = None
    try:
        top = modules[name](*data)
    except TypeError, e:
        log.error("%s: %s" % (name, e))
        raise ModuleError('probably bad call to __init__' , e)
    return top

def shell():
    while True:
        try:
            data = raw_input('/'.join(shell.prompt) + '> ')
        except (EOFError, KeyboardInterrupt):
            print
            break
        if not data: continue
        if data in ('quit', 'exit'): break
        keyword = data.split()[0]
        args = data.split()[1:]
    
        # Show the docstrings to all methods for all loaded modules
        if keyword == 'help':
            print_docstrings()
    
        # Go up a module in our stack
        elif keyword in ('up', 'cd..', 'cd ..'):
            shell.stack[-1].close()
            shell.stack = shell.stack[:-1]
            shell.prompt = shell.prompt[:-1]
    
        # Show the docstrings for all methods in our current module
        elif keyword in ('ls', 'help', '?'):
            if len(shell.stack):
                print_docstrings(shell.stack[-1])
            else:
                print_docstrings()
    
        # Flush our module stack
        elif keyword == 'cd':
            for obj in shell.stack:
                obj.close()
            shell.stack = []
            shell.prompt = prompt
    
        # iPython.  Never leave home without it.
        elif keyword in ('py', 'python'):
            os.system("ipython -noconfirm_exit")
        else:
            #figure out if there is a top
            if len(shell.stack):
                top = shell.stack[-1]
            else:
                top = None
            output, top, params = do_command(data.split(), top)
            if top:
                shell.stack += [top]
                shell.prompt += [top.__class__.__name__] + params
shell.stack = []
shell.prompt = prompt

def do_command(data, top=None):

    # Do some intelligent handling of unknown input.
    # For the given input 'foo bar', we first check if we have the
    # module 'foo' loaded, then we push it on the top of our module
    # stack and check if it has the 'bar' attribute.  If so, we call
    # it with any remaining arguments
    data = deque(data)
    params = []
    
    module = None
    params = []
    while len(data):
        if not top:
            mod = data.popleft()
            try:
                module = modules[mod]
            except KeyError, e:
                log.error('%s is not a known module' % e.message)
                return None, None, None
            while len(data):
                param = data.popleft()
                if hasattr(module, param):
                    data.appendleft(param)
                    break
                params += [param]
            try:
                top = module = load_module(mod, params)
                mod_params = params
                params = []
                loaded_module = True
            except ModuleError, e:
                log.debug(e.reason)
                break
        else:
            param = data.popleft()
            if hasattr(top, param):
                top = getattr(top, param)
            else:
                params += [param]
    output = None
    try:
        output = top(*params)
    except ExecutionException, e:
        # TODO: maket his as helpful as possible to the user
        log.critical('execution of command failed because: %s' % e.message)

    if module:
        return output, module, mod_params
    else:
        return output, None, None

def setup_options():
    '''Sets up an options parser for all command line utilities
    
    Arguements:
    none: none!
    
    Return Values:
    opts: an object containing the options specified
    args: remaining arguments
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%s %s" % ('%prog', __version__),
                          description=__description__)
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      help='Display verbose debugging output')
    return parser.parse_args()

def setup_logger(opts):
    '''Configures the logger system to the environment
    
    Arguments:
    opts: options from an OptionParser
    
    Return Values:
    none: none!
    '''
    global log
    # Setup our logger
    sh = logging.StreamHandler()
    if opts.verbose:
        log.setLevel(logging.DEBUG)
        sh.setLevel(logging.DEBUG)
        format = logging.Formatter("[%(levelname)s] %(message)s")
    else:
        log.setLevel(logging.INFO)
        sh.setLevel(logging.INFO)
        format = logging.Formatter("%(message)s")
    sh.setFormatter(format)
    log.addHandler(sh)

__all__ = ['do_command', 'log', 'setup_options', 'load_module', 'shell',
           'print_docstrings', 'modules', 'setup_logger', 'load_modules']
