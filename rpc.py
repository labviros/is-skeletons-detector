from is_wire.core import Channel, ZipkinTracer, Logger
from is_wire.rpc import ServiceProvider, LogInterceptor
from is_msgs.image_pb2 import Image
from skeletons_pb2 import Skeletons
from skeletons import SkeletonsDetector
from skeletons_utils import load_options

op = load_options()
sd = SkeletonsDetector(op)

log = Logger()
c = Channel(op.broker_uri)
log.info('Connected to broker {}', op.broker_uri)
tracer = ZipkinTracer(host_name=op.zipkin_host, port=op.zipkin_port, service_name='Skeletons')
c.set_tracer(tracer)
log_int = LogInterceptor()
provider = ServiceProvider(c)
provider.add_interceptor(log_int)

def get_skeletons(image):
    skeletons = sd.detect(image)
    return skeletons, {'code': 'OK'}

provider.delegate('Skeletons.Detect', Image, Skeletons, get_skeletons)

c.listen()