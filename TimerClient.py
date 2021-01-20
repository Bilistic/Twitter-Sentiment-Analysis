import pika
import uuid
import Messenger
import time
import datetime


class TweetRPCClient(Messenger.Messenger):

    def __init__(self, name, host="localhost"):
        Messenger.Messenger.__init__(self, name=name, host=host)
        self.response = None
        self.corr_id = None
        self._channel.basic_consume(self.on_response, no_ack=True, queue=self._callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, data):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self._channel.basic_publish(exchange='', routing_key='data_stream', properties=pika.BasicProperties(
                                         reply_to=self._callback_queue, correlation_id=self.corr_id,), body=str(["get", data]))
        retries = 10
        while self.response is None:
            if retries == 0:
                self.response = bytes(str([]), 'utf-8')
                break
            self._connection.process_data_events()
            retries -= 1
            time.sleep(0.5)
        return self.response


if __name__ == '__main__':
    client = TweetRPCClient("web-client")
    print(" [x] Requesting fib(30)")
    response = client.call(30)
    response = eval(response.decode("utf-8"))
    client.close()
    print(" [.] Got {}".format(response))
