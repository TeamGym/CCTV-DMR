from dataclasses import dataclass
from typing import Dict, Any
from dmr.rsp import Rsp
from dmr.rsp import StreamParser
from dmr.rsp.stream_data import DetectionResult
from dmr.rsp.stream_data import ControlPTZ

@dataclass
class TestCase:
    message: str
    expectedState: StreamParser.State
    expectedData: Any

parser = StreamParser()

testCases = [
    TestCase(
        message=
            'ATTACH RSP/{}\n'.format(Rsp.VERSION) +
            'Seq=123456\n' +
            'SessionID=0\n' +
            'Width=640\n' +
            'Height=480\n' +
            '\n',
        expectedState=StreamParser.State.FAILED,
        expectedData=None),

    TestCase(
        message=
            'RSP/0.1 200 OK\n'.format(Rsp.VERSION) +
            'Seq=54321\n' +
            'SessionID=0\n' +
            '\n',
        expectedState=StreamParser.State.FAILED,
        expectedData=None),

    TestCase(
        message=
            'S0 1\n' +
            '323653906\n' +
            '2,10,2,10,0.9,1,person\n' +
            '12,20,12,20,0.8,1,person\n' +
            '\n',
        expectedState=StreamParser.State.DONE,
        expectedData=DetectionResult(
            timestamp=323653906,
            boxes=[
                DetectionResult.DetectionBox(
                    left=2,
                    right=10,
                    top=2,
                    bottom=10,
                    confidence=0.9,
                    classID=1,
                    label='person'),
                DetectionResult.DetectionBox(
                    left=12,
                    right=20,
                    top=12,
                    bottom=20,
                    confidence=0.8,
                    classID=1,
                    label='person')])),

    TestCase(
        message=
            'S0 2\n' +
            '1,-1,1\n' +
            '\n',
        expectedState=StreamParser.State.DONE,
        expectedData=ControlPTZ(
            pan=1,
            tilt=-1,
            zoom=1))
]

for i, testCase in enumerate(testCases):
    print('\n==================== Case {} ====================\n'.format(i+1))
    print('---------- Message String ----------')
    print(testCase.message)
    print('------------------------------------')

    print('\n---------- Begin parsing ----------\n')

    state, stream = (None, None)
    for line in testCase.message.splitlines():
        state, stream = parser.parseLine(line)
        print('Parse Line: {}\n  State: {}'.format(line, state))
        if state == StreamParser.State.PARSE_DATA:
            print('  Data Parser State: {}'.format(parser.dataParser.state))

        if parser.isTerminated():
            print('Parser Terminated')
            break

    print('\n----------- End parsing -----------\n')

    assert state == testCase.expectedState

    if state == StreamParser.State.DONE:
        assert stream is not None

        print('Channel: {}'.format(stream.channel))
        print('Stream-Type: {}'.format(stream.streamType))

        print('Stream-Data: {}'.format(stream.data))

        assert stream.data == testCase.expectedData

    print('\n=================== Case End ===================')

    parser.reset()
