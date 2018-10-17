#include "utils.hpp"

is::SkeletonsDetectorOptions load_options(int argc, char** argv) {
  std::string filename = (argc == 2) ? argv[1] : "options.json";
  is::SkeletonsDetectorOptions options;
  try {
    is::load(filename, &options);
    is::validate_message(options);
  } catch (std::exception& e) { is::critical("{}", e.what()); }

  is::info("[SkeletonsDetectorOptions] \n{}", options);
  return options;
}

int64_t get_topic_id(std::string const& topic) {
  const auto id_regex = std::regex("CameraGateway.(\\d+).Frame");
  std::smatch matches;
  if (std::regex_match(topic, matches, id_regex))
    return std::stoi(matches[1]);
  else
    throw std::runtime_error(fmt::format("Wrong format topic: \'{}\'", topic));
}

std::shared_ptr<opentracing::Tracer> make_tracer(is::SkeletonsDetectorOptions const& options, std::string const& service_name) {
  ZipkinOtTracerOptions zp_options;
  zp_options.service_name = service_name;
  zp_options.collector_host = options.zipkin_host();
  zp_options.collector_port = options.zipkin_port();
  return makeZipkinOtTracer(zp_options);
}

void render_skeletons(cv::Mat& cv_image, is::vision::ObjectAnnotations const& skeletons, is::vision::Image* pb_image) {
  std::vector<int> base_values{0, 255, 85, 170};
  std::vector<cv::Scalar> colors;
  do {
    colors.push_back(cv::Scalar(base_values[0], base_values[1], base_values[2]));
    std::reverse(base_values.begin() + 3, base_values.end());
  } while (std::next_permutation(base_values.begin(), base_values.end()));

  const std::vector<std::pair<is::vision::HumanKeypoints, is::vision::HumanKeypoints>> links{
      {is::vision::HumanKeypoints::HEAD, is::vision::HumanKeypoints::NECK},                   // MPI
      {is::vision::HumanKeypoints::NECK, is::vision::HumanKeypoints::CHEST},                  // MPI
      {is::vision::HumanKeypoints::CHEST, is::vision::HumanKeypoints::RIGHT_HIP},             // MPI
      {is::vision::HumanKeypoints::CHEST, is::vision::HumanKeypoints::LEFT_HIP},              // MPI
      {is::vision::HumanKeypoints::NECK, is::vision::HumanKeypoints::LEFT_SHOULDER},          // COCO & MPI
      {is::vision::HumanKeypoints::LEFT_SHOULDER, is::vision::HumanKeypoints::LEFT_ELBOW},    // COCO & MPI
      {is::vision::HumanKeypoints::LEFT_ELBOW, is::vision::HumanKeypoints::LEFT_WRIST},       // COCO & MPI
      {is::vision::HumanKeypoints::NECK, is::vision::HumanKeypoints::LEFT_HIP},               // COCO
      {is::vision::HumanKeypoints::LEFT_HIP, is::vision::HumanKeypoints::LEFT_KNEE},          // COCO & MPI
      {is::vision::HumanKeypoints::LEFT_KNEE, is::vision::HumanKeypoints::LEFT_ANKLE},        // COCO & MPI
      {is::vision::HumanKeypoints::NECK, is::vision::HumanKeypoints::RIGHT_SHOULDER},         // COCO & MPI
      {is::vision::HumanKeypoints::RIGHT_SHOULDER, is::vision::HumanKeypoints::RIGHT_ELBOW},  // COCO & MPI
      {is::vision::HumanKeypoints::RIGHT_ELBOW, is::vision::HumanKeypoints::RIGHT_WRIST},     // COCO & MPI
      {is::vision::HumanKeypoints::NECK, is::vision::HumanKeypoints::RIGHT_HIP},              // COCO
      {is::vision::HumanKeypoints::RIGHT_HIP, is::vision::HumanKeypoints::RIGHT_KNEE},        // COCO & MPI
      {is::vision::HumanKeypoints::RIGHT_KNEE, is::vision::HumanKeypoints::RIGHT_ANKLE},      // COCO & MPI
      {is::vision::HumanKeypoints::NOSE, is::vision::HumanKeypoints::LEFT_EYE},               // COCO
      {is::vision::HumanKeypoints::LEFT_EYE, is::vision::HumanKeypoints::LEFT_EAR},           // COCO
      {is::vision::HumanKeypoints::NOSE, is::vision::HumanKeypoints::RIGHT_EYE},              // COCO
      {is::vision::HumanKeypoints::RIGHT_EYE, is::vision::HumanKeypoints::RIGHT_EAR}          // COCO
  };

  for (auto& skeleton : skeletons.objects()) {
    std::map<is::vision::HumanKeypoints, cv::Point> joints;
    for (auto& joint : skeleton.keypoints()) {
      auto id = static_cast<is::vision::HumanKeypoints>(joint.id());
      joints[id] = cv::Point(joint.position().x(), joint.position().y());
    }
    // draw links
    for (unsigned int k = 0; k < std::min(colors.size(), links.size()); ++k) {
      auto begin_joint = joints.find(links[k].first);
      auto end_joint = joints.find(links[k].second);
      if (begin_joint == joints.end() || end_joint == joints.end()) continue;
      cv::line(cv_image, begin_joint->second, end_joint->second, colors[k], 4);
    }
    // draw joints
    for (auto& joint : joints) {
      cv::circle(cv_image, joint.second, 4, cv::Scalar(255, 255, 255), -1);
    }
  }

  if (pb_image != nullptr) {
    std::vector<unsigned char> image_data;
    cv::imencode(".jpeg", cv_image, image_data, {cv::IMWRITE_JPEG_QUALITY, 80});
    auto compressed_data = pb_image->mutable_data();
    compressed_data->resize(image_data.size()); 
    std::copy(image_data.begin(), image_data.end(), compressed_data->begin());
  }
}

is::Message StreamChannel::consume_last(int* dropped) {
  std::vector<is::Message> msgs;
  is::Message msg = this->channel.consume();
  msgs.push_back(msg);
  while (true) {
    auto maybe_msg = this->channel.consume_for(std::chrono::milliseconds(0));
    if (maybe_msg)
      msgs.push_back(maybe_msg.get());
    else
      break;
  }

  if (dropped != nullptr) *dropped = msgs.size() - 1;
  return msgs.back();
}

void StreamChannel::publish(std::string const& topic, is::Message const& message) {
  this->channel.publish(topic, message);
}
