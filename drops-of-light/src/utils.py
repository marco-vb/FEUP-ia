from itertools import chain, combinations

# Represent the graph as an adjacency list
adjacency_list = [
    [1, 3, 5, 7, 9, 11],
    [0, 2, 12, 13],
    [1, 3, 13, 14],
    [0, 2, 4, 14],
    [3, 5, 14, 15],
    [0, 4, 6, 15],
    [5, 7, 15, 16],
    [0, 6, 8, 16],
    [7, 9, 16, 17],
    [0, 8, 10, 17],
    [9, 11, 17, 18],
    [0, 10, 12, 18],
    [1, 11, 13, 18],
    [1, 2, 12],
    [2, 3, 4],
    [4, 5, 6],
    [6, 7, 8],
    [8, 9, 10],
    [10, 11, 12],
]


# Get all the subsets of a set
def all_substets(ss):
    return chain(*map(lambda x: combinations(ss, x), range(0, len(ss) + 1)))


# Map the colors to their names
color_map = {
    "": "Empty",
    "1": "Red",
    "2": "Green",
    "3": "Blue",
    "12": "Yellow",
    "13": "Magenta",
    "23": "Cyan",
    "123": "White",
}


# Get the color name of a vertex
def get_color(colors):
    color_string = ""

    colors = sorted(map(lambda color: abs(color), colors))

    for color in colors:
        color_string += str(color)

    return color_map[color_string]


# Convert the color to an RGB tuple
rgb = {
    "Empty": (64, 64, 64),
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255),
    "Yellow": (255, 255, 0),
    "Magenta": (255, 0, 255),
    "Cyan": (0, 255, 255),
    "White": (255, 255, 255),
}

