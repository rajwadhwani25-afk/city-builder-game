#include "../include/RailwayStation.h"

RailwayStation::RailwayStation(int x, int y)
    : Transport("RailwayStation", x, y, 3000, 300, 60) {}

void RailwayStation::display() {
    cout << "Railway Station at (" << x << "," << y
         << ") | Connectivity: +" << connectivityBoost << endl;
}