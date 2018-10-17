#include <chrono>
#include "skeletons/utils.hpp"
#include "skeletons/detector.hpp"
#include <is/wire/core.hpp>
#include <is/msgs/utils.hpp>

using namespace std::chrono;

int main(int argc, char** argv) {
  auto options = load_options(argc, argv);
  const std::string service_name{"SkeletonsDetector"};

  auto channel = StreamChannel(options.broker_uri());
  is::info("Connected to broker {}", options.broker_uri());
  auto subscription = is::Subscription(channel.internal_channel(), service_name + ".Detection");
  subscription.subscribe("CameraGateway.*.Frame");
  auto tracer = make_tracer(options, "SkeletonsDetector");

  SkeletonsDetector detector(options);
  int dropped;
  while (true) {
    const auto start_span = [&](auto& maybe_ctx, auto span_name) {
      return maybe_ctx ? tracer->StartSpan(span_name, {ChildOf(maybe_ctx->get())}) : tracer->StartSpan(span_name);
    };

    auto msg = channel.consume_last(&dropped);

    auto maybe_ctx = msg.extract_tracing(tracer);
    auto service_span = start_span(maybe_ctx, "detection_and_render");

    auto unpack_span = start_span(maybe_ctx, "unpack");
    auto pb_image = msg.unpack<is::vision::Image>();
    if (!pb_image) continue;
    unpack_span->Finish();

    auto t0 = steady_clock::now();
    auto detection_span = start_span(maybe_ctx, "detection");
    auto camera_id = get_topic_id(msg.topic());
    auto skeletons = detector.detect(pb_image.get(), camera_id);
    detection_span->Finish();

    auto t1 = steady_clock::now();
    auto pack_sk_span = start_span(maybe_ctx, "pack_and_publish_detections");
    is::Message skeletons_msg{skeletons};
    skeletons_msg.inject_tracing(tracer, service_span->context());
    channel.publish(fmt::format("SkeletonsDetector.{}.Detection", camera_id), skeletons_msg);
    pack_sk_span->Finish();

    auto render_span = start_span(maybe_ctx, "render_pack_publish");
    auto cv_image = detector.last_image();
    Image pb_rendered_image;
    render_skeletons(cv_image, skeletons, &pb_rendered_image);
    is::Message rendered_msg{pb_rendered_image};
    channel.publish(fmt::format("SkeletonsDetector.{}.Rendered", camera_id), rendered_msg);
    render_span->Finish();

    service_span->SetTag("detections", skeletons.objects_size());
    service_span->Finish();
    auto t2 = steady_clock::now();

    const auto dt = [](auto& tf, auto& t0) { return duration_cast<microseconds>(tf - t0).count() / 1000.0; };
    is::info("source = {}, detections = {}, dropped_messages = {}", msg.topic(), skeletons.objects_size(), dropped);
    is::info("took_ms = {{ detection = {:.2f}, service = {:.2f} }}", dt(t1, t0), dt(t2, t0));
  }
}