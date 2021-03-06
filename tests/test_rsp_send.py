import logging
import socket
import time
import threading
from dmr.rsp import Rsp, RspConnection, EndpointType
from dmr.rsp import Request, Response, Stream
from dmr.rsp.stream_data import DetectionResult, ControlPTZ

logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)s: %(message)s ',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG)

PORT = 54323

messages = [
        Request(
            method=Request.Method.JOIN,
            properties={
                'CamId': '0',
                'Port': '50605'}),

       # Response(
       #     statusCode=200,
       #     properties={
       #         'SessionID': '0'}),

        Stream(
            channel='20',
            streamType=Stream.Type.DETECTION_RESULT,
            data=DetectionResult(
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

        Stream(
            channel='21',
            streamType=Stream.Type.CONTROL_PTZ,
            data=ControlPTZ(
                pan=1,
                tilt=-1,
                zoom=1))
]

def serverOnJoin(request, returnResponse):
    print('server: request received')
    print('server: method: {}'.format(request.Method))
    returnResponse(Response(
            statusCode=200,
            properties={
                'SessionID': '0'}))

def serverStreamReceived(stream):
    print('server: stream received')
    print('server: stream channel: {}'.format(stream.channel))
    print('server: stream type: {}'.format(stream.streamType))

def runServer():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', PORT))
    server.listen(10)
    server.setblocking(True)

    (client, address) = server.accept()
    conn = RspConnection(EndpointType.DMR, client)
    conn.addRequestHandler(Request.Method.JOIN, serverOnJoin)
    conn.addStreamHandler(20, serverStreamReceived)
    conn.addStreamHandler(21, serverStreamReceived)
    conn.start()

def clientStreamReceived(stream):
    print('client: stream received')
    print('client: stream type: {}'.format(stream.streamType))

#RspConnection.makeConnection('127.0.0.1')

serverThread = threading.Thread(target=runServer)
serverThread.daemon = True
serverThread.start()

time.sleep(1)

conn = RspConnection.makeConnection(EndpointType.APP, ('127.0.0.1', PORT))
conn.addStreamHandler(21, clientStreamReceived)
conn.start()

def onResponse(response):
    print('client: response received')
    print('client: statusCode: {}'.format(response.statusCode))

print('client: add request')
conn.sendRequest(
        Request(
            method=Request.Method.JOIN,
            properties={
                'CamId': '0',
                'Port': '50605'},
            onResponseCallback=onResponse))

conn.sendStream(Stream(
            channel=20,
            streamType=Stream.Type.DETECTION_RESULT,
            data=DetectionResult(
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
                    label='person')])))


conn.sendStream(Stream(
            channel=21,
            streamType=Stream.Type.CONTROL_PTZ,
            data=ControlPTZ(
                pan=1,
                tilt=-1,
                zoom=1)))

time.sleep(10)
