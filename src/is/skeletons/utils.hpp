#pragma once

#include <string>
#include "is/msgs/utils.hpp"
#include "is/wire/core.hpp"
#include "options.pb.h"

is::SkeletonsDetectorOptions load_options(int argc, char** argv);

class StreamChannel {
 public:
  StreamChannel(std::string const& uri) : channel(uri) {}
  is::Channel& internal_channel() { return this->channel; }
  is::Message consume_last(int* dropped = nullptr);

 private:
  is::Channel channel;
};