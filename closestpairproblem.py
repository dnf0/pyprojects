'''
Given an input array finds the closest pair.  Achieves matching using scipy's cKDTree, very quick even for 
millions of points.  Speed ups may be achieved using pyflann: 
https://github.com/mariusmuja/flann/tree/master/src/python/pyflann  

Here only 2-dimensional for plotting purposes. Extensible to more by changing the dims
parameter.  Large numbers of dimensions will experience a decline in performance, see
http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.cKDTree.html 
'''
import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.spatial as spatial 

def show_it(r_pts, closest):
    if closest == None:
        plt.plot(r_pts[:,1],r_pts[:,0],'b.')
        plt.show()
    else:
        plt.plot(r_pts[:,1],r_pts[:,0],'b.')
        #recolour closest points
        plt.plot([r_pts[closest[0],1],r_pts[closest[1],1]],
                 [r_pts[closest[0],0],r_pts[closest[1],0]],
                 'ro')
        plt.show()
    plt.close()
          
def get_closest_pair(r_pts):
    #make kdtree and self compare
    tree = spatial.cKDTree(r_pts)
    distances, indexes = tree.query(r_pts, 2)
    
    #extract the closest non-self matched pair    
    ref_min_index = np.argmin(distances[:,1])
    print 'distance:', distances[ref_min_index,1], 'units'
    comp_min_index = indexes[ref_min_index,1]
    
    return [ref_min_index, comp_min_index]

def main():
    
    #get grid size
    print 'please enter number of random points: '
    n_points = int(raw_input())
    dims = 2
    
    #make random x and y values
    random_points = np.random.rand(n_points,dims) 
    
    #show the points
    if dims == 2:
        print 'plotting figure... please close to proceed'
        show_it(random_points, None)
    
    #find the closest point pair
    closest_pair_index = get_closest_pair(random_points)
    
    #replot
    if dims ==2:
        show_it(random_points, closest_pair_index)
    
if __name__ == '__main__':
    sys.exit(main())