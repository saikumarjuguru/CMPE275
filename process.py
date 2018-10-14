import sample_pb2
import sample_pb2_grpc
import grpc
from concurrent import futures
import time
import threading
import collections

mq = collections.deque([])
my_ip = "localhost:4000"
next_ip = "localhost:4001"


class DataTransfer(sample_pb2_grpc.DataTransferServicer):
    def __init__(self):
        pass

    def sendMessage(self, request, context):
        if(request.dest == my_ip):
            print("%s : %s" % (request.origin, request.msg))
        else:
            mq.append(request)
        return sample_pb2.Empty()

    def recvMessage(self, request, context):
        pass


def serve():
    chat = DataTransfer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    sample_pb2_grpc.add_DataTransferServicer_to_server(chat, server)
    server.add_insecure_port(my_ip)
    server.start()
    inmsg = sample_pb2.InputMessage(origin=my_ip)
    try:
        while True:
            msg_dest = input("Enter message and destination:").split(";")
            inmsg.msg, inmsg.dest = msg_dest[0], msg_dest[1]
            mq.append(inmsg)
    except KeyboardInterrupt:
        pass


def run():
    stub = sample_pb2_grpc.DataTransferStub(
        grpc.insecure_channel(next_ip))  # server on another client
    try:
        while True:
            if len(mq) == 0:
                continue
            else:
                stub.sendMessage(mq.popleft())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    t1 = threading.Thread(target=serve)
    t2 = threading.Thread(target=run)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
