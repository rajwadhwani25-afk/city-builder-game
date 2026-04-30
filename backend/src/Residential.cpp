#include "../include/Residential.h"

Residential::Residential(int x, int y)
    : Building("Residential", x, y, 500, 50, 100), residents(0) {}

void Residential::display() {
    cout << "Residential at (" << x << "," << y
         << ") | Residents: " << residents << endl;
}