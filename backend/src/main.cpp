#include "../include/City.h"
#include "../include/Residential.h"
#include "../include/Commercial.h"
#include "../include/Industrial.h"
#include "../include/OutdoorRecreation.h"
#include "../include/IndoorRecreation.h"
#include "../include/Transport.h"
#include "../include/Airport.h"
#include "../include/RailwayStation.h"
#include "../include/Road.h"
#include "../include/Utility.h"

int main() {
    City myCity("PimpriCity", 100);

    // lay a long main road
    for(int col = 0; col < 30; col++)
        myCity.placeObject(new Road(10, col), 10, col);

    // vertical connecting road
    for(int row = 5; row < 20; row++)
        myCity.placeObject(new Road(row, 15), row, 15);

    // residential neighbourhood
    for(int col = 0; col < 6; col++)
        myCity.placeObject(new Residential(11, col), 11, col);

    // commercial strip
    for(int col = 6; col < 10; col++)
        myCity.placeObject(new Commercial(11, col, "shop"), 11, col);
    myCity.placeObject(new Commercial(11, 10, "mall"), 11, 10);

    // industrial zone (away from residential)
    myCity.placeObject(new Industrial(11, 20), 11, 20);
    myCity.placeObject(new Industrial(11, 21), 11, 21);

    // recreation
    myCity.placeObject(new OutdoorRecreation(9, 5, "garden"),        9, 5);
    myCity.placeObject(new OutdoorRecreation(9, 6, "amusement_park"),9, 6);
    myCity.placeObject(new IndoorRecreation(9, 7, "cinema"),         9, 7);
    myCity.placeObject(new IndoorRecreation(9, 8, "theatre"),        9, 8);

    // utilities
    myCity.placeObject(new Utility(9, 12, "hospital"),    9, 12);
    myCity.placeObject(new Utility(9, 13, "police"),      9, 13);
    myCity.placeObject(new Utility(9, 14, "firestation"), 9, 14);

    // transport — far from residential
    myCity.placeObject(new Airport(5, 25),         5, 25);
    myCity.placeObject(new RailwayStation(11, 16), 11, 16);

    myCity.displayStats();
    myCity.nextTurn();
    myCity.nextTurn();
    myCity.nextTurn();
    myCity.displayStats();

    return 0;
}