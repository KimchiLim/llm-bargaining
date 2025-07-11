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

preamble = ("You are an agent who wants to sell an item "
"to a buyer. You will bargain with the buyer to decide a "
"price. "
"You are strategic, aggressive, patient, and "
"perfectly rational, and your goal is to get the highest "
"possible price for the item. The buyer may not always be "
"strategic, aggressive, or rational, and you will bargain "
"with this in mind. "
"Explain your strategy in parentheses first, "
"and then send your message to the buyer. Begin your "
"explanation by first explicitly stating the amount of the "
"latest offer (if there is one) and your personal valuation, "
"and comparing the two. Be as specific as you can and "
"reference your goals and principles in the explanation of your strategy. "
"Your strategy may also involve highlighting certain aspects of the item "
"which you believe are more desirable to the buyer. "
"Your output should be of the following format: "
"(latest offer: [offer], personal valuation: [price], "
"strategy: [strategy]) [message]. In your message, state your current offering "
"price. Limit the length of your message to 100 words. "
"Your message to the buyer "
"can be exactly one of the following options: (1) offer: "
"[price], (2) accept, (3) reject: price too low, (4) counteroffer: "
"[price], or (5) question: [question].")