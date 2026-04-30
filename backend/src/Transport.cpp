#include "../include/Transport.h"

Transport::Transport(string name, int x, int y, int cost, int maintenance, int connectivity)
    : CityObject(name, x, y, cost, maintenance), connectivityBoost(connectivity) {}

void Transport::display() {
    cout << name << " at (" << x << "," << y
         << ") | Connectivity: +" << connectivityBoost << endl;
}