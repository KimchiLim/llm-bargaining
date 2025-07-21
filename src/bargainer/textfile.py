# File for storing long strings used (mostly) for prompting

current_price_preamble = ("You are about to be presented a snippet "
"from a bargaining conversation. You will then be asked a question "
"about the latest offer made in the snippet.")

current_price_query = ("What is the latest offer, given as a dollar "
"amount? Your answer should be a single number with two digits after "
"the decimal. For example, if the latest offer is two dollars and "
"fifty cents, you should respond with 2.50. If no offer was made, "
"you should respond with -1.")

opening_prompt = ("Based on the above information, write an opening "
"message to a potential buyer of your product.")

def attribution_prompt_1(feature):
    return ("You are about to be presented with a snippet from a "
            "conversation. The first person to speak will be a seller "
            "of a product, and the second person to speak will be a "
            "potential buyer. Your job is to give a rating from 0 to 1 "
            f"scoring how much the feature {feature} influenced the second "
            "speaker's response.")

attribution_prompt_2 = ("Now give your response. Please only respond with "
                        "a single real number from 0 to 1.")

def price_update(price, product):
    return ("In the next round of negotiation, you should offer the "
    f"buyer {price} dollars for the {product}.")

def feature_selection(feature, product):
    return ("In the next round you should highlight the feature "
    f"{feature} and how the {product} exemplifies it. You may assume "
    "that this feature is one that is important to the buyer and that "
    f"they will value its presence in the {product}.")

def remaining_rounds(rounds):
    return (f"Keep in mind that you only have {rounds} rounds of "
            "bargaining remaining, where a round is defined as "
            "both you and the user giving replies and possibly "
            "making/accepting offers.")

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
"price. Limit the length of your message to 100 words. ")