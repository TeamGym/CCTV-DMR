# Run as client

from threading import Condition

from dmr.rsp import RspConnection, EndpointType, Request, Stream
from dmr.rsp.stream_data import ControlPTZ

#REMOTE=('192.168.141.10', 50002)
REMOTE=('127.0.0.1', 50002)

exitCondition = Condition()

def onGetInfoResponse(response):
    print('get info response from server: \n{}'.format(response.getMessageString()))
    exitCondition.acquire()
    exitCondition.notify()
    exitCondition.release()

conn = RspConnection.makeConnection(
        endpointType=EndpointType.APP,
        remote=REMOTE)

print('send request')
conn.sendRequest(Request(
    method=Request.Method.GET_INFO,
    onResponseCallback=onGetInfoResponse))

print('send stream')
conn.sendStream(Stream(
    sessionID=2,
    streamType=Stream.Type.CONTROL_PTZ,
    data=ControlPTZ(
        pan=3,
        tilt=-10,
        zoom=1)))

exitCondition.acquire()
exitCondition.wait()
exitCondition.release()
