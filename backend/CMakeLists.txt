cmake_minimum_required(VERSION 3.12)
project(city_engine)

set(CMAKE_CXX_STANDARD 17)

find_package(pybind11 REQUIRED)

pybind11_add_module(city_engine
    src/bindings.cpp
    src/CityObject.cpp
    src/Building.cpp
    src/Residential.cpp
    src/Commercial.cpp
    src/Industrial.cpp
    src/Recreation.cpp
    src/OutdoorRecreation.cpp
    src/IndoorRecreation.cpp
    src/Transport.cpp
    src/Airport.cpp
    src/RailwayStation.cpp
    src/Road.cpp
    src/Utility.cpp
    src/City.cpp
)

target_include_directories(city_engine PRIVATE include)