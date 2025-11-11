from firebase_admin import credentials, firestore, initialize_app
cred = credentials.Certificate("edurekali-1620623900283-97316d3e8189.json")
initialize_app(cred)

PROJECT_ID = "edurekali-1620623900283"
DB_NAME = "notesdb"
db = firestore.client()


docs = db.collection('notes').where('userId', '==', 'alice').order_by('date', direction=firestore.Query.DESCENDING).limit(5).stream()
for doc in docs:
    print(doc.to_dict())