#include "detector.hpp"

SkeletonsDetector::SkeletonsDetector(is::SkeletonsDetectorOptions const& options)
    : options(options), scale_number(1), scale_gap(0.3) {
  int w = -1;
  int h = -1;
  if (options.has_output_resolution()) {
    w = options.output_resolution().width();
    h = options.output_resolution().height();
  }
  this->output_size = op::flagsToPoint(fmt::format("{}x{}", w, h), "-1x-1");

  w = -1;
  h = 368;
  if (options.has_network_resolution()) {
    w = options.network_resolution().width();
    h = options.network_resolution().height();
  }
  this->net_input_size = op::flagsToPoint(fmt::format("{}x{}", w, h), "-1x368");

  if (options.has_scale_number()) this->scale_number = options.scale_number().value();
  if (options.has_scale_gap()) this->scale_gap = options.scale_gap().value();

  if (this->scale_gap <= 0. && this->scale_number > 1) {
    is::critical(
        "Incompatible flag configuration: scale_gap ({:.1f}) must be greater than 0 or scale_number ({}) equals 1",
        this->scale_gap,
        this->scale_number);
  }

  const google::protobuf::EnumDescriptor* descriptor = is::SkeletonsDetectorOptions_Model_descriptor();
  this->pose_model = op::flagsToPoseModel(descriptor->FindValueByNumber(options.model())->name());

  this->scale_and_size_extractor = std::unique_ptr<op::ScaleAndSizeExtractor>(
      new op::ScaleAndSizeExtractor(this->net_input_size, this->output_size, this->scale_number, this->scale_gap));
  this->cvmat_to_input = std::unique_ptr<op::CvMatToOpInput>(new op::CvMatToOpInput(this->pose_model));
  this->pose_extractor = std::unique_ptr<op::PoseExtractorCaffe>(
      new op::PoseExtractorCaffe(this->pose_model, options.models_folder(), options.num_gpu_start()));

  this->pose_extractor->initializationOnThread();
}

ObjectAnnotations SkeletonsDetector::detect(Image const& pb_image, int64_t const& camera_id) {
  std::vector<char> coded(pb_image.data().begin(), pb_image.data().end());
  auto cv_image = cv::imdecode(coded, CV_LOAD_IMAGE_COLOR);
  return this->detect(cv_image, camera_id);
}

ObjectAnnotations SkeletonsDetector::detect(cv::Mat const& cv_image, int64_t const& camera_id) {
  const op::Point<int> image_size{cv_image.cols, cv_image.rows};

  std::vector<double> scale_input_to_netinputs;
  std::vector<op::Point<int>> net_inputs_size;
  double scale_input_to_output;
  op::Point<int> output_res;
  std::tie(scale_input_to_netinputs, net_inputs_size, scale_input_to_output, output_res) =
      this->scale_and_size_extractor->extract(image_size);
  const auto net_input_array = this->cvmat_to_input->createArray(cv_image, scale_input_to_netinputs, net_inputs_size);

  this->pose_extractor->forwardPass(net_input_array, image_size, scale_input_to_netinputs);

  const auto keypoints = pose_extractor->getPoseKeypoints();
  return make_skeletons(keypoints, image_size, camera_id);
}

ObjectAnnotations SkeletonsDetector::make_skeletons(op::Array<float> const& keypoints,
                                                    op::Point<int> const& image_size,
                                                    int64_t const& frame_id) {
  auto body_part = op::getPoseBodyPartMapping(this->pose_model);
  ObjectAnnotations skeletons;
  auto n_people = keypoints.getSize(0);
  auto n_parts = keypoints.getSize(1);
  for (auto n = 0; n < n_people; ++n) {
    auto sk = skeletons.add_objects();
    for (auto p = 0; p < n_parts; ++p) {
      auto base_index = keypoints.getSize(2) * (n * n_parts + p);
      auto x = keypoints[base_index];
      auto y = keypoints[base_index + 1];
      auto score = keypoints[base_index + 2];
      auto part_id = get_human_keypoint(body_part[p]);
      if ((x + y + score) > 0.0 && part_id != is::vision::HumanKeypoints::UNKNOWN_HUMAN_KEYPOINT) {
        auto kp = sk->add_keypoints();
        kp->mutable_position()->set_x(x);
        kp->mutable_position()->set_y(y);
        kp->set_id(part_id);
        kp->set_score(score);
      }
    }
    if (sk->keypoints_size() == 0) skeletons.mutable_objects()->RemoveLast();
  }
  skeletons.set_frame_id(frame_id);
  skeletons.mutable_resolution()->set_width(image_size.x);
  skeletons.mutable_resolution()->set_height(image_size.y);
  return skeletons;
}

is::vision::HumanKeypoints SkeletonsDetector::get_human_keypoint(std::string const& name) {
  const static std::unordered_map<std::string, is::vision::HumanKeypoints> to_human_keypoint{
      {"Head", is::vision::HumanKeypoints::HEAD},
      {"Nose", is::vision::HumanKeypoints::NOSE},
      {"Neck", is::vision::HumanKeypoints::NECK},
      {"RShoulder", is::vision::HumanKeypoints::RIGHT_SHOULDER},
      {"RElbow", is::vision::HumanKeypoints::RIGHT_ELBOW},
      {"RWrist", is::vision::HumanKeypoints::RIGHT_WRIST},
      {"LShoulder", is::vision::HumanKeypoints::LEFT_SHOULDER},
      {"LElbow", is::vision::HumanKeypoints::LEFT_ELBOW},
      {"LWrist", is::vision::HumanKeypoints::LEFT_WRIST},
      {"RHip", is::vision::HumanKeypoints::RIGHT_HIP},
      {"RKenee", is::vision::HumanKeypoints::RIGHT_KNEE},
      {"RAnkle", is::vision::HumanKeypoints::RIGHT_ANKLE},
      {"LHip", is::vision::HumanKeypoints::LEFT_HIP},
      {"LKenee", is::vision::HumanKeypoints::LEFT_KNEE},
      {"LAnkle", is::vision::HumanKeypoints::LEFT_ANKLE},
      {"REye", is::vision::HumanKeypoints::RIGHT_EYE},
      {"LEye", is::vision::HumanKeypoints::LEFT_EYE},
      {"REar", is::vision::HumanKeypoints::RIGHT_EAR},
      {"LEar", is::vision::HumanKeypoints::LEFT_EAR},
      {"Chest", is::vision::HumanKeypoints::CHEST}};

  auto pos = to_human_keypoint.find(name);
  return pos != to_human_keypoint.end() ? pos->second : is::vision::HumanKeypoints::UNKNOWN_HUMAN_KEYPOINT;
}