import re
from is_wire.core import Channel, Subscription, Message, Logger, ZipkinTracer
from is_wire.rpc import LogInterceptor
from is_msgs.image_pb2 import Image
from skeletons import SkeletonsDetector
from skeletons_utils import load_options, get_np_image, get_pb_image, draw_skeletons

op = load_options()
sd = SkeletonsDetector(op)

log = Logger()
c = Channel(op.broker_uri)
log.info('Connected to broker {}', op.broker_uri)
sb = Subscription(c, 'Skeletons.Detector')
tracer = ZipkinTracer(host_name=op.zipkin_host, port=op.zipkin_port, service_name='Skeletons')
log_int = LogInterceptor()
re_topic = re.compile(r'CameraGateway.(\w+).Frame')

def render(q):
    cr = Channel(op.broker_uri)
    while True:
        img, skeletons, context, topic = q.get()
        span1 = tracer.start_span('render', context=context)
        img_rendered = draw_skeletons(img, skeletons)
        tracer.end_span(span1)

        span2 = tracer.start_span('encode_rendered', context=context)
        img_rendered_pb = get_pb_image(img_rendered)
        tracer.end_span(span2)

        topic_rendered = re_topic.sub(r'Skeletons.\1.Rendered', topic)
        msg = Message()
        msg.pack(img_rendered_pb).set_topic(topic_rendered)
        cr.publish(msg)
        q.task_done()

@tracer.interceptor('Detect')
def on_image(msg, context):
    log_context = {'service_name': 'Skeletons.Detect'}
    log_context = log_int.before_call(log_context)
    
    im = msg.unpack(Image)
    msg_reply = None
    if im:
        try:
            # convert image to numpy
            im_np = get_np_image(im)
            # detect skeletons
            skeletons = sd.detect(im_np)
            # create Skeletons message and publish
            msg_reply = Message()
            topic = re_topic.sub(r'Skeletons.\1.Detections', msg.topic())
            msg_reply.pack(skeletons).set_topic(topic).add_metadata(context)
            c.publish(msg_reply)
            # render skeletons
            img_rendered = draw_skeletons(im_np, skeletons)
            # converte image to protobuf Image
            img_rendered_pb = get_pb_image(img_rendered)
            # serialize and publish rendered image
            topic_rendered = re_topic.sub(r'Skeletons.\1.Rendered', msg.topic())
            msg_rendered = Message()
            msg_rendered.pack(img_rendered_pb).set_topic(topic_rendered)
            c.publish(msg_rendered)
            #
            log_context['rpc-status'] = {'code': 'OK'}
        except Exception as ex:
            why = 'Can\'t detect skeletons on image from {}.\n{}'.format(msg.topic(), ex)
            log_context['rpc-status'] = {'code': 'INTERNAL_ERROR', 'why': why}
    else:
        why = 'Expected message type \'{}\' but received something else'.format(Image.DESCRIPTOR.full_name)
        log_context['rpc-status'] = {'code': 'FAILED_PRECONDITION', 'why': why}

    log_context = log_int.after_call(log_context)


sb.subscribe('CameraGateway.*.Frame', on_image)
c.listen()