#include "../include/IndoorRecreation.h"

IndoorRecreation::IndoorRecreation(int x, int y, string type)
    : Recreation("IndoorRecreation", x, y, 900, 90, 25), venueType(type), capacity(300) {
    if(type == "auditorium") { capacity = 1000; cost = 1800; happinessBoost = 35; }
    if(type == "cinema")     { capacity = 500;  cost = 1200; happinessBoost = 30; }
}

void IndoorRecreation::display() {
    cout << "Indoor [" << venueType << "] at (" << x << "," << y
         << ") | Capacity: " << capacity
         << " | Happiness: +" << happinessBoost << endl;
}