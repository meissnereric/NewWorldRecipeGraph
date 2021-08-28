#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import json
import networkx as nx
from datetime import datetime
import sys
import csv

def get_digits(text):
    return list(filter(str.isdigit, text))

def clean_node_rarities(F, rarity_values):
    
    for n,d in F.nodes(data=True):
        digits = get_digits(n)
        if len(digits) == 1:
            r = digits[0]
        else:
            r = 0
        F.node[n]['Rarity'] = r
    
    for s,t,d in F.edges(data=True):
        r = d['Rarity']
        q = d['Quantity']
        if q == 0:
            F.edges[s,t]['Quantity'] = 1
            q = 1
        v = rarity_values[r] * q
        F.node[t]['Rarity'] = r

def remove_cycles(F):
    for cycle in nx.algorithms.cycles.simple_cycles(F):
        source = [int(s) for s in cycle[0] if s.isdigit()]
        if len(cycle) > 1:
            sink = [int(s) for s in cycle[1] if s.isdigit()]
            F.remove_edge(cycle[0], cycle[1])
        else:
            F.remove_edge(cycle[0], cycle[0])

    for cycle in nx.algorithms.cycles.simple_cycles(F):
        print("Cycle left:", cycle)  
        
        
def initialize_start_items(F, start_items, values, rarity_values):
    for ingId in start_items:
        data = F.node[ingId]
        rarity = data['Rarity']
        value = rarity_values[int(rarity)]
        values[ingId] = value
        F.node[ingId]['Value'] = value
        
def reset(edge_values, node_values, rarity_values, F):
    clean_node_rarities(F, rarity_values)
    remove_cycles(F)
    initialize_start_items(F, start_items, node_values, rarity_values)


def add_edge_value(s, t, ev, edge_values, F):
    global edge_updates
    edge_updates = edge_updates + 1
    F.edges[s,t]['Value'] = ev
    edge_values[(s,t)] = ev
    
def add_node_value(node, value, node_values, F):
    global node_updates
    node_updates = node_updates + 1
    F.node[node]['Value'] = value
    node_values[node] = value

def compute_node_value_smol(node, node_values, edge_values, F):
    if node in node_values:
        print("Using existing node value for {}: {}".format(node, node_values[node]))
        return node_values[node]
    else:
        edge_list = []
        preds = list(F.predecessors(node))
        if len(preds) == 0:
            print("Using len(preds) == 0 logic for value.")
            node_value = rarity_values[F.node[node]['Rarity']]
            edge_list = [node_value]
        else:
            for p in preds:
                ev = compute_edge_value_smol(p, node, node_values, edge_values, F)
                edge_list.append(ev)
                node_value = sum(edge_list)
        print("New node value for {} is {}".format(node, node_value, edge_list))
        add_node_value(node, node_value, node_values, F)
        return node_value
        
    
def compute_edge_value_smol(s, t, node_values, edge_values, F):
    """
    Recipe ingredients are sources for the target recipe output.
    F: The graph
    s: source node 
    t: target node
    """
    if (s,t) in edge_values:
        print("Using existing edge value for {}: {}".format((s,t), edge_values[(s,t)]))
        return edge_values[(s,t)]
    s_value = compute_node_value_smol(s, node_values, edge_values, F)
    ev = s_value * F.edges[s,t]['Quantity']
    print("New edge value for {} is {}".format((s,t), ev))
    add_edge_value(s, t, ev, edge_values, F)
    return ev



def GenerateGephiDataFromNetX(F, fileString):
    """
        ing?: ingredient list in the form of [xid, name, rarity, typ, itemType, icon, quantity]
    """
    with open(fileString, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Source", "Target", "Quantity", "Tradeskill", "Rarity", "Station", "ItemType", "Category", "Value"]) #These column headers are used in Gephi automatically
        for s,t,d in F.edges(data=True):
            tradeskill = d['Tradeskill']
            rarity = d['Rarity']
            station = d['Station']
            quantity = d['Quantity']
            item_type = d['ItemType']
            category = d['Category']
            value = d['Value']
            writer.writerow([s, t, quantity, tradeskill, rarity, station, item_type, category, value]) #nodeA is ingredient, nodeB is recipe output, and count is the quantity


#Generates a new csv file for the node list labels on Gephi
def GenerateGephiLabelsFromNetX(F, fileString):
    print("Generating Labels...")
    sys.stdout.flush()
    with open(fileString, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Label", "Rarity", "Value"]) #These columns are used in Gephi automatically
        for node, data in F.nodes(data=True):
            name = data['name'] if 'name' in data else node
            writer.writerow([node, name, data['Rarity'], data['Value']]) #This data is streamer1, streamer1, and # of unique viewers for streamer1
    
now = datetime.now()
            
input_edge_file = 'data/08.27.2021.17.23.32EDGELIST.csv'
input_label_file = 'data/08.27.2021.17.23.32LABELS.csv'
output_edge_file = "data/%s" % (now.strftime("%m.%d.%Y.%H.%M.%SVALUE_EDGELIST.csv"))
output_label_file = "data/%s" % (now.strftime("%m.%d.%Y.%H.%M.%SVALUE_LABELS.csv"))


edgeData = open(input_edge_file, "r")
next(edgeData, None)  # skip the first line in the input file

labelData = open(input_label_file, "r")
next(labelData, None)  # skip the first line in the input file
edgeGraph = nx.DiGraph()
labelGraph = nx.DiGraph()

G = nx.parse_edgelist(edgeData, delimiter=',', create_using=edgeGraph,
                      nodetype=str, data=(('Quantity', int),
                                          ('Tradeskill', str),
                                          ('Rarity', int),
                                          ('Station', str),
                                          ('ItemType', str),
                                          ('Category', str),))


NG = nx.DiGraph()
nodes = pd.read_csv(label_file)
format_nodes = [(item[0], {'name': item[1], 'Rarity': item[2]})for item in nodes.values.tolist()]
NG.add_nodes_from(format_nodes)

F = nx.compose(NG,G)
print("G nodes {} NG nodes {} F nodes {}".format(len(list(G)),len(list(NG)),len(list(F)),))
end_items = sorted([ingId for ingId, degree in F.out_degree() if degree == 0 ])
start_items = sorted([ingId for ingId, degree in F.in_degree() if degree == 0 ])

edge_updates = 0
node_updates = 0

# Make sure all nodes have a rarity since we use it for baseline value.
# 
# Remove cycles to make things easier. They're just going up and down refined materials anyways.
# 
# Initialize all items with no predecessors with a value dependant on their rarity
edge_values = {}
node_values = {}
base = 3
rng = 6
rarity_values = [base ** i for i in range(0,rng)]
print(rarity_values)
reset(edge_values, node_values, rarity_values, F)
# print(edge_values, node_values.values())
for node_id in F.nodes():
    print(node_id)
    compute_node_value_smol(node_id, node_values, edge_values, F) 

print("Edge Updates: {} \n Node Updates: {}".format(edge_updates, node_updates))

nodes = []
no_value_nodes = []
for node in F.nodes(data=True):
    if 'Value' in node[1]:
        nodes.append((node[1]['Value'], node[0]))
    else:
        no_value_nodes.append((node[0]))
nodes = sorted(nodes)  
no_value_nodes = sorted(no_value_nodes)
print("Nodes: ", len(nodes), nodes)
print("\n\n\n\n no_value_nodes: ", len(no_value_nodes))

                
GenerateGephiDataFromNetX(F, output_edge_file)
GenerateGephiLabelsFromNetX(F, output_label_file)
