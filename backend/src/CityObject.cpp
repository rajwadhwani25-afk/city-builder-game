#include "../include/CityObject.h"

CityObject::CityObject(string name, int x, int y, int cost, int maintenance)
    : name(name), x(x), y(y), cost(cost), maintenanceCost(maintenance) {}

void CityObject::display() {
    cout << name << " at (" << x << "," << y << ")" << endl;
}