# Automating GIS processes final assignment
# Author: Henna Kalliokoski

import click
import fire as fire
import pandas as pd
import geopandas as gpd

from glob import glob
from pysal import Natural_Breaks

from bokeh.plotting import figure, save
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper

import pysal as ps
from bokeh.palettes import RdYlBu11 as palette
from bokeh.models import LogColorMapper

files = glob('data/HelsinkiRegion_TravelTimeMatrix2015/*/*')
metrop_access = gpd.read_file('MetropAccess_YKR_grid/MetropAccess_YKR_grid_EurefFIN.shp')

def files_by_YKR_ID(id_list):
    '''
    finds files from data folder. The folder must exist in the same folder as this script.
    :param id_list: list of YKR_ID values
    :return: list of results as filepaths
    '''
    i = 0
    results = []
    for file in files:
        i += 1
        print('processing', file, i, '/', len(files))
        if id_in_file(id_list, file):
            results = results + [file   ]
    print('results:', results)
    warn = [n for n in id_list if str(n) not in [a[-11:-4] for a in results]]
    if warn:
        print('wollowing IDs not found:', warn)
    return results


def id_in_file(id_list, file):
    '''
    tells if the file is one of the files we are looking for
    :param id_list: list of wanted YKR_ID's
    :param file: the file we are processing
    :return: True if the file is in the list, else False
    '''
    id_list = [str(id) for id in id_list]
    if file[-11:-4] in id_list:
        print('id', file[-11:-4], 'found in', file)
        return True
    return False


# print(metrop_access.head())
# files_by_YKR_ID(['6018253', '6015142', 'foobarbaz'])


def to_geodataframe(matrix_file):
    '''
    converts a csv file to geodataframe
    :param matrix_file: filepath of the csv file
    :return: geodataframe object
    '''
    data = pd.read_csv(matrix_file, sep=';', na_values=-1)
    gdf = metrop_access.merge(data, left_on='YKR_ID', right_on='from_id', how='inner')
    return gdf


def save_shapefile(gdf, outputfolder=''):
    '''
    saves a geodataframe to shapefile
    :param gdf: geodataframe object
    :param outputfolder: user defined output folder
    :return: None
    '''
    gdf.to_file(outputfolder + 'accessibility_to_' + str(int(gdf.to_id[0])))


def ykr_id_to_shapefile(YKR_ID, output_folder=''):
    save_shapefile(to_geodataframe(files_by_YKR_ID([YKR_ID])[0]), output_folder)
    if output_folder:
        print('shapefile saved to', output_folder)
    else:
        print('shapefile saved to current folder')

# save_shapefile(to_geodataframe('data/HelsinkiRegion_TravelTimeMatrix2014/5989xxx/travel_times_to_ 6013577.txt'), 'data/')
# ykr_id_to_shapefile('5989964')

def static_map(YKR_ID, travel_mode, output_folder=''):
    '''
    Creates static map based on YKR_ID and travel mode.
    :param YKR_ID: grid id
    :param travel_mode: walk, public or car
    :param output_folder: user defined output folder
    :return: None
    '''
    mode = {'car': 'car_r_t', 'public': 'pt_m_tt', 'walk': 'walk_t'}
    data = pd.read_csv(files_by_YKR_ID([YKR_ID])[0], sep=';', na_values=-1)
    data = data.dropna()
    data = metrop_access.merge(data, left_on='YKR_ID', right_on='from_id', how='inner')

    classified = data[[mode[travel_mode]]].apply(Natural_Breaks.make(k=6))
    classified.columns = [travel_mode + '_classified']
    data = data.join(classified)

    plot = data.plot(column=travel_mode + '_classified', linewidth=0)
    plot.get_figure().savefig(output_folder + str(YKR_ID) + '_' + travel_mode + '.png', dpi=300)

# static_map('5989964', 'public')
# static_map('5989964', 'public', 'data/')


def interactive_map(YKR_ID, travel_mode, output_folder=''):
    '''
    Creates interactive map based on YKR_ID and travel mode.
    :param YKR_ID: grid id
    :param travel_mode: walk, public or car
    :param output_folder: user defined folder
    :return: None
    '''
    data = to_geodataframe(files_by_YKR_ID([YKR_ID])[0])

    grid = metrop_access
    mode = {'car': 'car_r_t', 'public': 'pt_m_tt', 'walk': 'walk_t'}
    travel_m = mode[travel_mode]

    def get_poly_coords(row, geom, coord_type):
        """Returns the coordinates ('x' or 'y') of edges of a Polygon exterior"""

        # Parse the exterior of the coordinate
        exterior = row[geom].exterior

        if coord_type == 'x':
            # Get the x coordinates of the exterior
            return list(exterior.coords.xy[0])
        elif coord_type == 'y':
            # Get the y coordinates of the exterior
            return list(exterior.coords.xy[1])

    grid['x'] = grid.apply(get_poly_coords, geom='geometry', coord_type='x', axis=1)
    grid['y'] = grid.apply(get_poly_coords, geom='geometry', coord_type='y', axis=1)

    # Replace No Data values (-1) with large number (999)
    grid = grid.replace(-1, 999)

    # Classify our travel times into 5 minute classes until 200 minutes
    # Create a list of values where minumum value is 5, maximum value is 200 and step is 5.
    breaks = [x for x in range(5, 200, 5)]

    # Initialize the classifier and apply it
    classifier = ps.User_Defined.make(bins=breaks)
    pt_classif = data[[travel_m]].apply(classifier)

    # Rename the classified column
    pt_classif.columns = [travel_m + '_ud']

    # Join it back to the grid layer
    grid = grid.join(pt_classif)

    # Make a copy, drop the geometry column and create ColumnDataSource
    g_df = grid.drop('geometry', axis=1).copy()
    gsource = ColumnDataSource(g_df)
    # Initialize our figure
    p = figure(title="Travel times to " + YKR_ID + " by " + travel_mode)

    # Create the color mapper
    color_mapper = LogColorMapper(palette=palette)
    # Plot grid
    p.patches('x', 'y', source=gsource,
              fill_color={'field': travel_m + '_ud', 'transform': color_mapper},
              fill_alpha=1.0, line_color="black", line_width=0.05)

    # Save the figure
    outfp = output_folder + YKR_ID + '_interactive.html'
    save(p, outfp)
    return ''

# interactive_map('5989964', 'public', output_folder='data/')


def create_map(YKR_ID, travel_mode, outputfolder='', style=None):
    '''
    Creates static or interactive map based on YKR_ID and travel mode.
    :param YKR_ID: grid id
    :param travel_mode: walk, public or car
    :param outputfolder: user defined folder
    :param style: interactive or static
    :return: None
    '''
    if style == 'interactive':
        interactive_map(YKR_ID, travel_mode, outputfolder)
    else:
        static_map(YKR_ID, travel_mode, outputfolder)

# create_map('6013577', 'public')

def compare_modes(YKR_ID, comp, modes, outputfolder=''):
    '''
    Compares two travel modes and saves the calculation into shapefile.
    :param YKR_ID: grid id
    :param modes: walk, public, car
    :param comp: time or distance
    :param outputfolder: user defined folder
    :return: geodataframe object
    '''
    mode = {'time': {'car': 'car_r_t', 'public': 'pt_m_t', 'walk': 'walk_t'},
            'distance': {'car': 'car_r_d', 'public': 'pt_m_d', 'walk': 'walk_d'}}
    t_m1 = mode[comp][modes[0]]
    t_m2 = mode[comp][modes[1]]
    data = to_geodataframe(files_by_YKR_ID([YKR_ID])[0])
    data['compare'] = [m1 - m2 for m1, m2 in zip(data[t_m1], data[t_m2])]
    save_shapefile(data, outputfolder + modes[0] + '_compared_to_' + modes[1] + '_')
    return data

# print(compare_modes('5989964', comp='distance', modes=['walk', 'public']))


def main():
    fire.Fire({
        'find': files_by_YKR_ID,
        'shape': ykr_id_to_shapefile,
        'create_map': create_map,
        'compare': compare_modes
    })


if __name__ == '__main__':
    main()
