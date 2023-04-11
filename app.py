from flask import Flask, render_template, request, jsonify
import os
from Neo4J_API import InstacartAPI
from Final_Project_Driver import preprocessing
import traceback


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