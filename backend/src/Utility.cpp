#include "../include/Utility.h"

Utility::Utility(int x, int y, string type)
    : CityObject("Utility", x, y, 1000, 100), utilityType(type), serviceRadius(3) {
    if(type == "hospital")    { cost = 2000; serviceRadius = 4; }
    if(type == "police")      { cost = 1000; serviceRadius = 3; }
    if(type == "firestation") { cost = 1200; serviceRadius = 3; }
}

void Utility::display() {
    cout << "Utility [" << utilityType << "] at (" << x << "," << y
         << ") | Radius: " << serviceRadius << endl;
}