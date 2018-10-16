#include <chrono>
#include "skeletons/utils.hpp"
#include "skeletons/detector.hpp"
#include <is/wire/core.hpp>
#include <is/msgs/utils.hpp>

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
    auto t0 = std::chrono::steady_clock::now();
    auto skeletons = detector.detect(pb_image.get());
    auto tf = std::chrono::steady_clock::now();
    auto dt_ms = std::chrono::duration_cast<std::chrono::microseconds>(tf - t0).count() / 1000.0;
    is::info("took_ms = {{ detection={:.2f} }}", dt_ms);
  }
}