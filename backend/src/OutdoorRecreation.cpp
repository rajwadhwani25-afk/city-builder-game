#include "../include/OutdoorRecreation.h"

OutdoorRecreation::OutdoorRecreation(int x, int y, string type)
    : Recreation("OutdoorRecreation", x, y, 600, 60, 20), placeType(type) {
    if(type == "amusement_park") { happinessBoost = 50; cost = 2000; }
    if(type == "stadium")        { happinessBoost = 40; cost = 1500; }
}

void OutdoorRecreation::display() {
    cout << "Outdoor [" << placeType << "] at (" << x << "," << y
         << ") | Happiness: +" << happinessBoost << endl;
}