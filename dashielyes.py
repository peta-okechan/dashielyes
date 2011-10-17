#!/usr/local/python
# -*- coding: utf-8 -*-

'''
プログラミング言語「ﾀﾞｧ!! ｼｴﾘｲｪｯｽ!!」
'''

import sys
import re
from optparse import OptionParser

command_expressions = [u'ﾀﾞｧ', u' ', u'ｼ', u'ｴ', u'ﾘ', u'ｲｪｯ', u'ｽ', u'!!']

'''
プログラム例

Hello, world!
ｼｼｼｼｼｼｼｼｼｽﾀﾞｧｼｼｼｼｼｼｼｼﾀﾞｧｼｼｼｼｼｼｼｼｼｼｼﾀﾞｧｼｼｼｼｼ   ｴ!!
ﾀﾞｧﾘﾀﾞｧｼｼﾘｼｼｼｼｼｼｼﾘﾘｼｼｼﾘﾀﾞｧｴﾘｴｴｴｴｴｴｴｴｴｴｴｴﾘ ｼｼｼｼｼｼｼｼﾘｴｴｴｴｴｴｴｴﾘｼｼｼﾘｴｴｴｴｴｴﾘｴｴｴｴｴｴｴｴﾘﾀﾞｧｼﾘ

Hello, world!(Brainfuck版)
+++++++++[>++++++++>+++++++++++>+++++<<<-]>.>++.+++++++..+++.>-.------------.<++++++++.--------.+++.------.--------.>+.
'''

def main():
    usage = "usage:python %prog [options] filename"
    version = "%prog 0.1"
    parser = OptionParser(usage = usage, version = version)
    parser.add_option(
        '-t', '--translate',
        action = 'store_true', dest = 'translate', default = False,
        help = 'Translate Brainfuck script.'
    )
    options, args = parser.parse_args()
    if len(args) != 1:
       parser.error("incorrect number of arguments")
    
    tm = TuringMachine()
    with open(args[0], 'rb') as f:
        code = f.read().decode('utf-8')
    if options.translate:
        print tm.translate(code, command_expressions)
    else:
        tm.compile(code, command_expressions)
        tm.run()

class TuringMachine(object):
    def __init__(self):
        self.tape = [0]
        self.pointer = 0
        self.compiled = False
    
    def command_expressions_test(self, command_expressions):
        if isinstance(command_expressions, list) and len(command_expressions) == 8:
            table = dict()
            for id, ce in enumerate(command_expressions):
                if ce in table:
                    raise Exception('Command Error: Duplicate Command')
                table[ce] = id
        else:
            raise Exception('Command Error: Wrong Commands')
    
    def translate(self, bf_code, command_expressions):
        self.command_expressions_test(command_expressions)
        bf_expressions = ['>', '<', '+', '-', '.', ',', '[', ']']
        bf_table = {}
        for id, be in enumerate(bf_expressions):
            bf_table[be] = id
        _command_list = []
        for c in bf_code:
            if c in bf_table:
                _command_list.append(command_expressions[bf_table[c]])
        return ''.join(_command_list)
    
    def compile(self, code, command_expressions):
        self.command_expressions_test(command_expressions)
        commands = [
            self.next, self.prev, self.incr, self.decr,
            self.putc, self.getc, self.njmp, self.pjmp,
        ]
        table = {}
        for id, ce in enumerate(command_expressions):
            table[ce] = commands[id]
        
        _command_list = []
        i = 0
        while i < len(code):
            for ce in command_expressions:
                if ce == code[i:i+len(ce)]:
                    _command_list.append(ce)
                    i += len(ce) - 1
            i += 1
        
        self.command_list = []
        for command in _command_list:
            if command in table:
                self.command_list.append(table[command])
        self.command_pointer = 0
        self.compiled = True
        
    def get_value(self):
        return self.tape[self.pointer]
    
    def set_value(self, value):
        self.tape[self.pointer] = value
    
    value = property(get_value, set_value)
    
    def current_command(self):
        if 0 <= self.command_pointer < len(self.command_list):
            return self.command_list[self.command_pointer]
        else:
            raise Exception('Program Error: Illegal Jump')
    
    def run(self):
        if not self.compiled:
            raise Exception('Compile Error: Not Compiled')
        while self.command_pointer < len(self.command_list):
            self.current_command()()
            self.command_pointer += 1
    
    def next(self):
        self.pointer += 1
    
    def prev(self):
        self.pointer -= 1
    
    def incr(self):
        while len(self.tape) <= self.pointer:
            self.tape.append(0)
        self.value += 1
    
    def decr(self):
        if self.pointer < 0:
            raise Exception('Program Error: Minus Pointer')
        self.value -= 1
    
    def putc(self):
        sys.stdout.write(unichr(self.value))
    
    def getc(self):
        input = raw_input().decode('utf-8')
        if len(input) <= 0:
            raise Exception('Input Error: No Input')
        self.value = ord(input[0])
    
    def njmp(self):
        if self.value == 0:
            while self.current_command() != self.pjmp:
                self.command_pointer += 1
    
    def pjmp(self):
        if self.value != 0:
            while self.current_command() != self.njmp:
                self.command_pointer -= 1
    
if __name__ == "__main__":
    main()