#include "../include/Building.h"

Building::Building(string name, int x, int y, int cost, int maintenance, int capacity)
    : CityObject(name, x, y, cost, maintenance), capacity(capacity) {}