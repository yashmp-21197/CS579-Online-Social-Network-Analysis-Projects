Python file 1 : make_graph_nodes_edges_instagram.py
<br/>
Required libraries to install are selenium and webdriver_manager.
<br/>
Change insta_username and insta_password value with your credentials at the beginning of the main function.
<br/>
This script creates nodes and edges of the graph and write these objects in json format in all_insta_accounts.json and graph_edges.json files
<br/>

python file 2 : make_data_file_gephi.py
<br/>
This script reads edges from graph_edges.json file and write these edges in (source, target) format into csv file edge_list.csv
<br/>
This edge_list.csv is used to create graph in gephi tool.
<br/>

Gephi tool project file 3 : OSNA_P1.gephi
<br/>
Download gephi tool.
<br/>
Open this project file in gephi tool.
<br/>