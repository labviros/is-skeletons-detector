import re
from is_wire.core import Channel, Subscription, Message, Logger, ZipkinTracer
from is_wire.rpc import LogInterceptor
from is_msgs.image_pb2 import Image
from skeletons import SkeletonsDetector
from skeletons_utils import load_options

op = load_options()
sd = SkeletonsDetector(op)

log = Logger()
c = Channel(op.broker_uri)
log.info('Connected to broker {}', op.broker_uri)
sb = Subscription(c)
tracer = ZipkinTracer(host_name=op.zipkin_host, port=op.zipkin_port, service_name='Skeletons')
log_int = LogInterceptor()
re_topic = re.compile(r'CameraGateway.(\w+).Frame')

@tracer.interceptor('Detect')
def on_image(msg, context):
    log_context = {'service_name': 'Skeletons.Detect'}
    log_context = log_int.before_call(log_context)
    
    im = msg.unpack(Image)
    msg_reply = None
    if im:
        try:
            skeletons = sd.detect(im)
            msg_reply = Message()
            topic = re_topic.sub(r'Skeletons.\1.Detections', msg.topic())
            msg_reply.pack(skeletons).set_topic(topic).add_metadata(context)
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
        

sb.subscribe('CameraGateway.*.Frame', on_image)
c.listen()