"""
Justin Woo
Instacart Database API for Neo4J
"""
from neo4j import GraphDatabase

class InstacartAPI:
    def __init__(self, uri, username, password):
        """
        Initialize the databsae
        :param uri: db credentials
        :param username: db credentials
        :param password: db credentials
        """
        self.con = GraphDatabase.driver(
            uri, auth=(username, password))

    def reset_db(self):
        """
        Reset the graph database
        :return:
        """
        with self.con.session() as session:
            result = session.run("""
                   MATCH (n)
                   DETACH DELETE n
                   """)

    def load_graph(self):
        """
        Loads csv file that is created in the python code
        :parameter: None
        :return: None
            """
        with self.con.session() as session:
            with self.con.session() as session:
                result = session.run("""
                LOAD CSV WITH HEADERS FROM 'file:///instacart.csv' AS row
                MERGE (a:Order {order_id:row.order_id}) 
                MERGE (b:Product {product_name: row.product_name, department: row.department, aisle: row.aisle})
                MERGE (a)-[:Ordered]->(b)
                """)



    def recommend_item_to_cart(self, cart):
        """
        Recommend products based on the items within the inputted list. Retrieves all products that have appeared in
        orders with inputted list and outputs count of each

        :param cart(list): Inputted artist
        :return: recommendation(list): return 3 items and frequency with cart items:
        """
        # Query the database to get similarity scores for input songs
        with self.con.session() as session:
            result = session.run("""
                    MATCH (o:Order)-[:Ordered]->(cart_item:Product)
                    WHERE cart_item.product_name IN $cart
                    WITH o, collect(cart_item) AS cart_items
                    MATCH (o)-[:Ordered]->(:Product)<-[:Ordered]-(order:Order)-[:Ordered]->(recommended:Product)
                    WHERE NOT recommended IN cart_items
                    WITH recommended, count(DISTINCT order) AS frequency
                    ORDER BY frequency DESC
                    LIMIT 3
                    RETURN recommended.product_name, frequency
                """, cart=cart)

            records = [dict(record) for record in result]
            return records


    def close(self):
        """
        Close the connection
        :return: None
        """
        self.con.close()
