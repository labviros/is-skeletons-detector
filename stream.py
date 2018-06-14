import re
from is_wire.core import Channel, Subscription, Message, Logger, ZipkinTracer
from is_wire.rpc import LogInterceptor
from is_msgs.image_pb2 import Image
from skeletons import SkeletonsDetector
from skeletons_utils import load_options, get_np_image, get_pb_image, draw_skeletons

from time import time

op = load_options()
sd = SkeletonsDetector(op)

log = Logger()
c = Channel(op.broker_uri)
log.info('Connected to broker {}', op.broker_uri)
sb = Subscription(c, 'Skeletons.Detector')
tracer = ZipkinTracer(host_name=op.zipkin_host, port=op.zipkin_port, service_name='Skeletons')
log_int = LogInterceptor()
re_topic = re.compile(r'CameraGateway.(\w+).Frame')

@tracer.interceptor('Detect')
def on_image(msg, context):
    log_context = {'service_name': 'Skeletons.Detect'}
    log_context = log_int.before_call(log_context)
    
    im = msg.unpack(Image)
    msg_reply = None
    msg_rendered = None
    if im:
        try:
            t0 = time()
            im_np = get_np_image(im)
            t1 = time()
            skeletons = sd.detect(im_np)
            t2 = time()
            msg_reply = Message()
            topic = re_topic.sub(r'Skeletons.\1.Detections', msg.topic())
            msg_reply.pack(skeletons).set_topic(topic).add_metadata(context)
            t3 = time()
            im_rendered = draw_skeletons(im_np, skeletons)
            t4 = time()
            msg_rendered = Message()
            topic_rendered = re_topic.sub(r'Skeletons.\1.Rendered', msg.topic())
            msg_rendered.pack(get_pb_image(im_rendered)).set_topic(topic_rendered)
            t5 = time()
            d1 = 1000.0*(t1 - t0)
            d2 = 1000.0*(t2 - t1)
            d3 = 1000.0*(t3 - t2)
            d4 = 1000.0*(t4 - t3)
            d5 = 1000.0*(t5 - t4)
            log.info('Decode: {:.2f}ms | Detect: {:.2f}ms | PackSk: {:.2f}ms | Render: {:.2f}ms | PackIm: {:.2f}ms', d1, d2, d3, d4, d5)

            log_context['rpc-status'] = {'code': 'OK'}
        except Exception as ex:
            why = 'Can\'t detect skeletons on image from {}.\n{}'.format(msg.topic(), ex)
            log_context['rpc-status'] = {'code': 'INTERNAL_ERROR', 'why': why}
    else:
        why = 'Expected message type \'{}\' but received something else'.format(Image.DESCRIPTOR.full_name)
        log_context['rpc-status'] = {'code': 'FAILED_PRECONDITION', 'why': why}

    log_context = log_int.after_call(log_context)
    
    if msg_reply:
        c.publish(msg_reply)
    if msg_rendered:
        c.publish(msg_rendered)

sb.subscribe('CameraGateway.*.Frame', on_image)
c.listen()