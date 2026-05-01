#include <pybind11/pybind11.h>
#include <pybind11/stl.h>        // needed for vector<vector<string>>
#include "../include/City.h"
#include "../include/Residential.h"
#include "../include/Commercial.h"
#include "../include/Industrial.h"
#include "../include/OutdoorRecreation.h"
#include "../include/IndoorRecreation.h"
#include "../include/Road.h"
#include "../include/Utility.h"
#include "../include/Airport.h"
#include "../include/RailwayStation.h"

namespace py = pybind11;

PYBIND11_MODULE(city_engine, m) {
    m.doc() = "City builder game backend";

    py::class_<City>(m, "City")
        .def(py::init<string, int>())       // City("PimpriCity", 100)
        .def("placeResidential",  [](City& c, int x, int y) {
            return c.placeObject(new Residential(x, y), x, y);
        })
        .def("placeCommercial",   [](City& c, int x, int y, string type) {
            return c.placeObject(new Commercial(x, y, type), x, y);
        })
        .def("placeIndustrial",   [](City& c, int x, int y) {
            return c.placeObject(new Industrial(x, y), x, y);
        })
        .def("placeRoad",         [](City& c, int x, int y) {
            return c.placeObject(new Road(x, y), x, y);
        })
        .def("placeOutdoorRec",   [](City& c, int x, int y, string type) {
            return c.placeObject(new OutdoorRecreation(x, y, type), x, y);
        })
        .def("placeIndoorRec",    [](City& c, int x, int y, string type) {
            return c.placeObject(new IndoorRecreation(x, y, type), x, y);
        })
        .def("placeUtility",      [](City& c, int x, int y, string type) {
            return c.placeObject(new Utility(x, y, type), x, y);
        })
        .def("placeAirport",      [](City& c, int x, int y) {
            return c.placeObject(new Airport(x, y), x, y);
        })
        .def("placeRailway",      [](City& c, int x, int y) {
            return c.placeObject(new RailwayStation(x, y), x, y);
        })
        .def("removeObject",      &City::removeObject)
        .def("hasAdjacentRoad",   &City::hasAdjacentRoad)
        .def("nextTurn",          &City::nextTurn)
        .def("getGridState",      &City::getGridState)
        .def("getBudget",         &City::getBudget)
        .def("getPopulation",     &City::getPopulation)
        .def("getHappiness",      &City::getHappiness)
        .def("getTurn",           &City::getTurn)
        .def("getGridSize",       &City::getGridSize)
        .def("getCityName",       &City::getCityName);
}