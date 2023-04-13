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
            result = session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///instacart.csv' AS row
            MERGE (a:Order {order_id:row.order_id}) 
            MERGE (b:Product {product_name: row.product_name})
            ON CREATE SET b.department = row.department, b.aisle = row.aisle
            MERGE (a)-[:Ordered]->(b)
            """)

    def load_similarity_edge(self):
        """
        :parameter: None
        :return: None
        """

        with self.con.session() as session:
            result = session.run("""
            LOAD CSV WITH HEADERS FROM "file:///similarity.csv" AS row
            MATCH (p1:Product {product_name: row.product_1})
            MATCH (p2:Product {product_name: row.product_2})
            MERGE (p1)-[r:SIMILAR]->(p2)
            SET r.cosine_similarity = toFloat(row.cosine_similarity);
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

    def replacement_recommendation(self, product):
        """
        Recommend products based on the inputted product to simulate if an item is out of stock. Retrieves the top 3
        product nodes with the highest cosine similarity in the edge connected to them
        :param product(string): name of product that you want to find a substitute for
        :return: top 3 product nodes with highest cosine similarity to it
        """
        with self.con.session() as session:
            result = session.run("""
                MATCH (p1:Product {product_name: $product_name})-[r:SIMILAR]->(p2:Product)
                RETURN p2.product_name AS recommended_product, r.cosine_similarity AS similarity
                ORDER BY r.cosine_similarity DESC
                LIMIT 3
            """, product_name=product)


            records = [dict(record) for record in result]
            return records if records else None

    def aisle_recommendation(self, aisle):
        """
        Recommend items based on popularity of inputted aisle
        Retrieve the 5 most popular items in the aisle of the inputted product with their counts

        :param aisle(string): aisle
        :return: recommendation(list): return 5 items:
        """
        with self.con.session() as session:
            result = session.run("""
                    MATCH (o:Order)-[:Ordered]->(p:Product)
                    WHERE p.aisle = $aisle
                    WITH p, count(o) as orderCount
                    ORDER BY orderCount DESC
                    LIMIT 5
                    RETURN p.product_name as product, orderCount
                """, aisle=aisle)

            records = [dict(record) for record in result]
            return records

    def close(self):
        """
        Close the connection
        :return: None
        """
        self.con.close()
