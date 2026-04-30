#include "../include/Industrial.h"

Industrial::Industrial(int x, int y)
    : Building("Industrial", x, y, 1200, 120, 200), pollution(30), production(400) {}

void Industrial::display() {
    cout << "Industrial at (" << x << "," << y
         << ") | Pollution: " << pollution
         << " | Production: " << production << endl;
}