import re
import sys
import cv2
import numpy as np
from is_msgs.image_pb2 import Image
from is_wire.core import Channel, Subscription, Message, ZipkinTracer, Logger

broker_uri = 'amqp://localhost:5672'
topic_id = 0
if len(sys.argv) != 3 and len(sys.argv) != 1:
    log.critical('Invalid arguments. Try: python render.py <BROKER_URI> <TOPIC_ID>')
if len(sys.argv) > 1:
    broker_uri = sys.argv[1]
    if not re_uri.match(broker_uri):
        log.critical('Invalid broker uri \'{}\'. Use the pattern: amqp://<HOSTNAME>:<PORT>', broker_uri)
    topic_id = sys.argv[2]
    if not re_id.match(topic_id):
        log.critical('Invalid topic id \'{}\'. It must contains just [a-zA-Z0-9_] characters.', topic_id)

c = Channel()
sb = Subscription(c)
tracer = ZipkinTracer(service_name='CameraGateway.{}'.format(topic_id))
log = Logger()

image = cv2.imread('image.png')

for k in range(100):
    span = tracer.start_span('Frame')
    cimage = cv2.imencode('.png', image)
    data = cimage[1].tobytes()
    im = Image(data=data)
    msg = Message()
    topic = 'CameraGateway.{}.Frame'.format(topic_id)
    msg.pack(im).set_topic(topic).add_metadata(span)
    c.publish(msg)
    tracer.end_span(span)
