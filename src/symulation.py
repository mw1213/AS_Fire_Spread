import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors

# Create a forest fire animation based on a simple cellular automaton model.
# The maths behind this code is described in the scipython blog article
# at https://scipython.com/blog/the-forest-fire-model/
# Christian Hill, January 2016.
# Updated January 2020.

# Displacements from a cell to its eight nearest neighbours
neighbourhood = ((-1,-1), (-1,0), (-1,1), (0,-1), (0, 1), (1,-1), (1,0), (1,1))
EMPTY, DEAD_TREE, OLD_TREE, TREE, SAPLING, STONE, WATER, SPARKS, FIRE, COALS = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
# Colours for visualization: brown for EMPTY, dark green for TREE and orange
# for FIRE. Note that for the colormap to work, this list and the bounds list
# must be one larger than the number of different values in the array.
TREE_TYPES = DEAD_TREE, OLD_TREE, TREE, SAPLING
colors_list = ['black','sienna', 'darkolivegreen', 'darkgreen', 'lime', 'gray', 'blue', 'coral', 'firebrick', 'orange']
cmap = colors.ListedColormap(colors_list)
bounds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# scale 0-1: 1 means no reduction
water_reduction_rate = 1# 0.0000001

norm = colors.BoundaryNorm(bounds, cmap.N)

def near_water(X1, ix, iy):
    for dx,dy in neighbourhood:
        if X1[iy+dy,ix+dx] == WATER:
            return True
    return False

def calculate_fire_at_position(X, X1, ix, iy, tree_type, near_water):
    likelyhood_of_fire_multiplier = 0
    match tree_type:
        case 1:
            likelyhood_of_fire_multiplier = 2
        case 2:
            likelyhood_of_fire_multiplier = 1.5
        case 3:
            likelyhood_of_fire_multiplier = 1
        case 4:
            likelyhood_of_fire_multiplier = 0.5

    # FIRE is twice more likely to spread than COALS and SPARKS
    fire_probs = [0.5 * likelyhood_of_fire_multiplier, 0.35 * likelyhood_of_fire_multiplier, 0.25 * likelyhood_of_fire_multiplier]
    # if near WATER reduce fire_probs by water_reduction_rate
    if near_water:
        fire_probs =  [x * water_reduction_rate for x in fire_probs]

    
    if tree_type in TREE_TYPES:
        for dx,dy in neighbourhood:
            # The diagonally-adjacent trees are further away, so
            # only catch fire with a reduced probability:
            if abs(dx) == abs(dy) and np.random.random() < 0.573:
                continue
            if X[iy+dy,ix+dx] == FIRE and np.random.random() < fire_probs[0]:
                X1[iy,ix] = SPARKS
                break
            elif X[iy+dy,ix+dx] == SPARKS and np.random.random() < fire_probs[1]:
                X1[iy,ix] = SPARKS
                break
            elif X[iy+dy,ix+dx] == COALS and np.random.random() < fire_probs[2]:
                X1[iy,ix] = SPARKS
                break
            else:
                #lightning strike sets to fire instatnt
                if np.random.random() <= f:
                    X1[iy,ix] = FIRE


def iterate(X):
    """Iterate the forest according to the forest-fire rules."""

    # The boundary of the forest is always empty, so only consider cells
    # indexed from 1 to nx-2, 1 to ny-2
    X1 = np.zeros((ny, nx))
    for ix in range(1,nx-1):
        for iy in range(1,ny-1):
            if X[iy,ix] == EMPTY and np.random.random() <= p:
                X1[iy,ix] = SAPLING
            if X[iy,ix] == DEAD_TREE and np.random.random() <= p:
                X1[iy,ix] = SAPLING
            # if the cell was a sapling convert it to the tree
            if X[iy,ix] == SAPLING:
                X1[iy,ix] = TREE
            if X[iy,ix] == TREE:
                X1[iy,ix] = OLD_TREE
            if X[iy,ix] == OLD_TREE:
                X1[iy,ix] = OLD_TREE
            if X[iy,ix] == OLD_TREE and np.random.random() <= p_tree_death:
                X1[iy,ix] = DEAD_TREE
            if X[iy,ix] == STONE:
                X1[iy,ix] = STONE
            if X[iy,ix] == WATER:
                X1[iy,ix] = WATER
            if X[iy,ix] == SPARKS:
                X1[iy,ix] = FIRE
            if X[iy,ix] == FIRE:
                X1[iy,ix] = COALS
            if X[iy,ix] == COALS:
                X1[iy,ix] = EMPTY
            if X[iy,ix] in TREE_TYPES:
                is_near_water = near_water(X1, ix, iy)
                calculate_fire_at_position(X, X1, ix, iy, X1[iy,ix], is_near_water)
    return X1

# Probability of new tree growth per empty cell, and of lightning strike.
p, f = 0.05, 0.0001
p_tree_death = 0.01
# Forest size (number of cells in x and y directions).
nx, ny = 100, 100
# Initialize the forest grid.
X = np.random.choice([0,1,2,3,4,5,6,7,8], (ny, nx), p=[0.5, 0.05, 0.05, 0.19, 0.1, 0.05, 0.05, 0.005, 0.005])


fig = plt.figure(figsize=(25/3, 6.25))
ax = fig.add_subplot(111)
ax.set_axis_off()
im = ax.imshow(X, cmap=cmap, norm=norm)#, interpolation='nearest')



# The animation function: called to produce a frame for each generation.
def animate(i):
    im.set_data(animate.X)
    animate.X = iterate(animate.X)
# Bind our grid to the identifier X in the animate function's namespace.
animate.X = X

# Interval between frames (ms).
interval = 100
anim = animation.FuncAnimation(fig, animate, interval=interval, frames=200)
plt.show()