from pulp import LpMaximize, LpProblem, LpVariable, lpSum
import pandas as pd

# Define real product data with fats and carbs
products = [
    {"name": "Chicken Breast", "price_per_unit": 5.0, "net_weight": 1000, "protein_per_100g": 31, "calories_per_100g": 165, "fats_per_100g": 3.6, "carbs_per_100g": 0},
    {"name": "Eggs (12 pack)", "price_per_unit": 3.0, "net_weight": 720, "protein_per_100g": 12.6, "calories_per_100g": 143, "fats_per_100g": 10, "carbs_per_100g": 1},
    {"name": "Milk (1L)", "price_per_unit": 1.5, "net_weight": 1000, "protein_per_100g": 3.4, "calories_per_100g": 42, "fats_per_100g": 1, "carbs_per_100g": 5},
    {"name": "Greek Yogurt (500g)", "price_per_unit": 2.5, "net_weight": 500, "protein_per_100g": 10, "calories_per_100g": 59, "fats_per_100g": 0.4, "carbs_per_100g": 3.6},
    {"name": "Oats (1kg)", "price_per_unit": 3.0, "net_weight": 1000, "protein_per_100g": 13, "calories_per_100g": 389, "fats_per_100g": 6.9, "carbs_per_100g": 66},
    {"name": "Tuna Cans (185g)", "price_per_unit": 1.5, "net_weight": 185, "protein_per_100g": 24, "calories_per_100g": 128, "fats_per_100g": 0.5, "carbs_per_100g": 0},
    {"name": "Tofu (400g)", "price_per_unit": 2.0, "net_weight": 400, "protein_per_100g": 8, "calories_per_100g": 76, "fats_per_100g": 4.8, "carbs_per_100g": 1.9},
    {"name": "Broccoli (500g)", "price_per_unit": 2.0, "net_weight": 500, "protein_per_100g": 2.8, "calories_per_100g": 35, "fats_per_100g": 0.4, "carbs_per_100g": 7},
    {"name": "Peanut Butter (500g)", "price_per_unit": 3.0, "net_weight": 500, "protein_per_100g": 25, "calories_per_100g": 588, "fats_per_100g": 50, "carbs_per_100g": 20},
    {"name": "Brown Rice (1kg)", "price_per_unit": 4.0, "net_weight": 1000, "protein_per_100g": 7.5, "calories_per_100g": 370, "fats_per_100g": 2.7, "carbs_per_100g": 77},
]
budget_cap= 3000
calorie_cap= 15000

# Macronutrient Ratios (in percentages)
protein_ratio = 30  # 30% protein
fat_ratio = 25      # 25% fats
carb_ratio = 45     # 45% carbs

# Protein Target in grams
protein_target = 100  # 600g protein

# Total Caloric Intake (from protein target)
total_calories = (protein_target * 4) / (protein_ratio / 100)

# Fat and Carb Targets in Calories
fat_calories = total_calories * (fat_ratio / 100)
carb_calories = total_calories * (carb_ratio / 100)

# Convert to grams (for fat and carbs)
fat_target = fat_calories / 9
carb_target = carb_calories / 4

# Create the optimization problem
problem = LpProblem("Optimize_Grocery_List", LpMaximize)

# Define decision variables
z = {p["name"]: LpVariable(f"z_{p['name']}", lowBound=0, upBound=1, cat="Continuous") for p in products}
x = {p["name"]: LpVariable(f"x_{p['name']}", lowBound=0, cat="Integer") for p in products}

# Objective: Maximize protein intake
problem += lpSum(p["protein_per_100g"] * z[p["name"]] for p in products), "Maximize_Protein"

# Constraints
# Protein target
problem += lpSum(p["protein_per_100g"] * z[p["name"]] for p in products) >= protein_target, "Protein_Target"

# Fat target (calories-based)
problem += lpSum(p["fats_per_100g"] * z[p["name"]] * 9 for p in products) == fat_calories, "Fat_Target"

# Carb target (calories-based)
problem += lpSum(p["carbs_per_100g"] * z[p["name"]] * 4 for p in products) == carb_calories, "Carb_Target"

# Budget cap
problem += lpSum(p["price_per_unit"] * x[p["name"]] for p in products) <= budget_cap, "Budget_Cap"

# Calorie cap
problem += lpSum(p["calories_per_100g"] * z[p["name"]] * 10 for p in products) <= calorie_cap, "Calorie_Cap"

# Linking z_n and x_n
for p in products:
    product_name = p["name"]
    problem += z[product_name] * p["net_weight"] <= x[product_name] * 100, f"Linking_{product_name}"

# Solve the problem
problem.solve()

# Print results
print("Status:", problem.status)
# for p in products:
#     product_name = p["name"]
#     print(f"{product_name}:")
#     print(f"  Fraction of 100g purchased (z_n): {z[product_name].varValue:.2f}")
#     print(f"  Number of units purchased (x_n): {int(x[product_name].varValue) if x[product_name].varValue is not None else 0}")

data = []

# Loop through products and calculate required values
for product in products:
     
    product_name = product["name"]

    # Get the values from z and x dictionaries (unit price and number of units purchased)
    price_per_unit = product["price_per_unit"]
    units_purchased = int(x[product_name].varValue) if x[product_name].varValue is not None else 0


    
    # Calculate total price for the product
    total_price = price_per_unit * units_purchased

    # Append the row of data
    data.append({
        "Product Name": product_name,
        "Price (€)": price_per_unit,
        "Recommended Quantity": units_purchased,
        "Total Price (€)": total_price
    })


df = pd.DataFrame(data)

print(df)

# Print total nutritional values
total_protein = sum(p["protein_per_100g"] * z[p["name"]].varValue for p in products)
total_price = sum(p["price_per_unit"] * x[p["name"]].varValue for p in products)
total_calories = sum(p["calories_per_100g"] * z[p["name"]].varValue for p in products)
total_fats = sum(p["fats_per_100g"] * z[p["name"]].varValue for p in products)
total_carbs = sum(p["carbs_per_100g"] * z[p["name"]].varValue for p in products)





print(f"Total Protein: {total_protein:.2f} g")
print(f"Total Fats: {total_fats:.2f} g")
print(f"Total Carbs: {total_carbs:.2f} g")
print(f"Total Price: €{total_price:.2f}")
print(f"Total Calories: {total_calories:.2f} kcal")
