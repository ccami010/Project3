from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField
import main_functions


# Passes database user without directly revealing it
user_info = main_functions.read_from_file("MongoUser.json")
username = user_info["username"]
password = user_info["password"]

# Links to MongoDB database
app = Flask(__name__)
app.config["SECRET_KEY"] = "KvloanMPIztpjVP8o7cPt-a-wG20Rqe5GvGvskbP"
app.config["MONGO_URI"] = "mongodb+srv://{0}:{1}@project3.5h3on.mongodb.net/" \
                          "db?retryWrites=true&w=majority".format(username, password)
mongo = PyMongo(app)

# Creates a list of categories
category_list = ["Employment",
                       "Supplies",
                       "Utilities",
                       "Rent",
                       "Internet",
                       "Phone",
                       "Advertising",
                       "Events",
                       "Other"]

# Recreates the category list for use as a flask field
category_list_long = []

for i in category_list:
    category_list_long.append((i, i))


# Creates the flask fields used in the website
class Expenses(FlaskForm):
    description = StringField("description")
    category = SelectField("category", choices=category_list_long)
    cost = DecimalField("cost")
    date = DateField("date")


# Function to calculate cost for each expense category
def get_total_expenses(category):
    # Adds total cost for a specific category
    my_expenses_category = mongo.db.expenses.find({"category": category})
    print(my_expenses_category)
    category_cost = 0
    for i in my_expenses_category:
        category_cost += i["cost"]
        print(i["cost"])
    return category_cost


# Since it is possible to enter a string value in the cost field
# This function makes sure that the resulting error is caught and handled
def check_if_string(cost_form):
    try:
        print(float(cost_form))
        return float(cost_form)
    except:
        return 0


# Renders index.html
@app.route('/')
def index():
    # Reads database collection
    my_expenses = mongo.db.expenses.find()

    # Adds total cost of expenses
    total_cost = 0
    for i in my_expenses:
        total_cost += float(i["cost"])

    # The index.html file will loop across this list to display categories and costs
    expenses_by_category = {}
    for i in category_list:
        expenses_by_category.update({i: get_total_expenses(i)})

    return render_template("index.html", total_cost=total_cost, expenses_by_category=expenses_by_category)


# Renders addExpenses.html
@app.route('/addExpenses', methods=['GET', 'POST'])
def addExpenses():
    expenses_form = Expenses(request.form)

    # When the user submits data
    if request.method == "POST":
        user_input = {
            "category": request.form["category"],
            "description": request.form["description"],
            "cost": check_if_string(request.form["cost"]),
            "date": request.form["date"],
        }

        mongo.db.expenses.insert(user_input)
        return render_template("expenseAdded.html")

    # When the user accesses the page normally
    return render_template("addExpenses.html", form=expenses_form)


# Runs the website
if __name__ == "__main__":
    app.run(debug=True, port=80)