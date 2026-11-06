"""Smart category prediction using simple keyword matching.

To upgrade later, replace `predict_category` with an NLP / ML model
(e.g. scikit-learn text classifier) - the rest of the app won't change.
"""
import re

KEYWORDS = {
    "Food": [
        "pizza", "burger", "lunch", "dinner", "breakfast", "snack", "restaurant",
        "cafe", "coffee", "tea", "swiggy", "zomato", "dominos", "mcdonald", "kfc",
        "biryani", "grocer", "vegetable", "fruit", "milk", "bakery", "food", "meal",
    ],
    "Travel": [
        "uber", "ola", "taxi", "cab", "bus", "train", "metro", "flight", "petrol",
        "diesel", "fuel", "toll", "parking", "rapido", "irctc", "ticket", "travel",
        "hotel", "auto",
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "shirt", "shoe", "jeans", "dress", "clothes",
        "mall", "shopping", "gift", "watch", "bag", "electronics", "mobile", "laptop",
    ],
    "Bills": [
        "electricity", "water bill", "wifi", "internet", "broadband", "recharge",
        "rent", "gas", "bill", "insurance", "emi", "loan", "postpaid",
    ],
    "Entertainment": [
        "movie", "netflix", "prime", "hotstar", "spotify", "game", "concert",
        "cinema", "youtube", "party", "pub", "club", "outing",
    ],
    "Health": [
        "doctor", "medicine", "pharmacy", "hospital", "clinic", "dental", "gym",
        "medical", "checkup", "lab test", "vitamin", "yoga",
    ],
    "Education": [
        "book", "course", "tuition", "school", "college", "fee", "exam", "udemy",
        "coursera", "stationery", "notebook", "pen", "class",
    ],
}


def predict_category(description: str) -> str:
    text = (description or "").lower()
    for category, words in KEYWORDS.items():
        for word in words:
            if re.search(rf"\b{re.escape(word)}", text):
                return category
    return "Other"
