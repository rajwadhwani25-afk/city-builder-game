#pragma once
#include "Transport.h"

class RailwayStation : public Transport {
public:
    RailwayStation(int x, int y);
    void display() override;
};  