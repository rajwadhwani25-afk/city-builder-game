#include "../include/Road.h"

Road::Road(int x, int y, string type)
    : CityObject("Road", x, y, 100, 10), roadType(type) {}

void Road::display() {
    cout << "Road [" << roadType << "] at (" << x << "," << y << ")" << endl;
}