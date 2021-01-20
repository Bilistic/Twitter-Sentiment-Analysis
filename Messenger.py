import pika
import time


class Messenger(object):

    def __init__(self, name, host="localhost"):
        self.name = name
        self.host = host
        credentials = pika.PlainCredentials('admin', 'admin')
        retries = 10
        while True:
            try:
                self._connection = pika.BlockingConnection(pika.ConnectionParameters(host, credentials=credentials))
                break
            except Exception as e:
                if retries == 0:
                    raise e
                retries -= 1
                time.sleep(0.5)


        self._channel = self._connection.channel()
        result = self._channel.queue_declare(exclusive=True)
        self._callback_queue = result.method.queue
        self.test_connection()


    '''
    configures the messenger to listen for incoming data indefinitely
    '''
    def listen(self, callback=None):
        if not callback:
            callback = self.callback
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(callback, queue='data_stream')
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self._channel.start_consuming()

    '''
    connects...
    '''
    def connect(self):
        self.close()
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self._channel = self._connection.channel()
        result = self._channel.queue_declare(exclusive=True)
        self._callback_queue = result.method.queue
        self.test_connection()


    '''
    Tests the connection with a random message PIKA will drop this message as it has no recipient
    '''
    def test_connection(self):
        self._channel.queue_declare(queue='data_stream', durable=True)

    '''
    Sends a message to an exchange
    '''
    def send(self, exchange, routing_key, body):
        self._channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body, properties=pika.BasicProperties(
                         delivery_mode=2, reply_to=self._callback_queue,
                      ))
        print(" {} Sent {} -> {}".format(self.name, body, routing_key))

    '''
    Closes the current connection
    '''
    def close(self):
        self._connection.close()

    def callback(self, ch, method, properties, body):
        print(" {} Received {}".format(self.name, body))
        ch.basic_ack(delivery_tag=method.delivery_tag)
