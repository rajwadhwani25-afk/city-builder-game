#include "../include/Recreation.h"

Recreation::Recreation(string name, int x, int y, int cost, int maintenance, int happiness)
    : CityObject(name, x, y, cost, maintenance), happinessBoost(happiness) {}

void Recreation::display() {
    cout << name << " at (" << x << "," << y
         << ") | Happiness boost: +" << happinessBoost << endl;
}