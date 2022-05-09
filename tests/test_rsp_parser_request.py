from dataclasses import dataclass
from typing import Dict
from dmr.rsp import Rsp
from dmr.rsp import RequestParser

@dataclass
class TestCase:
    message: str
    expectedState: RequestParser.State
    expectedProperties: Dict[str, str]

parser = RequestParser()

testCases = [
    TestCase(
        message=
            'ATTACH RSP/{}\n'.format(Rsp.VERSION) +
            'Seq=123456\n' +
            'SessionID=0\n' +
            'Width=640\n' +
            'Height=480\n' +
            '\n',
        expectedState=RequestParser.State.DONE,
        expectedProperties={
            'SessionID': 0,
            'Width': 640,
            'Height': 480}),

    TestCase(
        message=
            'RSP/0.1 200 OK\n'.format(Rsp.VERSION) +
            'Seq=54321\n' +
            'SessionID=0\n' +
            '\n',
            expectedState=RequestParser.State.FAILED,
            expectedProperties={})
]

for i, testCase in enumerate(testCases):
    print('\n==================== Case {} ====================\n'.format(i+1))
    print('---------- Message String ----------')
    print(testCase.message)
    print('------------------------------------')

    print('\n---------- Begin parsing ----------\n')

    state, request = (None, None)
    for line in testCase.message.splitlines():
        state, request = parser.parseLine(line)
        print('Parse Line: {}\n  State: {}'.format(line, state))

        if parser.isTerminated():
            print('Parser Terminated')
            break

    print('\n----------- End parsing -----------\n')

    assert state == testCase.expectedState

    if state == RequestParser.State.DONE:
        assert request is not None

        print('Request-Method: {}'.format(request.method))
        print('Sequence-Number: {}\n'.format(request.sequence))

        for property in request.getProperties():
            print('Property\n  key: {}\n  value: {}'.format(
                property,
                request.getProperty(property)))

            assert property in testCase.expectedProperties

        for property in testCase.expectedProperties:
            assert request.getProperty(property) is not None

    print('\n=================== Case End ===================')

    parser.reset()
