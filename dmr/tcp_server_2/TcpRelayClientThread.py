import logging
import threading, socket
import json
from queue import Queue

l = logging.getLogger(__name__)
class TcpRelayClientThread():
    def __init__(self, sock, addr, client_thread_dict):
        self.sock = sock
        self.addr = addr
        self.client_thread_dict = client_thread_dict
        self.video_width = None
        self.video_height = None
        self.queue = Queue()

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        try:
            while True:
                data = self.sock.recv(16384)
                try:
                    jsonobj = json.loads(data.decode('utf-8'))
                    mode = jsonobj['mode']
                    cam_id = jsonobj['cam_id']
                    # mode 1: send, mode 0: receive
                    l.info('mode: {}, requested cam_id: {}'.format(mode, cam_id))
                    if cam_id not in self.client_thread_dict:
                        self.client_thread_dict[cam_id] = []
                    client_list = self.client_thread_dict[cam_id]
                    if mode == 1:
                        l.info('{"video_width": ' + str(jsonobj['video_width']) + ', "video_height": ' + str(jsonobj['video_height']) + '}')
                        while True:
                            data = self.sock.recv(16384)
                            if not data:
                                break
                            #result = dill.loads(data)
                            #json_str = json.dumps(result, default=lambda o: o.__dict__)
                            json_str = data.decode('utf-8')
                            #l.info('json_str: {}'.format(json_str))
                            for client in client_list:
                                if client.video_width is None:
                                    client.video_width = jsonobj['video_width']
                                    client.video_height = jsonobj['video_height']
                                client.queue.put(json_str)
                    elif mode == 0:
                        # 클라이언트가 연결에서 끊어졌을 때 queue를 client_list에서 제거해야됨
                        client_list.append(self)
                        sent_resolution = False
                        while True:
                            item = self.queue.get()
                            #item = None ##
                            #l.info(f'result: {item}')
                            if not sent_resolution:
                                #self.sock.sendall('{"video_width": 640, "video_height": 480}\n'.encode('utf-8')) ##
                                self.sock.sendall(('{"video_width": ' + str(self.video_width) + ', "video_height": ' + str(self.video_height) + '}\n').encode('utf-8'))
                                sent_resolution = True
                            self.sock.sendall(item.encode('utf-8'))
                            #self.sock.sendall('{"timestamp": 0.0, "boxes": [{"x": 122, "y": 36, "width": 29, "height": 99, "confidence": 0.7901222109794617, "classID": 73, "label": "book"}, {"x": 143, "y": 33, "width": 32, "height": 102, "confidence": 0.7653483152389526, "classID": 73, "label": "book"}, {"x": 69, "y": 47, "width": 37, "height": 79, "confidence": 0.6571048498153687, "classID": 73, "label": "book"}, {"x": 192, "y": 60, "width": 24, "height": 82, "confidence": 0.6541954874992371, "classID": 73, "label": "book"}, {"x": 92, "y": 46, "width": 37, "height": 84, "confidence": 0.6088696718215942, "classID": 73, "label": "book"}, {"x": 316, "y": 57, "width": 33, "height": 81, "confidence": 0.5515491962432861, "classID": 73, "label": "book"}, {"x": 260, "y": 50, "width": 50, "height": 93, "confidence": 0.547731339931488, "classID": 73, "label": "book"}, {"x": 123, "y": 133, "width": 261, "height": 195, "confidence": 0.5067321062088013, "classID": 62, "label": "tvmonitor"}, {"x": 166, "y": 37, "width": 31, "height": 99, "confidence": 0.46987318992614746, "classID": 73, "label": "book"}, {"x": 313, "y": 1, "width": 27, "height": 47, "confidence": 0.3665698170661926, "classID": 73, "label": "book"}]}\n'.encode('utf-8'))
                            self.queue.task_done()
                except ValueError:
                    l.info(f'incorrect data: {data}')
                    break
        except socket.error as e:
            l.info(f'error from {self.addr}')
            l.exception(e)
