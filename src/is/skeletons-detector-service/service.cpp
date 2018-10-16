#include <chrono>
#include "skeletons/utils.hpp"
#include "skeletons/detector.hpp"
#include <is/wire/core.hpp>
#include <is/msgs/utils.hpp>

using namespace std::chrono;

int main(int argc, char** argv) {
  auto options = load_options(argc, argv);
  const std::string service_name{"SkeletonsDetector.Detection"};

  auto channel = StreamChannel(options.broker_uri());
  is::info("Connected to broker {}", options.broker_uri());
  auto subscription = is::Subscription(channel.internal_channel(), service_name);
  subscription.subscribe("CameraGateway.*.Frame");

  SkeletonsDetector detector(options);
  int dropped;
  while (true) {
    auto msg = channel.consume_last(&dropped);
    auto pb_image = msg.unpack<is::vision::Image>();
    if (!pb_image) continue;

    auto t0 = steady_clock::now();

    auto camera_id = get_topic_id(msg.topic());
    auto skeletons = detector.detect(pb_image.get(), camera_id);

    auto t1 = steady_clock::now();

    is::Message skeletons_msg{skeletons};
    channel.publish(fmt::format("SkeletonsDetector.{}.Detection", camera_id), skeletons_msg);
    auto cv_image = detector.last_image();
    Image pb_rendered_image;
    render_skeletons(cv_image, skeletons, &pb_rendered_image);
    is::Message rendered_msg{pb_rendered_image};
    channel.publish(fmt::format("SkeletonsDetector.{}.Rendered", camera_id), rendered_msg);

    auto t2 = steady_clock::now();

    const auto dt = [](auto& tf, auto& t0) { return duration_cast<microseconds>(tf - t0).count() / 1000.0; };
    is::info("source = {}, detections = {}, dropped_messages = {}", msg.topic(), skeletons.objects_size(), dropped);
    is::info("took_ms = {{ detection = {:.2f}, service = {:.2f} }}", dt(t1, t0), dt(t2, t0));
  }
}