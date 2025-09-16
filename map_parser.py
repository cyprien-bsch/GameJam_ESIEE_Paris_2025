

def map_parser(file_name):
    map = list()

    with open(file_name, "r") as f:
        X = int(f.readline())
        Y = int(f.readline())

        for y in range(Y):
            line = list()
            fline = f.readline()
            for x in range(X):
                line.append(fline[x])
            map.append(line)
    
    return map


def map_encoder(map, X, Y, file_name):
    
    with open(file_name, "w") as f:
        f.write(str(X) + "\n")
        f.write(str(Y) + "\n")

        for y in range(Y):
            line = ""
            for x in range(X):
                line = line + map[y][x]
            f.write(line + "\n")


