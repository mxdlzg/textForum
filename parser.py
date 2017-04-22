from html.parser import HTMLParser
from re import sub
from sys import stderr
from traceback import print_exc



if __name__ == '__main__':
    string = "\\r\\n\\t\\t\\t\\t"
    string = string.replace('\\r\\n','')
    print(string)