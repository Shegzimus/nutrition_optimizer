import cvxpy as cp
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

# Macronutrient Ratios (in percentages); subject to change based on prefered fitness goals
protein_ratio = 30  # 30% protein
fat_ratio = 25      # 25% fats
carb_ratio = 45     # 45% carbs

# Calculate target macronutrients based on protein target
protein_target = 100
total_calories = (protein_target * 4) / (protein_ratio / 100)
fat_target = (total_calories * (fat_ratio / 100)) / 9
carb_target = (total_calories * (carb_ratio / 100)) / 4

# Budget and calorie caps (test values)
budget_cap = 3000
calorie_cap = 15000

# Decision variables
x = {p["name"]: cp.Variable(integer=True) for p in products}  # Number of units purchased
z = {p["name"]: cp.Variable() for p in products}  # Fraction of 100g purchased

# Objective: Maximize protein intake
objective = cp.Maximize(sum(p["protein_per_100g"] * z[p["name"]] for p in products))

# Constraints
constraints = []

# Macronutrient constraints
constraints.append(sum(p["protein_per_100g"] * z[p["name"]] for p in products) >= protein_target)
constraints.append(sum(p["fats_per_100g"] * z[p["name"]] * 9 for p in products) == fat_target * 9)
constraints.append(sum(p["carbs_per_100g"] * z[p["name"]] * 4 for p in products) == carb_target * 4)

# Budget and calorie caps
constraints.append(sum(p["price_per_unit"] * x[p["name"]] for p in products) <= budget_cap)
constraints.append(sum(p["calories_per_100g"] * z[p["name"]] for p in products) <= calorie_cap)

# Connect constraints using net weight and number of whole number purchases
for p in products:
    constraints.append((p["net_weight"] * x[p["name"]]) / z[p["name"]]  == 100 )

# Solve the problem
problem = cp.Problem(objective, constraints)
problem.solve()

# Results
print("Status:", problem.status)
data = []
for p in products:
    product_name = p["name"]
    units_purchased = x[p["name"]].value
    total_price = p["price_per_unit"] * units_purchased
    data.append({
        "Product Name": product_name,
        "Price (€)": p["price_per_unit"],
        "Recommended Quantity": int(units_purchased) if units_purchased is not None else 0,
        "Total Price (€)": total_price
    })

df = pd.DataFrame(data)
print(df)
