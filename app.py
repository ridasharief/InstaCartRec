from flask import Flask, render_template, request, jsonify
import os
from Neo4J_API import InstacartAPI
from Neo4J_Driver import preprocessing, cosine_edges
import traceback

"""
IMPORTANT: Make sure to change Neo4J API credentials below 

How to run app and use
1. go to terminal and go to directory of Git folder
2. run "python app.py"
3. After code is running (should see this message in terminal: 

"Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with watchdog (fsevents)"
 
 4. Go to http://127.0.0.1:5000/ to access UI
"""
app = Flask(__name__)
# Input your Neo4J credentials
api = InstacartAPI(uri='neo4j://localhost:7687', username='neo4j', password='theflash')
df = preprocessing('order_products__train.csv', 'products.csv', 'departments.csv', 'aisles.csv', 2000)
similarity = cosine_edges(df)

# Save the nodes and edges data frames to CSV files (to run on your device, change the directory appropriately)
df.to_csv('/Users/justinwoo/neo4j-community-5.5.0/import/instacart.csv', index=False)
similarity.to_csv('/Users/justinwoo/neo4j-community-5.5.0/import/similarity.csv', index=False)

api.reset_db()
api.load_graph()
api.load_similarity_edge()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def get_recommendations():
    try:
        items = request.json["items"]
        recommendations = api.recommend_item_to_cart(items)
        return jsonify({"recommendations": recommendations})
    except Exception as e:
        print("Error: ", e)
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/replacement", methods=["POST"])
def replacement_recommendation():
    data = request.get_json()
    product = data.get("product")
    recommendations = api.replacement_recommendation(product)
    print("Replacement Recommendations:", recommendations)
    return jsonify({"recommendations": recommendations})

@app.route("/aisle", methods=["POST"])
def aisle_recommendation():
    data = request.get_json()
    aisle = data.get("aisle")
    recommendations = api.aisle_recommendation(aisle)
    print("Aisle Recommendations:", recommendations)
    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    app.run(debug=True)