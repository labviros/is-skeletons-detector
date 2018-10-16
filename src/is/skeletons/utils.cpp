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
