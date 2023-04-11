"""
@author: Justin Woo
@file  : Neo4J_Driver.py
Driver file for Neo4J API
"""
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler
from Neo4J_API import InstacartAPI
import warnings
from pandas.core.common import SettingWithCopyWarning
from sklearn.metrics import euclidean_distances
warnings.filterwarnings('ignore', category=SettingWithCopyWarning)

def preprocessing(orders, products, departments, aisle, num_orders):
    """
    Imports all data and merges them together
    Filter and scale subset
       - remove duplicate track_id
       - remove duplicate rows (identical values aside from track_id, album_name, and popularity)
       - scale numeric columns
    :param orders(string): name of orders file
    :param products(string): name of products file
    :param departments(string): name of departments file
    :param aisle(string): name of aisle file
    :param num_orders(int): number of unique orders to load as nodes
    :return: filtered_df: dataframe to be imported into Neo4J as nodes and to be used to create/ calculate edges
    """
    # Read the CSV files into a pandas DataFrames
    orders_df = pd.read_csv(orders)
    products_df = pd.read_csv(products)
    departments_df = pd.read_csv(departments)
    aisle_df = pd.read_csv(aisle)

    # Extract num_orders of orders from orders df
    sample = np.unique(orders_df['order_id'])[:num_orders]
    orders_sample = orders_df[orders_df['order_id'].isin(sample)]
    orders_sample.nunique()
    """
    Imports all data and merges them together
    Filter and scale subset
       - remove duplicate track_id
       - remove duplicate rows (identical values aside from track_id, album_name, and popularity)
       - scale numeric columns
    :param orders(string): name of orders file
    :param products(string): name of products file
    :param departments(string): name of departments file
    :param aisle(string): name of aisle file
    :param num_orders(int): number of unique orders to load as nodes
    :return: filtered_df: dataframe to be imported into Neo4J as nodes and to be used to create/ calculate edges
    """
    # Read the CSV files into a pandas DataFrames
    orders_df = pd.read_csv(orders)
    products_df = pd.read_csv(products)
    departments_df = pd.read_csv(departments)
    aisles_df = pd.read_csv(aisle)

    # Extract num_orders of orders from orders df
    sample = np.unique(orders_df['order_id'])[:num_orders]
    orders_sample = orders_df[orders_df['order_id'].isin(sample)]
    orders_sample.nunique()

    # Consolidate DataFrames into 1

    # Join products data
    consolidated_df = pd.merge(orders_sample, products_df, on='product_id', how='inner')
    # Join departments data
    consolidated_df = pd.merge(consolidated_df, departments_df, on='department_id', how='inner')
    # Join aisles data
    consolidated_df = pd.merge(consolidated_df, aisles_df, on='aisle_id', how='inner')

    # Filter only relevent columns
    final_df = consolidated_df[['order_id', 'product_name', 'department', 'aisle']]

    # Clean data

    # Filter out rows where department or aisle are "missing"
    final_df = final_df[(final_df['department'] != "missing") | (final_df['aisle'] != 'missing')]

    # Filter out rows where department or aisle are "other"
    final_df = final_df[(final_df['department'] != "other") | (final_df['aisle'] != 'other')]

    # Remove '/"' from product name column as double-quote aren't permitted in Neo4J
    final_df['product_name'] = final_df['product_name'].str.replace(r'\\\"', '')
    return final_df


def main():
    #api = InstacartAPI(uri=os.environ["uri"], username=os.environ["username"], password=os.environ["password"])
    api = InstacartAPI(uri='neo4j://localhost:7687', username='neo4j', password='theflash')
    # Preprocessing step
    df = preprocessing('order_products__train.csv', 'products.csv', 'departments.csv', 'aisles.csv', 2000)

    # Save the nodes and edges data frames to CSV files (to run on your device, change the directory appropriately)
    df.to_csv('/Users/justinwoo/neo4j-community-5.5.0/import/instacart.csv', index=False)

    # Neo4J Commands

    # Reset database
    api.reset_db()
    # Load nodes
    api.load_graph()

    # Make recommendation
    rec = api.recommend_item_to_cart(['Bulgarian Yogurt', 'Organic Whole String Cheese', 'Bag of Organic Bananas'])
    print(rec)
    # Close Connection
    api.close()
if __name__ == '__main__':
    main()

