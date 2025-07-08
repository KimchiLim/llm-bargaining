# File for storing long strings used (mostly) for prompting

current_price_preamble = ("You are about to be presented a snippet "
"from a bargaining conversation. You will then be asked a question "
"about the latest offer made in the snippet.")

current_price_query = ("What is the latest offer, given as a dollar "
"amount? Your answer should be a single number with two digits after "
"the decimal. For example, if the latest offer is two dollars and "
"fifty cents, you should respond with 2.50. If no offer was made, "
"you should respond with -1.")

def price_update(price, product):
    return ("In the next round of negotiation, you should offer the "
    f"buyer {price} dollars for the {product}.")

def feature_selection(feature, product):
    return ("In the next round you should highlight the feature "
    f"{feature} and how the {product} exemplifies it. You may assume "
    "that this feature is one that is important to the buyer and that "
    f"they will value its presence in the {product}.")