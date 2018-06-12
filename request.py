import cv2
import numpy as np
import time
from skeletons_utils import draw_skeletons
from is_msgs.image_pb2 import Image
from skeletons_pb2 import Skeletons
from is_wire.core import Channel, Subscription, Message, Logger

c = Channel()
sb = Subscription(c)
log = Logger()
image = cv2.imread('image.png')

def on_skeletons(msg, context):
    skeletons = msg.unpack(Skeletons)
    im_skeletons = draw_skeletons(image, skeletons)
    cv2.imshow('{} Skeletons'.format(len(skeletons.skeletons)), im_skeletons)
    cv2.waitKey(0)

cimage = cv2.imencode('.png', image)
data = cimage[1].tobytes()
im = Image(data=data)
msg = Message()
msg.pack(im)                       \
    .set_topic('Skeletons.Detect') \
    .set_reply_to(sb)              \
    .set_on_reply(on_skeletons)

c.publish(msg)
c.listen()