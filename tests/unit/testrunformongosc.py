from pymongo import MongoClient

# Connect to the MongoDB server
client = MongoClient('mongodb://localhost:27017')

# Access the database
db = client['PlantConnectome']
genes = db["all_dic"]
# Access a collection
geneAlias_collection = db['gene_alias']
my_search = ['5.8S RRNA[GENE]']
gas=geneAlias_collection.find({"$or":[{"gene": {"$in": my_search}},{"aliases" :{"$in": my_search}}]})
#for result in gas:
#    print(result)
gasList=[]
for ga in gas:
    print(ga)
    gasList.append(ga['gene'])
    for item in ga['aliases']:
        gasList.append(item)
print("alias-list",gasList)
results = genes.find(
            {"$or": [{"entity1": {"$in": my_search}}, {"entity2": {"$in": my_search}}]})

