cmake_minimum_required(VERSION 3.10.0)

# # ######
# # #### Build service binary
# # ######

find_package(is-msgs REQUIRED)
find_package(is-wire REQUIRED)
find_package(opencv REQUIRED)

list(APPEND libraries 
  skeletons::utils
  skeletons::detector
  is-wire::is-wire
  is-msgs::is-msgs
  opencv::opencv
)

add_executable(stream.bin stream.cpp)
target_link_libraries(stream.bin PRIVATE ${libraries})
set_property(TARGET stream.bin PROPERTY CXX_STANDARD 14)

add_executable(rpc.bin rpc.cpp)
target_link_libraries(rpc.bin PRIVATE ${libraries})
set_property(TARGET rpc.bin PROPERTY CXX_STANDARD 14)