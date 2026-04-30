#pragma once
#include "Recreation.h"

class IndoorRecreation : public Recreation {
    string venueType;
    int capacity;

public:
    IndoorRecreation(int x, int y, string type = "theatre");
    void display() override;
    string getVenueType()    { return venueType; }
    int getCapacity()        { return capacity; }
};