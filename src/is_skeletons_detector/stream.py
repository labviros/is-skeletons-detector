import re
import dateutil.parser as dp

from is_wire.core import Subscription, Message, Logger
from is_wire.core import Tracer, ZipkinExporter, BackgroundThreadTransport
from is_msgs.image_pb2 import Image

from .stream_channel import StreamChannel
from .skeletons import SkeletonsDetector
from .utils import load_options, get_np_image, get_pb_image, draw_skeletons


def span_duration_ms(span):
    dt = dp.parse(span.end_time) - dp.parse(span.start_time)
    return dt.total_seconds() * 1000.0


def main():
    service_name = 'SkeletonsDetector.Detection'
    re_topic = re.compile(r'CameraGateway.(\w+).Frame')

    op = load_options()
    sd = SkeletonsDetector(op)

    log = Logger(name=service_name)
    channel = StreamChannel(op.broker_uri)
    log.info('Connected to broker {}', op.broker_uri)

    max_batch_size = max(100, op.zipkin_batch_size)
    exporter = ZipkinExporter(
        service_name=service_name,
        host_name=op.zipkin_host,
        port=op.zipkin_port,
        transport=BackgroundThreadTransport(max_batch_size=max_batch_size),
    )

    subscription = Subscription(channel=channel, name=service_name)
    subscription.subscribe('CameraGateway.*.Frame')

    while True:
        msg, dropped = channel.consume(return_dropped=True)

        tracer = Tracer(exporter, span_context=msg.extract_tracing())
        span = tracer.start_span(name='detection_and_render')
        detection_span = None

        with tracer.span(name='unpack'):
            im = msg.unpack(Image)
            im_np = get_np_image(im)
        with tracer.span(name='detection') as _span:
            skeletons = sd.detect(im_np)
            detection_span = _span
        with tracer.span(name='pack_and_publish_detections'):
            sks_msg = Message()
            sks_msg.topic = re_topic.sub(r'SkeletonsDetector.\1.Detection', msg.topic)
            sks_msg.inject_tracing(span)
            sks_msg.pack(skeletons)
            channel.publish(sks_msg)
        with tracer.span(name='render_pack_publish'):
            im_rendered = draw_skeletons(im_np, skeletons)
            rendered_msg = Message()
            rendered_msg.topic = re_topic.sub(r'SkeletonsDetector.\1.Rendered', msg.topic)
            rendered_msg.pack(get_pb_image(im_rendered))
            channel.publish(rendered_msg)

        span.add_attribute('Detections', len(skeletons.objects))
        tracer.end_span()
        log.info('detections = {:2d}, dropped_messages = {:2d}', len(skeletons.objects), dropped)
        log.info('took_ms = {{ detection: {:5.2f}, service: {:5.2f}}}',
                 span_duration_ms(detection_span), span_duration_ms(span))


if __name__ == "__main__":
    main()