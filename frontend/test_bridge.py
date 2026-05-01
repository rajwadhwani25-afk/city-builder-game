import os
os.add_dll_directory("C:/msys64/mingw64/bin")

import city_engine

city = city_engine.City("PimpriCity", 100)
city.placeRoad(10, 5)
city.placeRoad(10, 6)
city.placeResidential(11, 5)
city.placeCommercial(11, 6, "shop")

print("City name:  ", city.getCityName())
print("Budget:     ", city.getBudget())
print("Population: ", city.getPopulation())
print("Happiness:  ", city.getHappiness())

city.nextTurn()
print("\nAfter 1 turn:")
print("Budget:     ", city.getBudget())
print("Happiness:  ", city.getHappiness())