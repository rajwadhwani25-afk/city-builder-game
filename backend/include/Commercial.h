#pragma once
#include "Building.h"

class Commercial : public Building {
    int revenue;
    string shopType;

public:
    Commercial(int x, int y, string type = "shop");
    void display() override;
    int getRevenue()         { return revenue; }
    string getShopType()     { return shopType; }
};