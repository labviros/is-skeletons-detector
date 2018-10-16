cmake_minimum_required(VERSION 3.10.0)

# # ######
# # #### Build service binary
# # ######

find_package(is-msgs REQUIRED)
find_package(is-wire REQUIRED)
find_package(zipkin-cpp-opentracing REQUIRED)
find_package(opencv REQUIRED)
add_executable(service.bin service.cpp)

target_link_libraries(
  service.bin
 PRIVATE
  skeletons::utils
  skeletons::detector
  is-wire::is-wire
  is-msgs::is-msgs
  zipkin-cpp-opentracing::zipkin-cpp-opentracing
  opencv::opencv
)

set_property(TARGET service.bin PROPERTY CXX_STANDARD 14)