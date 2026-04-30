#include "../include/Airport.h"

Airport::Airport(int x, int y)
    : Transport("Airport", x, y, 5000, 500, 100) {}

void Airport::display() {
    cout << "Airport at (" << x << "," << y
         << ") | Connectivity: +" << connectivityBoost << endl;
}