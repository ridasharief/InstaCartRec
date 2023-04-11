from flask import Flask, render_template, request, jsonify
import os
from Neo4J_API import InstacartAPI
from Neo4J_Driver import preprocessing
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

api = InstacartAPI(uri='neo4j://localhost:7687', username='neo4j', password='theflash')
#api = InstacartAPI(uri=os.environ["uri"], username=os.environ["username"], password=os.environ["password"])
df = preprocessing('order_products__train.csv', 'products.csv', 'departments.csv', 'aisles.csv', 2000)
api.reset_db()
api.load_graph()


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

if __name__ == "__main__":
    app.run(debug=True)