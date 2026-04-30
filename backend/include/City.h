#pragma once
#include "CityObject.h"
#include <vector>
#include <string>
using namespace std;

class City {
    string cityName;
    int budget;
    int population;
    int happiness;
    int turn;
    int gridSize;
    vector<vector<CityObject*>> grid;

public:
    City(string name, int size = 100);
    ~City();

    bool placeObject(CityObject* obj, int x, int y);
    bool removeObject(int x, int y);
    bool hasAdjacentRoad(int x, int y);
    bool isInBounds(int x, int y);
    CityObject* getObject(int x, int y);

    void nextTurn();
    void displayGrid();
    void displayStats();

    vector<vector<string>> getGridState();

    int getBudget()          { return budget; }
    int getPopulation()      { return population; }
    int getHappiness()       { return happiness; }
    int getTurn()            { return turn; }
    int getGridSize()        { return gridSize; }
    string getCityName()     { return cityName; }
};