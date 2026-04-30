#pragma once
#include "Recreation.h"

class OutdoorRecreation : public Recreation {
    string placeType;

public:
    OutdoorRecreation(int x, int y, string type = "garden");
    void display() override;
    string getPlaceType()    { return placeType; }
};