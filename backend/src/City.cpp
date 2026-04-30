#include "../include/City.h"
#include "../include/Residential.h"
#include "../include/Commercial.h"
#include "../include/Industrial.h"
#include "../include/Recreation.h"
#include "../include/OutdoorRecreation.h"
#include "../include/IndoorRecreation.h"
#include "../include/Transport.h"
#include "../include/Airport.h"
#include "../include/RailwayStation.h"
#include "../include/Utility.h"
#include "../include/Road.h"
#include <iostream>
#include <algorithm>
using namespace std;

City::City(string name, int size)
    : cityName(name), budget(50000), population(0),
      happiness(50), turn(1), gridSize(size) {
    grid.resize(size);
    for(int i = 0; i < size; i++)
        grid[i].resize(size, nullptr);
}

City::~City() {
    for(int i = 0; i < gridSize; i++)
        for(int j = 0; j < gridSize; j++)
            if(grid[i][j]) {
                delete grid[i][j];
                grid[i][j] = nullptr;
            }
}

bool City::isInBounds(int x, int y) {
    return x >= 0 && x < gridSize && y >= 0 && y < gridSize;
}

CityObject* City::getObject(int x, int y) {
    if(!isInBounds(x, y)) return nullptr;
    return grid[x][y];
}

bool City::placeObject(CityObject* obj, int x, int y) {
    if(!isInBounds(x, y)) {
        cout << "Out of bounds!" << endl;
        return false;
    }
    if(grid[x][y] != nullptr) {
        cout << "Cell already occupied!" << endl;
        return false;
    }
    if(budget < obj->getCost()) {
        cout << "Not enough budget!" << endl;
        return false;
    }
    budget -= obj->getCost();
    grid[x][y] = obj;
    return true;
}

bool City::removeObject(int x, int y) {
    if(!isInBounds(x, y) || grid[x][y] == nullptr) return false;
    delete grid[x][y];
    grid[x][y] = nullptr;
    return true;
}

bool City::hasAdjacentRoad(int x, int y) {
    int dx[] = {0, 0, 1, -1};
    int dy[] = {1, -1, 0, 0};
    for(int i = 0; i < 4; i++) {
        int nx = x + dx[i];
        int ny = y + dy[i];
        if(isInBounds(nx, ny))
            if(grid[nx][ny] && grid[nx][ny]->getName() == "Road")
                return true;
    }
    return false;
}

void City::nextTurn() {
    int revenue        = 0;
    int happinessChange = 0;

    for(int i = 0; i < gridSize; i++) {
        for(int j = 0; j < gridSize; j++) {
            if(!grid[i][j]) continue;

            // deduct maintenance for every placed object
            budget -= grid[i][j]->getMaintenance();

            // commercial earns revenue
            Commercial* c = dynamic_cast<Commercial*>(grid[i][j]);
            if(c) revenue += c->getRevenue();

            // recreation boosts happiness
            Recreation* r = dynamic_cast<Recreation*>(grid[i][j]);
            if(r) happinessChange += r->getHappinessBoost();

            // industrial earns but pollutes
            Industrial* ind = dynamic_cast<Industrial*>(grid[i][j]);
            if(ind) {
                revenue         += ind->getProduction();
                happinessChange -= ind->getPollution();
            }

            // transport boosts population growth
            Transport* t = dynamic_cast<Transport*>(grid[i][j]);
            if(t) population += t->getConnectivityBoost() / 20;
        }
    }

    budget     += revenue;
    happiness  += happinessChange;
    happiness   = max(0, min(100, happiness));   // clamp 0-100
    population += max(0, happiness / 10);        // happiness drives growth
    turn++;

    cout << "\n--- Turn " << turn - 1 << " complete ---" << endl;
    cout << "Revenue:   " << revenue        << endl;
    cout << "Happiness: " << happiness      << endl;
    cout << "Budget:    " << budget         << endl;
    cout << "Pop:       " << population     << endl;
}

vector<vector<string>> City::getGridState() {
    vector<vector<string>> state(gridSize, vector<string>(gridSize, "empty"));
    for(int i = 0; i < gridSize; i++)
        for(int j = 0; j < gridSize; j++)
            if(grid[i][j]) state[i][j] = grid[i][j]->getName();
    return state;
}

void City::displayStats() {
    cout << "\n=========================" << endl;
    cout << "City:      " << cityName   << endl;
    cout << "Budget:    " << budget     << endl;
    cout << "Pop:       " << population << endl;
    cout << "Happiness: " << happiness  << "/100" << endl;
    cout << "Turn:      " << turn       << endl;
    cout << "Grid:      " << gridSize   << "x" << gridSize << endl;
    cout << "=========================" << endl;
}

void City::displayGrid() {
    if(gridSize > 20) {
        cout << "Grid too large for console display." << endl;
        return;
    }
    for(int i = 0; i < gridSize; i++) {
        for(int j = 0; j < gridSize; j++) {
            if(!grid[i][j])                                         cout << ". ";
            else if(grid[i][j]->getName() == "Road")                cout << "# ";
            else if(grid[i][j]->getName() == "Residential")         cout << "R ";
            else if(grid[i][j]->getName() == "Commercial")          cout << "C ";
            else if(grid[i][j]->getName() == "Industrial")          cout << "I ";
            else if(grid[i][j]->getName() == "OutdoorRecreation")   cout << "G ";
            else if(grid[i][j]->getName() == "IndoorRecreation")    cout << "T ";
            else if(grid[i][j]->getName() == "Utility")             cout << "U ";
            else if(grid[i][j]->getName() == "Airport")             cout << "A ";
            else if(grid[i][j]->getName() == "RailwayStation")      cout << "S ";
            else                                                     cout << "? ";
        }
        cout << endl;
    }
}