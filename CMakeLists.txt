cmake_minimum_required(VERSION 3.6)
project(cg_cpp_bundler)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES tests/out/bundled_code.cpp)
add_executable(cg_cpp_bundler_test ${SOURCE_FILES})