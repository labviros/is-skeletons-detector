import re
from functools import partial

from is_wire.core import Channel, Message, Status, StatusCode, Logger
from is_wire.core import Tracer, ZipkinExporter, BackgroundThreadTransport
from is_wire.rpc import ServiceProvider, LogInterceptor, TracingInterceptor
from is_msgs.image_pb2 import Image, ObjectAnnotations

from .skeletons import SkeletonsDetector
from .utils import load_options


class RPCSkeletonsDetector:
    def __init__(self, options):
        self._sd = SkeletonsDetector(options)

    def detect(self, image, ctx):
        try:
            return self._sd.detect(image)
        except:
            return Status(code=StatusCode.INTERNAL_ERROR)


def main():
    service_name = 'SkeletonsDetector.Detect'

    op = load_options()
    sd = RPCSkeletonsDetector(op)

    log = Logger(name=service_name)
    channel = Channel(op.broker_uri)
    log.info('Connected to broker {}', op.broker_uri)
    provider = ServiceProvider(channel)
    provider.add_interceptor(LogInterceptor())

    max_batch_size = max(100, op.zipkin_batch_size)
    exporter = ZipkinExporter(
        service_name=service_name,
        host_name=op.zipkin_host,
        port=op.zipkin_port,
        transport=BackgroundThreadTransport(max_batch_size=max_batch_size),
    )
    tracing = TracingInterceptor(exporter=exporter)

    provider.delegate(
        topic='SkeletonsDetector.Detect',
        function=partial(RPCSkeletonsDetector.detect, sd),
        request_type=Image,
        reply_type=ObjectAnnotations)
    
    provider.run()

if __name__ == "__main__":
    main()