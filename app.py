import pandas as pd
from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# Global variable to store association rules
association_rules_df = None

def load_rules():
    """Loads the association rules from the CSV file."""
    global association_rules_df
    try:
        # Load the rules from the most comprehensive support file
        association_rules_df = pd.read_csv('supermarket_association_rules_support_0.001.csv')
        print("Association rules loaded successfully.")
    except FileNotFoundError:
        print("Error: supermarket_association_rules_support_0.001.csv not found.")
        association_rules_df = pd.DataFrame() # Initialize empty DataFrame
    except Exception as e:
        print(f"Error loading association rules: {e}")
        association_rules_df = pd.DataFrame() # Initialize empty DataFrame

@app.route('/')
def home():
    """Home route for basic API check."""
    return "Supermarket Product Suggestion API is running!"

@app.route('/suggest_products', methods=['GET'])
def suggest_products():
    """
    Endpoint to suggest products based on association rules.
    Expects a query parameter 'product_name'.
    """
    product_name = request.args.get('product_name')

    if not product_name:
        return jsonify({"error": "Please provide a 'product_name' query parameter."}), 400

    if association_rules_df.empty:
        return jsonify({"error": "Association rules not loaded or available."}), 500

    # Filter rules where the given product_name is in the antecedents
    # We need to be careful with string matching for antecedents as they are comma-separated
    # For now, a simple 'in' check is used. For exact matching, we might need to parse.
    # Assuming 'antecedents' in the CSV are single items or comma-separated strings
    # For robust matching, we should split and check for membership if antecedents can be multiple items.
    # Based on your output, antecedents are single items for these top rules.
    relevant_rules = association_rules_df[
        association_rules_df['antecedents'].apply(
            lambda x: product_name.strip().lower() in [item.strip().lower() for item in x.split(',')]
        )
    ]

    if relevant_rules.empty:
        return jsonify({"suggestions": [], "message": f"No strong suggestions found for '{product_name}'."})

    # Sort by lift and get unique consequents
    relevant_rules = relevant_rules.sort_values(by='lift', ascending=False)
    suggestions = relevant_rules['consequents'].unique().tolist()

    return jsonify({"suggestions": suggestions})

if __name__ == '__main__':
    load_rules() # Load rules when the app starts
    app.run(debug=True) # Set debug=False for production