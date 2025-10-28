import json
import csv

with open('app/shade/final_shades.json', 'r') as f:
    data = json.load(f)

with open('app/shade/shade_clusters.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Color Name', 'Cluster Count'])
    
    for color_name, clusters in data.items():
        writer.writerow([color_name, len(clusters)])

print("CSV file created successfully!")
