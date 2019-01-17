import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist

class cluster_density(object):

	def __init__(self, points, eval_points=None):
		self.eval_points=points
		self.points = eval_points
		return

	def _construct_components(self,distance_matrix, is_FE_min):
		# Build subgraphs with connected components of the isolated FE minima
		print('Constructing connected components.')
		n_points = distance_matrix.shape[0]
		sort_inds = np.argsort(distance_matrix,axis=1)
	
		all_inds = np.arange(n_points)
		graph = np.zeros((n_points,n_points))
	
		for i in range(n_points):
			if is_FE_min[i]:
				check_points = []
				neighbors = sort_inds[i,:]
				k_neighbors=1
			
				# Add neighbors until another potential component is reached
				for j in range(k_neighbors,n_points):
					current_neighbor = neighbors[j]
					if is_FE_min[current_neighbor]:
					
						neighbor_distance = distance_matrix[i,current_neighbor]
					
						if len(check_points) > 2:
							check_point_distances = distance_matrix[current_neighbor,np.asarray(check_points)]
							is_smaller_dist = check_point_distances < neighbor_distance
							if np.sum(is_smaller_dist) > 0:
								# A non-component point is closer to both the current point and 
								# the other component point => the two component points are not neighbors
								break;
					
						# Add connection between neighbors
						graph[i,current_neighbor] = 1	
						# Enforce symmetry
						graph[current_neighbor,i] = 1			
					else:
						check_points.append(current_neighbor);
	
		# Sparsify graph to contain only the connected components
		graph = graph[is_FE_min,:]
		graph = graph[:,is_FE_min]
	
		return graph;

	def _find_connected_components(self,graph):
		# Assign points to connected components
		print('Clustering data points.')
		
		n_points = graph.shape[0]
		component_indices = np.zeros(n_points)
		is_visited = np.zeros(n_points)	
		all_inds = np.arange(n_points)
	
		iComponent = 1
		while np.sum(is_visited) < is_visited.shape[0]:
			iComponent += 1
			queue = []
			# get next unvisited point
			unvisited_points = all_inds[is_visited==0]
			queue.append(unvisited_points[0])
		
			while len(queue) > 0:
				current_point = queue.pop(0)
				if is_visited[current_point] == 0:
					is_visited[current_point] = 1
					component_indices[current_point] = iComponent
	
					# get unvisited neighbors 
					neighbors = all_inds[graph[current_point,:] > 0]
					for iNeighbor in neighbors:
						if is_visited[iNeighbor] == 0:
							queue.append(iNeighbor)
	
		return component_indices
	
	def _data_cluster_indices(self, point_distances, cluster_indices_eval_points):
		"""
		Set cluster indices according to the closest data point.
		"""
		n_points = point_distances.shape[0]
		cluster_inds = np.zeros(n_points)
		
		min_inds = np.argmin(point_distances,axis=1)
		
		# Set cluster index of point to the same as the cluster index of evaluated (grid) point
		cluster_inds = cluster_indices_eval_points[min_inds]
		return cluster_inds
	
	def cluster_data(self, is_FE_min):
		
		# Construct and detect connected components
		graph = self._construct_components(cdist(self.eval_points,self.eval_points), is_FE_min)
		print('# Graph connections: '+str(np.sum(graph)))
		cluster_indices_eval_points = self._find_connected_components(graph)
		
		all_cl_inds = np.zeros(self.eval_points.shape[0])
		all_cl_inds[is_FE_min] = cluster_indices_eval_points
		if self.points is not None:
			cluster_indices = self._data_cluster_indices(cdist(data,self.points),all_cl_inds)
		else:
			cluster_indices = all_cl_inds
		
		return cluster_indices