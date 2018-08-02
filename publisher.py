import re
import sys
import cv2
import numpy as np
import time
from is_msgs.image_pb2 import Image
from is_wire.core import Channel, Message, Logger
from is_wire.core import Tracer, ZipkinExporter, BackgroundThreadTransport

log = Logger(name='Publisher')

topic_id = 0
broker_uri='amqp://localhost:5672'
if len(sys.argv) != 3 and len(sys.argv) != 1:
    log.critical('Invalid arguments. Try: python render.py <BROKER_URI> <TOPIC_ID>')
if len(sys.argv) > 1:
    broker_uri = sys.argv[1]
    topic_id = sys.argv[2]

channel = Channel(broker_uri)
exporter = ZipkinExporter(
    service_name='CameraGateway.{}'.format(topic_id),
    host_name='localhost',
    port=9411,
    transport=BackgroundThreadTransport,
)

image = cv2.imread('image.png')

for k in range(10):
    tracer = Tracer(exporter)
    with tracer.span(name='image') as span:
        cimage = cv2.imencode(
            ext='.jpeg',
            img=image,
            params=[cv2.IMWRITE_JPEG_QUALITY, 80]
        )
        data = cimage[1].tobytes()
        im = Image(data=data)
        msg = Message()
        msg.topic = 'CameraGateway.{}.Frame'.format(topic_id)
        msg.inject_tracing(span)
        msg.metadata.update({'image_id': k})
        msg.pack(im)
        channel.publish(msg)
        log.info('Message {} published', k)
    time.sleep(0.250)