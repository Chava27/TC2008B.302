import gps

map = None
with open('./model/town_blocks.txt', 'r') as file:
    map = file.read()[:-1].split("\n")

m = [["" for i in range(26)] for i in range(26)]

print(len(map))
for y in range(26):
            for x in range(26):
                m[x][26-1-y] = map[y][x]



gipies =gps.GPS(m)

# Basic tests used to debug the GPS
print("Route: ",gipies.shortest_path((17,16), (16, 15)))
print("Route: ",gipies.shortest_path((17,16), (16, 16)))
print("Route: ",gipies.shortest_path((17,16), (16, 17)))
print("Route: ",gipies.shortest_path((17,16), (17, 17)))
print("Route: ",gipies.shortest_path((5,17), (4, 16)))
print("Route: ",gipies.shortest_path((16,11), (17, 10)))