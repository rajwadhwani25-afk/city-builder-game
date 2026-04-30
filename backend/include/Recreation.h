#pragma once
#include "CityObject.h"

class Recreation : public CityObject {
protected:
    int happinessBoost;

public:
    Recreation(string name, int x, int y, int cost, int maintenance, int happiness);
    int getHappinessBoost()  { return happinessBoost; }
    void display() override;
};