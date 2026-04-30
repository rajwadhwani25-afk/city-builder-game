#pragma once
#include "CityObject.h"

class Utility : public CityObject {
    string utilityType;
    int serviceRadius;

public:
    Utility(int x, int y, string type = "hospital");
    void display() override;
    string getUtilityType()  { return utilityType; }
    int getServiceRadius()   { return serviceRadius; }
};