#pragma once
#include "Transport.h"

class Airport : public Transport {
public:
    Airport(int x, int y);
    void display() override;
};