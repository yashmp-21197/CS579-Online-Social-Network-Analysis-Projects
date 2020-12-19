import csv
import json

if __name__ == '__main__':

    graph_edges_filename = 'graph_edges.json'
    graph_edges = None

    try:
        with open(graph_edges_filename) as input_file:
            graph_edges = json.load(input_file)
    except:
        graph_edges = {}

    rows = []

    for user in graph_edges:
        following_users = graph_edges[user]

        for following_user in following_users:
            rows.append([user, following_user])

    fields = ['Source', 'Target']

    csv_filename = "edge_list.csv"

    with open(csv_filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)
