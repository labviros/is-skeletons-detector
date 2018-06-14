from skeletons_utils import get_np_image, get_links
from options_pb2 import Options
from skeletons_pb2 import Skeleton, SkeletonPart, Skeletons, SkeletonModel, SkeletonPartType
from is_msgs.image_pb2 import Image
import cv2
import numpy as np
import tf_pose_estimation.common as common
from tf_pose_estimation.estimator import TfPoseEstimator
from tf_pose_estimation.networks import get_graph_path, model_wh

class SkeletonsDetector:
    def __init__(self, options):
        if not isinstance(options, Options):
            raise Exception('Invalid parameter on \'SkeletonsDetector\' constructor: not a Options type')
        self.__op = options
        model = '{}x{}'.format(self.__op.resize.width, self.__op.resize.height)
        w, h = model_wh(model)
        self.__resize_to_default = (w > 0 and h > 0)
        model_name = Options.Model.Name(self.__op.model).lower()
        graph_path = get_graph_path(model_name=model_name, base_path=self.__op.models_folder)
        self.__e = TfPoseEstimator(graph_path, target_size=(w, h))
        self.__to_sks_part = {
            0 : SkeletonPartType.Value('NOSE'),
            1 : SkeletonPartType.Value('NECK'),
            2 : SkeletonPartType.Value('RIGHT_SHOULDER'),
            3 : SkeletonPartType.Value('RIGHT_ELBOW'),
            4 : SkeletonPartType.Value('RIGHT_WRIST'),
            5 : SkeletonPartType.Value('LEFT_SHOULDER'),
            6 : SkeletonPartType.Value('LEFT_ELBOW'),
            7 : SkeletonPartType.Value('LEFT_WRIST'),
            8 : SkeletonPartType.Value('RIGHT_HIP'),
            9 : SkeletonPartType.Value('RIGHT_KNEE'),
            10: SkeletonPartType.Value('RIGHT_ANKLE'),
            11: SkeletonPartType.Value('LEFT_HIP'),
            12: SkeletonPartType.Value('LEFT_KNEE'),
            13: SkeletonPartType.Value('LEFT_ANKLE'),
            14: SkeletonPartType.Value('RIGHT_EYE'),
            15: SkeletonPartType.Value('LEFT_EYE'),
            16: SkeletonPartType.Value('RIGHT_EAR'),
            17: SkeletonPartType.Value('LEFT_EAR'),
            18: SkeletonPartType.Value('BACKGROUND')
        }

    '''
        @detect, image argument can be either a np.darray matrix
                 or an is_msgs.image_pb2.Image
    '''
    def detect(self, image):
        _image = get_np_image(image)
        humans = self.__e.inference(_image,             \
            resize_to_default=self.__resize_to_default, \
            upsample_size=self.__op.resize_out_ratio)

        im_h, im_w = _image.shape[:2]
        return self.__to_skeletons(humans, im_w, im_h)

    def __to_skeletons(self, humans, im_width, im_height):
        sks = Skeletons()
        for human in humans:
            sk = sks.skeletons.add()
            for part_id, bp in human.body_parts.items():
                part = sk.parts.add()
                part.x = bp.x * im_width
                part.y = bp.y * im_height
                part.type = self.__to_sks_part[part_id]
                part.score = bp.score
        sks.model = SkeletonModel.Value('COCO')
        return sks