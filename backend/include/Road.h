#pragma once
#include "CityObject.h"

class Road : public CityObject {
    string roadType;

public:
    Road(int x, int y, string type = "twoway");
    void display() override;
    string getRoadType()     { return roadType; }
};