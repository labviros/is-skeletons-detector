#include <chrono>
#include "skeletons/utils.hpp"
#include "skeletons/detector.hpp"
#include <is/wire/core.hpp>
#include <is/wire/rpc.hpp>
#include <is/wire/rpc/log-interceptor.hpp>
#include <is/msgs/utils.hpp>

using namespace std::chrono;

int main(int argc, char** argv) {
  auto options = load_options(argc, argv);
  const std::string service_name{"SkeletonsDetector"};

  auto channel = is::Channel(options.broker_uri());
  is::info("Connected to broker {}", options.broker_uri());
  auto provider = is::ServiceProvider(channel);
  provider.add_interceptor(is::LogInterceptor());
  auto tracer = make_tracer(options, "SkeletonsDetector");
  channel.set_tracer(tracer);

  SkeletonsDetector detector(options);

  provider.delegate<Image, ObjectAnnotations>(
      service_name + ".Detect", [&](is::Context*, Image const& pb_image, ObjectAnnotations* skeletons) {
        try {
          *skeletons = detector.detect(pb_image);
        } catch (std::runtime_error& e) {
          return is::make_status(is::wire::StatusCode::INTERNAL_ERROR, e.what());
        } catch (...) { return is::make_status(is::wire::StatusCode::INTERNAL_ERROR); }
        return is::make_status(is::wire::StatusCode::OK);
      });

  provider.run();
}