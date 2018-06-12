import re
import sys
import cv2
from threading import Timer
from skeletons_utils import draw_skeletons, get_pb_image, load_options
from skeletons_pb2 import Skeletons
from is_msgs.image_pb2 import Image
from is_wire.core import Channel, Subscription, Message, Logger, ZipkinTracer
from is_wire.rpc import LogInterceptor

op = load_options()
log = Logger()

images = {}
timers = {}

c = Channel(op.broker_uri)
sb = Subscription(c)
tracer = ZipkinTracer(host_name=op.zipkin_host, port=op.zipkin_port, service_name='Skeletons')

log_int = LogInterceptor()

@tracer.interceptor('Render')
def on_skeletons(msg, context):
    skeletons = msg.unpack(Skeletons)
    log_context = {'service_name': 'Skeletons.{}.Render'.format(op.render_topic)}
    log_context = log_int.before_call(log_context)

    metadata = msg.metadata()
    rendered_msg = None
    if 'x-b3-traceid' in metadata and skeletons:
        trace_id = metadata['x-b3-traceid']
        if trace_id in images:
            try:
                rendered_image = draw_skeletons(images[trace_id], skeletons)
                rendered_msg = Message()
                rendered_msg.pack(get_pb_image(rendered_image))          \
                    .set_topic('Skeletons.{}.Rendered'.format(op.render_topic)) \
                    .add_metadata(context)
                log_context['rpc-status'] = {'code': 'OK'}
            except Exception as ex:
                why = 'Failed to render image.\n{}'.format(ex)
                log_context['rpc-status'] = {'code': 'INTERNAL_ERROR', 'why': why}
            if trace_id in images:
                del images[trace_id]
        else:
            why = 'Image with trace-id \'{}\' doesn\'t exist'.format(trace_id)
            log_context['rpc-status'] = {'code': 'FAILED_PRECONDITION', 'why': why}        
        
        if trace_id in timers:
            timers[trace_id].cancel()
            del timers[trace_id]
    else:
        why = 'Skelton message without trace information'
        log_context['rpc-status'] = {'code': 'FAILED_PRECONDITION', 'why': why}        

    log_context = log_int.after_call(log_context)
    if rendered_msg:
        c.publish(rendered_msg)

def on_image(msg, context):
    image = msg.unpack(Image)
    metadata = msg.metadata()
    if 'x-b3-traceid' in metadata and image:
        trace_id = metadata['x-b3-traceid']
        images[trace_id] = image
        def on_timeout(trace_id):
            if trace_id in images:
                del images[trace_id]
            del timers[trace_id]
        timers[trace_id] = Timer(60.0, on_timeout, [trace_id])
        timers[trace_id].start()

sb.subscribe('Skeletons.{}.Detections'.format(op.render_topic), on_skeletons)
sb.subscribe('CameraGateway.{}.Frame'.format(op.render_topic), on_image)
c.listen()