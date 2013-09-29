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
# Authors: Yaakov M. Nemoy <ynemoy@redhat.com>
#

import re
from copy import copy

class Either(object):
    def __init__(self, value, right=True):
        self.value = value
        self.state = right

    @property
    def left(self):
        return not self.state

    @property
    def right(self):
        return self.state


class Pattern(object):
    '''A base catch all pattern

    always returns true.

    A pattern is any kind of pattern that can be evaluated for a line.
    '''
    def match(self, line):
        '''base method for matching lines
        
        should return either None, True, False or some Match object 
        that will be passed to the handler in certain conditions
        '''
        return True

    def __call__(self, line):
        '''shortcut for match
        '''
        return self.match(line)


Begin = Pattern()
End = Pattern()
EveryLinePattern = Pattern()


class FalsePattern(Pattern):
    def match(self, line):
        return False

class RegexPattern(Pattern):
    '''a specialized pattern that accepts a regex as the matcher

    returns the regex MatchObject when matches are found
    '''
    def __init__(self, regex_str, flags=0):
        '''creates a RegexPattern

        regex_str is a str that is a regex
        '''
        self.regex_str = regex_str
        self.flags = flags
        self.is_compiled = False

    @property
    def regex(self):
        '''a compiled regex for the regex represented by this object
        '''
        if not self.is_compiled:
            self._regex = re.compile(self.regex_str, self.flags)
            self.is_compiled = True
        return self._regex

    def match(self, line):
        '''returns a MatchObject where a match is found
        '''
        return self.regex.search(line)


class UnaryPattern(Pattern):
    def __init__(self, first):
        self.first = first
    
    def match(self, line):
        raise NotImplementedError


class BinaryPattern(Pattern):
    '''Base class for any binary operator
    '''
    def __init__(self, first, second):
        self.first = first
        self.second = second
    
    def match(self, line):
        raise NotImplementedError


class TrinaryPattern(Pattern):
    '''Base class for any trinary operator
    '''
    def __init__(self, first, second, third):
        self.first = first
        self.second = second
        self.third = third


class AndPattern(BinaryPattern):
    '''and operator analagous to the python 'and' operator
    '''
    def match(self, line):
        '''operates the same as 'and' in python namely:

        when the first and second match, it returns the second match
        when one match fails, it returns the output of the first failure

        evaluates lazy, so if the first match fails, the second match is never evaluated
        '''
        return self.first.match(line) and self.second.match(line)


class OrPattern(BinaryPattern):
    '''or operator analagous to the python 'or' operator
    '''
    def match(self, line):
        '''operates the same as 'or' in python namely:

        when the first or second match, it returns the first positive match
        when both matches fails, it returns the output of the second failure

        evaluates lazy, so if the first match succeeds, the second match is never evaluated
        '''
        return self.first.match(line) or self.second.match(line)


class RangePattern(BinaryPattern):
    '''matches against two patterns that define a range, as in Gnu Awk
    '''
    def __init__(self, first, second):
        BinaryPattern.__init__(self, first, second)
        self.is_in_range = False

    def match(self, line):
        '''matches when the first match is found up until and including when the second match is found

        if the first match is found, it returns that match, otherwise it constantly returns true
        up until the second match is found, then it returns that match, and returns False subsequently
        '''
        if not self.is_in_range:
            match = self.first.match(line)
            if match:
                self.is_in_range = True
                return match
            return False
        else:
            match = self.second.match(line)
            if match:
                self.is_in_range = False
                return match
            return True


class NotPattern(UnaryPattern):
    '''analagous to python 'not' operator
    '''
    def match(self, line):
        '''if the match is found, return False, else return True
        '''
        return not self.first.match(line)


class IfThenPattern(TrinaryPattern):
    '''analogous to the ?: trinary operator in Gnu Awk
    '''
    def match(self, line):
        '''if the first match succeeds, it returns the output of the second match, otherwise the third'''
        if self.first.match(line):
            return self.second.match(line)
        else:
            return self.third.match(line)


class OneOfPattern(Pattern):
    def __init__(self, *patterns):
        self.patterns = patterns

    def match(self, line):
        for pattern in self.patterns:
            match = pattern.match(line)
            if match:
                return match
        return None


def handler(awk, match, line):
    '''function signature'''
    pass


class BaseHandler(object):
    '''an example base handler that always yields what it is given

    analogous to a simple 'print' in Gnu Awk
    '''
    def __call__(self, awk, match, line):
        yield


class PrintHandler(object):
    def __call__(self, awk, match, line):
        yield line


class Action(object):
    '''a composite of a pattern and handler, equivalent to a line of code in Gnu Awk'''
    def __init__(self, pattern=EveryLinePattern, handler=PrintHandler()):
        self.pattern = pattern
        self.handler = handler

    def match(self, awk, line):
        '''given a line and the current awk instance, see if it matches, and if so, invoke the hanndler
        '''
        match = self.pattern.match(line)
        if match:
            return self.handler(awk, match, line)

    def __call__(self, awk, line):
        '''convenience function
        '''
        return self.match(awk, line)


class EitherOrPattern(BinaryPattern):
    def match(self, line):
        match = self.first.match(line)
        if match:
            return Either(match, right=True)
        else:
            return Either(self.second.match(line), right=False)


class EitherOrHandler(BaseHandler):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, awk, match, line):
        if match.right:
            return self.right(awk, match.value, line)
        else:
            return self.left(awk, match.value, line)


class MatchOrEveryLinePattern(UnaryPattern):
    def match(self, line):
        match = self.first.match(line)
        if match:
            return Either(match, right=True)
        else:
            return Either(True, right=False)


class EitherOrAction(Action):
    def __init__(self, first, second):
        self.pattern = EitherOrPattern(first.pattern, second.pattern)
        self.handler = EitherOrHandler(first.handler, second.handler)


class MatchOrPrintHandler(EitherOrHandler):
    def __init__(self, handler):
        EitherOrHandler.__init__(self, PrintHandler(), handler)


class ActionOrPrint(Action):
    def __init__(self, pattern=EveryLinePattern, handler=PrintHandler()):
        self.pattern = MatchOrEveryLinePattern(pattern)
        self.handler = MatchOrPrintHandler(handler)


BarPattern = RegexPattern(r'(?P<bar>bar)')
def BarHandler(awk, match, line):
    yield 'quack!'

BarAction = ActionOrPrint(BarPattern, BarHandler)


class DoubleHandler(object):
    '''an example handler that doubles a line given
    '''
    def __call__(self, awk, match, line):
        yield line
        yield line


Print = Action()
DoublePrint = Action(handler=DoubleHandler())


class IncrementHandler(object):
    '''an example handler that counts up each time it's called and yields 
    a line n times for the current count, including a prefixed line number
    '''
    def __init__(self):
        self.count = 0

    def __call__(self, awk, match, line):
        self.count += 1
        for nr in xrange(self.count):
            yield str(nr) + ": " + line


IncrementPrint = Action(handler=IncrementHandler())

class AwkInstance(object):
    def __init__(self, begin, actions, end):
        self.fs = ' '
        self.nr = 0
        self.rs = '\n'
        self.begin = begin
        self.actions = actions
        self.end = end

    def process(self, generator):
        '''for some iterable, run all the actions given
        '''
        for action in self.begin:
            result = action.match(self, None)
            if result:
                for line in result:
                    yield line
        for line in generator:
            for action in self.actions:
                result = action.match(self, line)
                if result:
                    for line in result:
                        yield line
            self.nr += 1
        for action in self.end:
            result = action.match(self, None)
            if result:
                for line in result:
                    yield line

    def __call__(self, generator):
        return self.process(generator)


class AwkProgram(object):
    '''Class representing an instance of awk

    this will probably be broken up a bit to seperate the declaration of a program
    and the runtime thereof
    '''
    def __init__(self):
        self.actions = list()
        self.begin = list()
        self.end = list()

    
    def add_pattern_w_handler(self, pattern, handler):
        '''given a simple pattern and handler, add it to the queue
        '''
        self.add_action(Action, pattern, handler)

    def add_action(self, action):
        '''adds an action to the list of actions

        if the action runs on Begin, it is run before any lines are processed
        if the action runs on End, it is run after all lines are processed
        otherwise it is run once per line
        '''
        if action.pattern is Begin:
            self.begin.append(action)
        elif action.pattern is End:
            self.end.append(action)
        else:
            self.actions.append(action)

    def run(self):
        begin = copy(self.begin)
        actions = copy(self.actions)
        end = copy(self.end)
        return AwkInstance(begin, actions, end)

    def __call__(self):
        return self.run()


Repeater = AwkProgram()
Repeater.add_action(Print)
repeater = Repeater()

Doubler = AwkProgram()
Doubler.add_action(DoublePrint)
doubler = Doubler()

Incrementer = AwkProgram()
Incrementer.add_action(IncrementPrint)
incrementer = Incrementer()

BarProgram = AwkProgram()
BarProgram.add_action(BarAction)
bar = BarProgram()

def demonstrate():
    foo = ['bar', 'baz', 'quux']
    
    print list(repeater(foo))
    print
    print list(doubler(foo))
    print
    print list(incrementer(foo))
    print
    print list(bar(foo))

__all__ = ['Either', 'Pattern', 'Begin', 'End', 'EveryLinePattern', 'RegexPattern',
           'UnaryPattern', 'BinaryPattern', 'TrinaryPattern', 'AndPattern', 
           'OrPattern', 'RangePattern', 'NotPattern', 'IfThenPattern', 'MatchOrEveryLinePattern',
           'BaseHandler', 'PrintHandler', 'DoubleHandler', 'IncrementHandler', 'Action', 
           'ActionOrPrint', 'Print', 'AwkInstance', 'AwkProgram', 'OneOfPattern']
