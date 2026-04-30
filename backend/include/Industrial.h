#pragma once
#include "Building.h"

class Industrial : public Building {
    int pollution;
    int production;

public:
    Industrial(int x, int y);
    void display() override;
    int getPollution()       { return pollution; }
    int getProduction()      { return production; }
};