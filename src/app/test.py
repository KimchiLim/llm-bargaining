import requests

URL = 'http://localhost:8000'
conversation_id = 0

while True:
    print("Please select one of the following:")
    print("\t1. Start conversation")
    print("\t2. Continue conversation")
    print("\t3. Exit")
    option = input("> ")
    if option == '1':
        payload = {
            "max_rounds": 5,
            "product_id": "6870cb4cb15cd0c8dd92279e"
        }
        response = requests.post(URL + "/conversations", json=payload).json()
        if response["success"] == False:
            print("Ran into an error trying to start a conversation...")
        else:
            print(response["message"])
            conversation_id = response["conversation_id"]
            print(f"Conversation id is {conversation_id}")
    elif option == '2':
        print("You may respond with a counteroffer and message.")
        print("Please enter your counteroffer as a dollar amount:")
        counteroffer_str = input("> ")
        try:
            counteroffer = float(counteroffer_str)
        except Exception as e:
            print(f"[Error] {e}")
            continue
        print("Please enter your message:")
        message = input("> ")
        payload = {
            "offer": counteroffer,
            "message": message,
            "accept": False
        }
        response = requests.post(URL + f"/conversations/{conversation_id}", json=payload).json()
        if response["success"] == False:
            print("Ran into an error trying to continue the conversation...")
        else:
            print(response["message"])
            print("Latest offer: ", {response["offer"]})
    else:
        break
        
