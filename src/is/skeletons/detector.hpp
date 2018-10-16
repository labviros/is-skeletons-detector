#pragma once

#include <memory>
#include <is/wire/core/logger.hpp>
#include <is/msgs/image.pb.h>
#include "options.pb.h"

#include <openpose/core/headers.hpp>
#include <openpose/filestream/headers.hpp>
#include <openpose/gui/headers.hpp>
#include <openpose/pose/headers.hpp>
#include <openpose/utilities/headers.hpp>

using namespace is::vision;

class SkeletonsDetector {
 public:
  SkeletonsDetector(is::SkeletonsDetectorOptions const& options);
  ObjectAnnotations detect(Image const& pb_image, int64_t const& camera_id = 0);
  ObjectAnnotations detect(cv::Mat const& cv_image, int64_t const& camera_id = 0);
  cv::Mat last_image();

 private:
  is::SkeletonsDetectorOptions options;
  std::unique_ptr<op::ScaleAndSizeExtractor> scale_and_size_extractor;
  std::unique_ptr<op::PoseExtractorCaffe> pose_extractor;
  std::unique_ptr<op::CvMatToOpInput> cvmat_to_input;

  op::PoseModel pose_model;
  op::Point<int> net_input_size;
  op::Point<int> output_size;
  int32_t scale_number;
  double scale_gap;
  cv::Mat last_cv_image;

  ObjectAnnotations make_skeletons(op::Array<float> const& keypoints,
                                   op::Point<int> const& image_size,
                                   int64_t const& frame_id);
  HumanKeypoints get_human_keypoint(std::string const& name);
};