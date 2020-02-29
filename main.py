import xml.etree.ElementTree as ET
import re
import os
import numpy as np
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter



dirName = 'D:/PhD at Vanderbilt/pythonWorkplace/data-processing/'

def getFiles(dirName):
    if not dirName.endswith('/'):
        dirName += '/'

    files = os.listdir(dirName)
    svgFiles = [(dirName + file) for file in files if file.endswith('.svg')]

    for svgFile in svgFiles:
        print(svgFile)
        txtFileName = extractData(svgFile)
        plotHeatmap(txtFileName, cell_sides=[2, 2], min_density=0.000001, max_density=0.0012)
        
def extractData(svgFileName):
    txtFileName = svgFileName.replace('.svg', '.txt')

    output = ' '

    tree = ET.parse(svgFileName)
    root = tree.getroot()

    tmp = root.findall(".//circle")

    viewbox = root.attrib['viewBox'].split(' ')[2: 4]
    output = output.join(viewbox) + '\n\n'

    circles = root.findall('.//{http://www.w3.org/2000/svg}circle')
    paths = root.findall('.//{http://www.w3.org/2000/svg}path')

    if 0 != len(circles):
        for circle in circles:
            try:
                stroke = circle.attrib.get('stroke')
                if stroke is not None:
                    output += ' '.join([circle.attrib.get(key) for key in ['cx', 'cy']]) + '\n'
            except Exception:
                print(circle.attrib)

    if 0 != len(paths):
        for path in paths:
            try:
                match = re.search('^M([0-9\.]+),([0-9\.]+)', path.attrib.get('d'))
                if match:
                    output += ' '.join(match.groups()) + '\n'
            except Exception:
                print(path.attrib)

    txtFile = open(txtFileName, 'w')
    txtFile.write(output)
    txtFile.close()

    return txtFileName

def plotHeatmap(txtFileName, cell_sides, min_density, max_density):
    # sns.set()
    fig, axs = plt.subplots(ncols = 1, nrows = 1)

    data = np.loadtxt(txtFileName)
    range_xy = [[0, data[0, 1]], [0, data[0, 0]]]
    n_xy = (data[0] / cell_sides).astype(np.int)
    points = data[1:]

    H, x_edges, y_edges = np.histogram2d(x = points[:, 1], y = points[:, 0],
                                         bins = n_xy,
                                         range = range_xy,
                                         normed = True)
    # H_tmp = H.copy()
    # H_tmp[np.where(H_tmp == 0)] = np.nan
    # print(txtFileName + " sec min is " + str(np.nanmin(H_tmp)) + " max is " + str(np.nanmax(H_tmp)))

    H = H + min_density
   # ax0 = sns.heatmap(np.log(H), xticklabels = False, yticklabels = False, vmin = np.log(min_density), vmax = np.log(max_density),
    #            cbar = True, cmap = plt.get_cmap("hot"), ax = axs[0])
    H = gaussian_filter(H, sigma = 1)
    ax1 = sns.heatmap(np.log(H), xticklabels = False, yticklabels = False, vmin = np.log(min_density), vmax = np.log(max_density),
                cbar = True, cmap = plt.get_cmap("hot"), ax = axs)
    # ax1= sns.heatmap(H, xticklabels=False, yticklabels=False, vmin=0, vmax=0.0006,
    #             cbar=True, cmap=plt.get_cmap("jet"))

    plt.savefig(txtFileName.replace(".txt", ".eps"))

    # plt.show()

    return H.max()





getFiles(dirName)
# plotHeatmap("18-19LHBDA.txt", cell_sides=[2, 2], min_density=0.000001, max_density=0.0012)
# max_dentsity = plotHeatmap('18-19LHCTB.txt', cell_sides = [2, 2], min_density = 0.000001, max_density = 0.0006)
# print(max_dentsity)
