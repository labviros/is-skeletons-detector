import re
import sys
import cv2
from skeletons_utils import get_np_image
from is_msgs.image_pb2 import Image
from is_wire.core import Channel, Subscription, Message, Logger

log = Logger()
re_uri = re.compile(r'amqp:\/\/[\w0-9\.]+[:][0-9]+$')
re_id = re.compile(r'[\w]+$')

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

c = Channel(broker_uri)
sb = Subscription(c)
topic = 'Skeletons.{}.Rendered'.format(topic_id)

def on_image(msg, context):
    rendered_image = msg.unpack(Image)
    log.info('New image')
    if rendered_image:
        cv2.imshow(topic, get_np_image(rendered_image))
        cv2.waitKey(1)

sb.subscribe(topic, on_image)
c.listen()