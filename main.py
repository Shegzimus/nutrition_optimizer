from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value

# Define real product data
products = [
    {"name": "Chicken Breast", "price_per_unit": 5.0, "net_weight": 1000, "protein_per_100g": 31, "calories_per_100g": 165},
    {"name": "Eggs (12 pack)", "price_per_unit": 3.0, "net_weight": 720, "protein_per_100g": 12.6, "calories_per_100g": 143},
    {"name": "Milk (1L)", "price_per_unit": 1.5, "net_weight": 1000, "protein_per_100g": 3.4, "calories_per_100g": 42},
    {"name": "Greek Yogurt (500g)", "price_per_unit": 2.5, "net_weight": 500, "protein_per_100g": 10, "calories_per_100g": 59},
    {"name": "Oats (1kg)", "price_per_unit": 3.0, "net_weight": 1000, "protein_per_100g": 13, "calories_per_100g": 389},
    {"name": "Tuna Cans (185g)", "price_per_unit": 1.5, "net_weight": 185, "protein_per_100g": 24, "calories_per_100g": 128},
    {"name": "Tofu (400g)", "price_per_unit": 2.0, "net_weight": 400, "protein_per_100g": 8, "calories_per_100g": 76},
    {"name": "Broccoli (500g)", "price_per_unit": 2.0, "net_weight": 500, "protein_per_100g": 2.8, "calories_per_100g": 35},
    {"name": "Peanut Butter (1kg)", "price_per_unit": 5.0, "net_weight": 1000, "protein_per_100g": 25, "calories_per_100g": 588},
    {"name": "Brown Rice (1kg)", "price_per_unit": 4.0, "net_weight": 1000, "protein_per_100g": 7.5, "calories_per_100g": 370},
]

# Parameters
protein_target = 600  # Minimum protein requirement (grams)
budget_cap = 80       # Budget cap (euros)
calorie_cap = 14000   # Maximum calorie limit (kcal)

# Create the optimization problem
problem = LpProblem("Optimize_Grocery_List", LpMaximize)

# Define decision variables
z = {p["name"]: LpVariable(f"z_{p['name']}", lowBound=0, upBound=1, cat="Continuous") for p in products}
x = {p["name"]: LpVariable(f"x_{p['name']}", lowBound=0, cat="Integer") for p in products}  # Integer constraint

# Objective: Maximize protein intake
problem += lpSum(p["protein_per_100g"] * z[p["name"]] for p in products), "Maximize_Protein"

# Constraints
# Protein target
problem += lpSum(p["protein_per_100g"] * z[p["name"]] for p in products) >= protein_target, "Protein_Target"

# Budget cap
problem += lpSum(p["price_per_unit"] * x[p["name"]] for p in products) <= budget_cap, "Budget_Cap"

# Calorie cap
problem += lpSum(p["calories_per_100g"] * z[p["name"]] for p in products) <= calorie_cap, "Calorie_Cap"

# Linking z_n and x_n (ensures z_n corresponds to the fraction of net weight purchased)
for p in products:
    product_name = p["name"]
    problem += z[product_name] * p["net_weight"] <= x[product_name] * 100, f"Linking_{product_name}"

# Solve the problem
problem.solve()

# Print the results
print("Status:", problem.status)
for p in products:
    product_name = p["name"]
    print(f"{product_name}:")
    print(f"  Fraction of 100g purchased (z_n): {z[product_name].varValue:.2f}")
    print(f"  Number of units purchased (x_n): {int(x[product_name].varValue) if x[product_name].varValue is not None else 0}")

# Print the total protein, price, and calories
total_protein = sum(p["protein_per_100g"] * z[p["name"]].varValue for p in products)
total_price = sum(p["price_per_unit"] * x[p["name"]].varValue for p in products)
total_calories = sum(p["calories_per_100g"] * z[p["name"]].varValue for p in products)

print(f"Total Protein: {total_protein:.2f} g")
print(f"Total Price: €{total_price:.2f}")
print(f"Total Calories: {total_calories:.2f} kcal")
