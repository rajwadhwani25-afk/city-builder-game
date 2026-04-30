#pragma once
#include <string>
#include <iostream>
using namespace std;

class CityObject {
protected:
    string name;
    int x, y;
    int cost;
    int maintenanceCost;

public:
    CityObject(string name, int x, int y, int cost, int maintenance);
    virtual void display();
    int getCost()            { return cost; }
    int getX()               { return x; }
    int getY()               { return y; }
    string getName()         { return name; }
    int getMaintenance()     { return maintenanceCost; }
    virtual ~CityObject()    {}
};