from dataclasses import dataclass
from typing import Dict
from dmr.rsp import Rsp
from dmr.rsp import ResponseParser

@dataclass
class TestCase:
    message: str
    expectedState: ResponseParser.State
    expectedProperties: Dict[str, str]

parser = ResponseParser()

testCases = [
    TestCase(
        message=
            'ATTACH RSP/{}\n'.format(Rsp.VERSION) +
            'Seq=123456\n' +
            'SessionID=0\n' +
            'Width=640\n' +
            'Height=480\n' +
            '\n',
        expectedState=ResponseParser.State.FAILED,
        expectedProperties={}),

    TestCase(
        message=
            'RSP/0.1 200 OK\n'.format(Rsp.VERSION) +
            'Seq=54321\n' +
            'SessionID=0\n' +
            '\n',
        expectedState=ResponseParser.State.DONE,
        expectedProperties={
            'SessionID': 0}),

    TestCase(
        message=
            'S0 1\n' +
            '323653906\n' +
            '2,10,2,10,0.9,1,person\n' +
            '12,20,12,20,0.8,1,person\n' +
            '\n',
        expectedState=ResponseParser.State.FAILED,
        expectedProperties={}),

    TestCase(
        message=
            'S0 2\n' +
            '1,-1,1\n' +
            '\n',
        expectedState=ResponseParser.State.FAILED,
        expectedData={})
]

for i, testCase in enumerate(testCases):
    print('\n==================== Case {} ====================\n'.format(i+1))
    print('---------- Message String ----------')
    print(testCase.message)
    print('------------------------------------')

    print('\n---------- Begin parsing ----------\n')

    state, response = (None, None)
    for line in testCase.message.splitlines():
        state, response = parser.parseLine(line)
        print('Parse Line: {}\n  State: {}'.format(line, state))

        if parser.isTerminated():
            print('Parser Terminated')
            break

    print('\n----------- End parsing -----------\n')

    assert state == testCase.expectedState

    if state == ResponseParser.State.DONE:
        assert response is not None

        print('Status-Code: {}'.format(response.statusCode))
        print('Status-Message: {}'.format(response.statusMessage))
        print('Sequence-Number: {}\n'.format(response.sequence))

        for property in response.getProperties():
            print('Property\n  key: {}\n  value: {}'.format(
                property,
                response.getProperty(property)))

            assert property in testCase.expectedProperties

        for property in testCase.expectedProperties:
            assert response.getProperty(property) is not None

    print('\n=================== Case End ===================')

    parser.reset()
