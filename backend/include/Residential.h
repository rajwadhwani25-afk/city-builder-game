#pragma once
#include "Building.h"

class Residential : public Building {
    int residents;

public:
    Residential(int x, int y);
    void display() override;
    int getResidents()       { return residents; }
    void addResidents(int n) { residents += n; }
};