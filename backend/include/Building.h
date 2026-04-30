#pragma once
#include "CityObject.h"

class Building : public CityObject {
protected:
    int capacity;

public:
    Building(string name, int x, int y, int cost, int maintenance, int capacity);
    int getCapacity() { return capacity; }
};