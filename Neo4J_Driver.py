"""
@author: Justin Woo
@file  : Neo4J_Driver.py
Driver file for Neo4J API
"""
import pandas as pd
import numpy as np
from Neo4J_API import InstacartAPI
import os
import warnings
from pandas.core.common import SettingWithCopyWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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
    final_df = consolidated_df[['order_id','product_id', 'product_name', 'department', 'aisle']]

    # Clean data

    # Filter out rows where department or aisle are "missing"
    final_df = final_df[(final_df['department'] != "missing") | (final_df['aisle'] != 'missing')]

    # Filter out rows where department or aisle are "other"
    final_df = final_df[(final_df['department'] != "other") | (final_df['aisle'] != 'other')]

    # Remove '/"' from product name column as double-quote aren't permitted in Neo4J
    final_df['product_name'] = final_df['product_name'].str.replace(r'\\\"', '')
    return final_df

def cosine_edges(df):
    """
    Create a DataFrame with columns product_1, product_2 and similarity to create edges between products to be used
    for item replacement recommendation engine
    :param df(DataFrame): Merged data created from preprocessing
    :return: cosine_edges(DataFrame): DataFrame to be used to import edges from Product to Product
    """
    # Create a new DataFrame with unique product names and their corresponding product IDs
    unique_products_df = df[['product_id', 'product_name']].drop_duplicates()

    # Create a TfidfVectorizer object
    vectorizer = TfidfVectorizer()

    # Transform the 'product_name' column into a matrix of TF-IDF features
    tfidf_matrix = vectorizer.fit_transform(unique_products_df['product_name'])

    # Calculate cosine similarity between all product names
    cosine_sim_matrix = cosine_similarity(tfidf_matrix)

    # Create a DataFrame with the cosine similarity scores between products
    product_names = df['product_name'].unique()
    similarity_df = pd.DataFrame(cosine_sim_matrix, index=product_names, columns=product_names)

    # Convert the similarity matrix to a long format
    long_similarity_df = similarity_df.stack().reset_index()
    long_similarity_df.columns = ['product_1', 'product_2', 'cosine_similarity']

    # Remove rows where product_1 is the same as product_2 (self-similarity)
    long_similarity_df = long_similarity_df[long_similarity_df['product_1'] != long_similarity_df['product_2']]

    # Remove rows with 0 similarity
    long_similarity_df = long_similarity_df[long_similarity_df['cosine_similarity'] > 0]

    # Calculate the 80th percentile value to use as a threshold
    threshold = long_similarity_df['cosine_similarity'].quantile(0.80)

    # Filter out rows with similarity scores lower than the average
    filtered_similarity_df = long_similarity_df[long_similarity_df['cosine_similarity'] > threshold]
    return filtered_similarity_df

def main():
    pass

if __name__ == '__main__':
    main()

