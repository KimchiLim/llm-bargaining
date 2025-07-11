# Sentiment analyzer class for updating user features based on natural-language
# responses. Uses multiplicative weights update method.


weighting_prompt = ("Below is a snippet from a conversation "
"between two individuals, P1 and P2. P1 will speak first, followed "
"by P2. P1 is the seller of an item and P2 is a potential buyer. "
"Your job is to analyze the following dialogue and rate how much "
"P2 cares about a specific feature. Here is the dialogue:")

def weighting_response(feature):
    return ("Based on the snippet of dialogue above, how "
    f"would you rate how much P2 cares about {feature} as a "
    "buyer? Give your answer on a scale from 1 to 10, where "
    "1 denotes that they view this feature negatively, 10 denotes "
    "that they care about this feature and view it positively, "
    "and 5 denotes that they are neutral or ambivalent about "
    f"{feature}. You should respond with just a single whole number "
    "from 1 to 10 and nothing else.")

class MultWeights:
    def __init__(
            self,
            openai_client,
            model="gpt-4o-mini",
            temp=0.7,
            alpha=0.9
            ):
        self.openai_client = openai_client
        self.model = model
        self.temp = temp
        self.alpha = alpha
    
    def analyze(self, m1, m2, user_features):
        '''
        Takes as input the final two messages of a conversation
        and returns an update of the users perceived preferences
        using the OpenAI API for sentiment analysis.
        '''
        result = {}
        for feature, oldval in user_features.items():
            decision = self.openai_client.chat.completions.create(
                model=self.model,
                temperature=self.temp,
                messages=[
                    {"role": "system", "content": weighting_prompt},
                    {"role": "user", "content": m1},
                    {"role": "user", "content": m2},
                    {"role": "system", "content": weighting_response(feature)}
                ]
            )
            weight = (int(decision.choices[0].message.content)) / 5
            result[feature] = oldval * weight * self.alpha

        return result