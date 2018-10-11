import re
import sys
import cv2
import time
import numpy as np
from is_msgs.image_pb2 import Image, ObjectAnnotations
from is_wire.core import Channel, Subscription, Message, Logger
from is_wire.core import Tracer, ZipkinExporter, BackgroundThreadTransport

log = Logger(name='Publisher')

broker_uri = 'amqp://localhost:5672'
if len(sys.argv) > 2:
    log.critical('Invalid arguments. Try: python requester.py <BROKER_URI>')
if len(sys.argv) > 1:
    broker_uri = sys.argv[1]

channel = Channel(broker_uri)
subscription = Subscription(channel)
exporter = ZipkinExporter(
    service_name='SkeletonsDetectorRequester',
    host_name='localhost',
    port=9411,
    transport=BackgroundThreadTransport(max_batch_size=100),
)

image = cv2.imread('../image.png')

tracer = Tracer(exporter)
with tracer.span(name='image') as span:
    cimage = cv2.imencode(ext='.jpeg', img=image, params=[cv2.IMWRITE_JPEG_QUALITY, 80])
    data = cimage[1].tobytes()
    im = Image(data=data)
    msg = Message(content=im, reply_to=subscription)
    msg.inject_tracing(span)
    channel.publish(message=msg, topic='SkeletonsDetector.Detect')

    cid = msg.correlation_id
    while True:
        msg = channel.consume()
        if msg.correlation_id == cid:
            skeletons = msg.unpack(ObjectAnnotations)
            print(skeletons)
            sys.exit(0)
