import sys
import re
import string
import pprint

class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


data = {'var': dict.fromkeys(string.ascii_uppercase, False),
        'rules': {},
        'request': [],
        'result': {}}
operation = ['(', ')', '!', '+', '|', '^']


def error(line):
    print('\033[91m' + re.split(':', line)[0] + ':\033[0m' + re.split(':', line)[1])
    sys.exit(1)


def check_order(line):
    i = 0
    for c in line:
        d = i % 2
        if c == '!' or c == '(' or c == ')':
            continue
        if i % 2 == 0 and c not in data['var']:
            error("Invalid order: '{}'".format(" ".join(line)))
        i += 1
    return


def syntax_check_left(line):
    i = 0
    for c in line:
        if c not in operation and c not in data['var']:
            error("Invalid value: '{}'".format(" ".join(line)))
        if c == '(':
            i += 1
        elif c == ')':
            i -= 1
            if i < 0:
                error("Invalid parentheses: '{}'!".format(" ".join(line)))
    if i != 0:
        error("Invalid parentheses: '{}'!".format(" ".join(line)))
    check_order(line)


def syntax_check_right(line):
    i = 0
    for c in line:
        if c not in operation and c not in data['var']\
                or c == '|' or c == '^':
            error("Invalid value: '{}'".format(" ".join(line)))
        if c == '(':
            i += 1
        elif c == ')':
            i -= 1
            if i < 0:
                error("Invalid parentheses: '{}'!".format(" ".join(line)))
    if i != 0:
        error("Invalid parentheses: '{}'!".format(" ".join(line)))
    check_order(line)


def get_true(line):
    line = line.replace('=', '', 1)
    line = line.replace(' ', '')
    for c in re.findall(r'.', line):
        if c not in data['var']:
            error("Non found key: '{}'!".format(c))
        data['var'][c] = True


def get_request(line):
    line = line.replace('?', '', 1)
    line = line.replace(' ', '')
    for c in re.findall(r'.', line):
        if c not in data['var']:
            error("Non found key: '{}'!".format(c))
        data['request'].append(c)


def add_rule(line):
    left = "".join(re.split('=>', line)[0].split())
    syntax_check_left(left)
    right = "".join(re.split('=>', line)[1].split())
    syntax_check_right(right)
    data['rules'][left] = right


def handle_input(f):
    for line in f:
        if '#' in line:
            line = re.split('#', line)[0]
        line = line.lstrip()
        if line == '\n' or line == '':
            continue
        if re.match('=', line):
            get_true(line)
        elif re.match(r'\?', line):
            get_request(line)
        elif '=>' in line:
            add_rule(line)
        else:
            error("Invalid line: '{}'!".format(line.replace('\n', '')))


def handle_op(result, c):
    if result and c == '+':
        return True


def is_true(rule):
    result = False
    false = False
    for c in rule:
        if c in data['var']:
            result = count_one(c)
        if c in operation:
            if result and c == '+':
                return True
    return result


def count_one(one):
    if data['var'][one]:
        return True
    for rule in data['rules']:
        if one in data['rules'][rule]:
            if is_true(rule):
                return True
    return False


def count(all_var):
    for one in all_var:
        data['result'][one] = count_one(one)
