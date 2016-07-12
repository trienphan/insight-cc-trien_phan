"""
Title:	Calculating the Median Degree of a Venmo Transaction Graph
Name:	Trien Phan
Email: 	<tphan@caltech.edu>
Date:	2016-07-11
"""
# Import third-party libraries
import pandas as pd
import numpy as np
import networkx as nx

# Load JSON objects into a pandas DataFrame for efficient manipulation.
# However, we must first preprocess the .txt file.

# First, read the .txt line-by-line into a list.
with open(r'venmo_input/venmo-trans.txt', 'r') as i:
	venmo_data = i.readlines()

# Second, remove trailing '\n' from each line using "rstrip" function.
for ii in range(0, len(venmo_data)):
	venmo_data[ii] = venmo_data[ii].rstrip()

# Third, separate each JSON object with a comma and add square brackets 
# to the beginning and end in order for pandas to parse correctly.
venmo_data_str = '[' + ','.join(venmo_data) + ']'

# Finally, load it into a DataFrame.
venmo_df = pd.read_json(venmo_data_str, convert_dates=True)
num_rows = venmo_df.shape[0]	# number of payments

# Ready the output file for writing.
write_output = open(r'venmo_output/output.txt', 'w')

# Beginning of Data Analysis
for ii in range(0, num_rows):
	# Set up temporary DataFrame for each iteration
	ven_loop = venmo_df.iloc[0:ii+1,:]
	
	# Set up actor-target tuples for future edge creation
	ven_loop['at_pair'] = tuple(zip(ven_loop.actor, ven_loop.target))
	
	# Next, detect payments that are >= 60 seconds older than the
	# most recent payment. First, calcuate time differences in seconds.
	time_diff = ven_loop.created_time.max() - venmo_df.created_time
	time_diff_sec = time_diff / np.timedelta64(1, 's')
	
	# Then, find the index of the rows where the time difference
	# is >= 60 seconds.
	td_sec_TOO_OLD = time_diff_sec.loc[time_diff_sec[:] >= 60.0]
	td_drop_index = td_sec_TOO_OLD.index
	
	# Drop the rows in ven_loop according to td_drop_index.
	ven_loop.drop(td_drop_index, axis=0)
	
	# Now, the ven_loop DataFrame only contains recent payments. 
	# Next, determine the numbers of nodes by finding all of the
	# unique names in the DataFrame. Both 'actor' and 'target'
	# columns are included.
	at_combined = ven_loop[['actor','target']]
	unique_names = pd.unique(at_combined.values.ravel())
	
	# Create an empty graph via NetworkX in which nodes and edges
	# can be constructed.
	G = nx.Graph()
	
	# Add the nodes to G.
	G.add_nodes_from(unique_names)
	
	# Then, add the edges using the 'at_pair' column in ven_loop.
	G.add_edges_from(ven_loop.at_pair)
	
	# Calculate the degree of each node using the built-in function.
	deg_values = nx.degree(G).values()
	
	# However, this outputs a dictionary. Let's convert this into
	# a numpy array for easy median calcuation.
	deg = np.array(list( (deg_values) ))
	
	# Finally, we can calculate the median!
	median_out = np.median(deg, overwrite_input=True)
	
	# Truncate the median to two decimal places.
	median_out = np.trunc(median_out * 100) / 100
	
	# Print the median for this iteration to the output file.
	med_str = '{:0.2f}'.format(median_out) + '\n'
	write_output.write(med_str)

	G.clear()

write_output.close()
