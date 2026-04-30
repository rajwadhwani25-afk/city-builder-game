#include "../include/Commercial.h"

Commercial::Commercial(int x, int y, string type)
    : Building("Commercial", x, y, 800, 80, 50), revenue(200), shopType(type) {
    if(type == "mall")   { revenue = 500; cost = 1500; }
    if(type == "office") { revenue = 350; cost = 1000; }
}

void Commercial::display() {
    cout << "Commercial [" << shopType << "] at (" << x << "," << y
         << ") | Revenue/turn: " << revenue << endl;
}