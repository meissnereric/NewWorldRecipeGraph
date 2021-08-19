# New World Recipe Graph

1. Step 1 - Run the web crawler over the recipes you need to collect a big json file.
2. Step 2 - Run the "Processing Recipes into Table - Best" notebook. It generates "recipe\_table.csv", among other files, which you'll use in the next step.
3. Step 3 - Process Tables into Gephi Files notebook - This generates and EDGELIST and LABEL file with the dates.
4. Step 4 - Networkx Computing Values notebook - Modify this file to use the EDGELIST and LABEL files, then run to get the final edgelist and label files.
 1. If you want to modify the values for computing the overall value of a compound item, do that here either directly in the values table when you initialize it, or using the 'rarity\_values' list.
5. Step 5 - Load the edge and label files into Gephi or your favorite network graphing software.


## Web Crawler

## Notebooks for processing the scraped data

## 
