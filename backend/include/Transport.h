#pragma once
#include "CityObject.h"

class Transport : public CityObject {
protected:
    int connectivityBoost;

public:
    Transport(string name, int x, int y, int cost, int maintenance, int connectivity);
    int getConnectivityBoost() { return connectivityBoost; }
    void display() override;
};