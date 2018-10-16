cmake_minimum_required(VERSION 3.10.0)

find_package(openpose REQUIRED)
find_package(is-msgs REQUIRED)
find_package(is-wire REQUIRED)

######
### detector library
######

add_library(detector detector.cpp detector.hpp)

target_link_libraries(
  detector
 PUBLIC
  options::options
  is-msgs::is-msgs
  openpose::openpose
 PRIVATE
  is-wire::is-wire
)

target_include_directories(
  detector
 PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/..> # for headers when building
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}> # for generated files in build mode
  $<INSTALL_INTERFACE:include/${include_dir}> # for clients in install mode
)

set_property(TARGET detector PROPERTY CXX_STANDARD 11)
add_library(skeletons::detector ALIAS detector)

######
### utils library
######

add_library(utils utils.cpp utils.hpp)

target_link_libraries(
  utils
 PUBLIC
  options::options
  is-msgs::is-msgs
 PRIVATE
  is-wire::is-wire
)

target_include_directories(
  utils
 PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/..> # for headers when building
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}> # for generated files in build mode
  $<INSTALL_INTERFACE:include/${include_dir}> # for clients in install mode
)

set_property(TARGET utils PROPERTY CXX_STANDARD 11)
add_library(skeletons::utils ALIAS utils)



