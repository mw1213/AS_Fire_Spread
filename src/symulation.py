import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors
import matplotlib.patches as mpatches


# based on model from article
# https://scipython.com/blog/the-forest-fire-model/

# Displacements from a cell to its eight nearest neighbours
neighbourhood = ((-1,-1), (-1,0), (-1,1), (0,-1), (0, 1), (1,-1), (1,0), (1,1))


# Wind influence based on its direction: from top left clockwise
wind_max, wind_most, wind_ok, wind_bad, wind_no = 2, 1.25, 0.75, 0.25, 0
wind_infulence =[
    [wind_max, wind_most, wind_ok, wind_most, wind_bad, wind_ok, wind_bad, wind_no],
    [wind_most, wind_max, wind_most, wind_ok, wind_ok, wind_bad, wind_no, wind_bad],
    [wind_ok, wind_most, wind_max, wind_bad, wind_most, wind_no, wind_bad, wind_ok],
    [wind_bad, wind_ok, wind_most, wind_no, wind_max, wind_bad, wind_ok, wind_most],
    [wind_no, wind_bad, wind_ok, wind_bad, wind_most, wind_ok, wind_most, wind_max],
    [wind_bad, wind_no, wind_bad, wind_ok, wind_ok, wind_most, wind_max, wind_most],
    [wind_ok, wind_bad, wind_no, wind_most, wind_bad, wind_max, wind_most, wind_ok],
    [wind_most, wind_ok, wind_bad, wind_max, wind_no, wind_most, wind_ok, wind_bad],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

# Wind direction setting
se, e, ne, n, nw, w, sw, s, no_wind_source = 0,1,2,3,4,5,6,7,8
# cell types
EMPTY, DEAD_TREE, OLD_TREE, TREE, SAPLING, STONE, WATER, SPARKS, FIRE, COALS, BURNED_GROUND = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
TREE_TYPES = DEAD_TREE, OLD_TREE, TREE, SAPLING

# maping cell types to colors
colors_list = ['white','sienna', 'darkolivegreen', 'darkgreen', 'lime', 'gray', 'blue', 'coral', 'firebrick', 'orange', 'black']
cmap = colors.ListedColormap(colors_list)
bounds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

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

    # FIRE is twice more likely to spread than COALS and  4x more likely than from SPARKS
    fire_probs = [likelyhood_of_fire_multiplier, 0.5 * likelyhood_of_fire_multiplier, 0.25 * likelyhood_of_fire_multiplier]
    # if near WATER reduce fire_probs by water_reduction_rate
    if near_water:
        fire_probs =  [x * water_reduction_rate for x in fire_probs]

    
    if tree_type in TREE_TYPES:
        for i in range(len(neighbourhood)):
            # The diagonally-adjacent trees are further away, so
            # only catch fire with a reduced probability:
            # if abs(dx) == abs(dy) and np.random.random() < 0.573:
            #     continue

            # with wind inflence
            dx, dy = neighbourhood[i][0], neighbourhood[i][1]
            wind_power = wind_infulence[wind_direction][i]
            local_probability_of_spread = np.random.random()
            chance_of_fire = wind_power * local_probability_of_spread
            treshold = 0.5

            if X[iy+dy,ix+dx] == FIRE and chance_of_fire * fire_probs[0] > treshold:
                X1[iy,ix] = SPARKS
                break
            elif X[iy+dy,ix+dx] == SPARKS and chance_of_fire * fire_probs[1] > treshold:
                X1[iy,ix] = SPARKS
                break
            elif X[iy+dy,ix+dx] == COALS and chance_of_fire * fire_probs[2] > treshold:
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
    X1 = np.copy(X)
    X1[0,:] = BURNED_GROUND
    X1[nx-1,:] = BURNED_GROUND
    X1[:,ny-1] = BURNED_GROUND
    X1[:,0] = BURNED_GROUND
    for ix in range(1,nx-1):
        for iy in range(1,ny-1):
            if X[iy,ix] == EMPTY and np.random.random() <= p:
                X1[iy,ix] = SAPLING
            if X[iy,ix] == DEAD_TREE:
                if np.random.random() <= p:
                    X1[iy,ix] = SAPLING
                else:
                    X1[iy,ix] = DEAD_TREE
            # if the cell was a sapling convert it to the tree
            if X[iy,ix] == SAPLING:
                if np.random.random() <= P_sapling_to_tree:
                    X1[iy,ix] = TREE
                else:
                    X1[iy,ix] = SAPLING
            if X[iy,ix] == TREE:
                if np.random.random() <= p_tree_to_old_tree:
                    X1[iy,ix] = OLD_TREE
                else:
                    X1[iy,ix] = TREE
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
                X1[iy,ix] = BURNED_GROUND
            if X[iy,ix] == BURNED_GROUND:
                X1[iy,ix] = BURNED_GROUND
            if X[iy,ix] in TREE_TYPES:
                is_near_water = near_water(X1, ix, iy)
                calculate_fire_at_position(X, X1, ix, iy, X1[iy,ix], is_near_water)
    return X1

# Probability of new tree growth per empty cell, and of lightning strike.
p, f = 0.0005, 0.00001
p_tree_death = 0.01
p_tree_to_old_tree = 0.25
P_sapling_to_tree = 0.35
# water influence in scale 0-1: 1 means no reduction
water_reduction_rate =  1
wind_direction = e
# Forest size (number of cells in x and y directions).
nx, ny = 100, 100

# interval = time between frames (ms).
def animate_with_pltshow(interval=100, wr_rate = 1, wind_dir = e, frames=200):
    # Initialize the forest grid.
    X = np.random.choice([0,1,2,3,4,5,6,7,8], (ny, nx), p=[0.3, 0.05, 0.05, 0.47, 0.108, 0.01, 0.01, 0.001, 0.001])


    fig = plt.figure(figsize=(25/3, 6.25))
    ax = plt.axes([0.05, 0.05, 0.5, 0.9])
    ax.set_axis_off()
    im = ax.imshow(X, cmap=cmap, norm=norm)#, interpolation='nearest')

    plt.rcParams['figure.facecolor'] = '#272727'
    plt.rcParams['savefig.facecolor'] = '#272727'


    # The animation function: called to produce a frame for each generation.
    def animate(i):
        im.set_data(animate.X)
        animate.X = iterate(animate.X)
        plt.legend(handles=[mpatches.Patch(color='white', label='EMPTY'), mpatches.Patch(color='sienna', label='DEAD_TREE'), \
            mpatches.Patch(color='darkolivegreen', label='OLD_TREE'), mpatches.Patch(color='darkgreen', label='TREE'), \
            mpatches.Patch(color='lime', label='SAPLING'), mpatches.Patch(color='gray', label='STONE'), \
            mpatches.Patch(color='blue', label='WATER'), mpatches.Patch(color='coral', label='SPARKS'), \
            mpatches.Patch(color='firebrick', label='FIRE'), mpatches.Patch(color='orange', label='COALS'), \
            mpatches.Patch(color='black', label='BURNED \nGROUND')], bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    # Bind our grid to the identifier X in the animate function's namespace.
    animate.X = X

    global water_reduction_rate
    water_reduction_rate = wr_rate
    global wind_direction
    wind_direction = wind_dir
    return animation.FuncAnimation(fig, animate, interval=interval, frames=frames)

# #lower fps fater animation when interval == 100
# def animate_to_gif(interval=100, no_fps=60, wr_rate = 1, wind_dir = e):
#     global water_reduction_rate
#     water_reduction_rate = wr_rate
#     global wind_direction
#     wind_direction = wind_dir
#     anim = animation.FuncAnimation(fig, animate, interval=interval, frames=200)
#     anim.save(f'animations/animation_water_influence_{water_reduction_rate}_wind_direction_{wind_direction}_with_legend_fps_{no_fps}.gif', fps = no_fps)

# animate_with_pltshow(10, wind_dir = s)
#animate_to_gif(wind_dir=nw)