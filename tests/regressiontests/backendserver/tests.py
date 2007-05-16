backed_server = r'''
>>> from nc.backendserver import BackendServer
>>> bs = BackendServer(56789, 'localhost')
>>> status, response = bs.ask('G', name='al3x')
>>> status
(210, 'OK')
>>> response['UID']
4233
'''

parse_answer = r'''
>>> from nc.backendserver import BackendServer, LINE_TERMINATOR
>>> bs = BackendServer(None)
>>> answer = ('210 OK', 'UID: 4233', 'NAME: al3x', 'PWD: 11c08f2be758e0464e7ff3aaade3a135',
... 'SIG: ', 'CRD: 57', 'HITS: 0', 'BONUS_PLUS: 0', 'BONUS_MINUS: 0', 'LAST_HIT: 30.3.2007 15:40:48',
... 'LAST_BONUS: 15.1.2007 15:12:40', 'HASH_NUM: 5', 'LOG: 2', 'TO_HASH: 2', 'SPEC: 0', 'MAIL_NODE: 1',
... 'IP: 62.84.145.14', 'FORWARDED_FOR: 62.84.145.32', 'KNOW_SIG: 1', 'KNOW_PASS: 1', 'HASH_TIME: 3600',)
>>> status, data = bs._parse_answer(LINE_TERMINATOR.join(answer))
>>> status
(210, 'OK')
>>> data['UID']
4233
>>> data['SIG']
''
>>> data['HASH_TIME']
3600
>>> data['LAST_HIT']
datetime.datetime(2007, 3, 30, 15, 40, 48)
>>> len(data.values())
20
'''

build_query = r'''
>>> from nc.backendserver import BackendServer, LINE_TERMINATOR
>>> bs = BackendServer(None)
>>> bs._build_query('G', name='12', SSS=123, a1='', name2='a\r\nb')
'G\r\na1: \r\nname2: a b\r\nname: 12\r\nSSS: 123\r\n\r\n'
'''

parse_line = r'''
>>> from nc.backendserver import BackendServer
>>> bs = BackendServer(None)
>>> bs._parse_line('NAME: al3x \r\n')
('NAME', 'al3x')
>>> bs._parse_line('XXX:   23     ')
('XXX', 23)
>>> bs._parse_line('KEY:  -123  ')
('KEY', '-123')
>>> bs._parse_line('LAST_HIT: 30.3.2007 15:40:48')
('LAST_HIT', datetime.datetime(2007, 3, 30, 15, 40, 48))
'''

escape = r'''
>>> from nc.backendserver import BackendServer
>>> import datetime
>>> bs = BackendServer(None)
>>> dt = datetime.datetime.fromtimestamp(10000)
>>> bs._escape(dt)
'01.01.1970 03:46:40'
>>> bs._escape('some\r\nnasty\rtext\n')
'some nasty\rtext\n'
>>> bs._escape(True)
'1'
>>> bs._escape(False)
'0'
'''

__test__ = {
    'escape' : escape,
    'build_query' : build_query,
    'parse_line' : parse_line,
    'parse_answer' : parse_answer,
    'backend_server' : backed_server,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()
