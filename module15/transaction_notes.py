from firebase_admin import firestore, initialize_app, credentials
import datetime
import firebase_admin

PROJECT_ID = 'edurekali-1620623900283'
cred = credentials.Certificate("edurekali-1620623900283-97316d3e8189.json")
firebase_admin.initialize_app(cred, {'projectId': PROJECT_ID})
db = firestore.client()



batch = db.batch()
users_ref = db.collection("users")

for i in range(1,101):
    user_id = f"user{i}"
    user_data = {
        'name': f"User name {i}",
        'email': f'User{i}@example.com',
        'created_at': firestore.SERVER_TIMESTAMP,
        'notes': []
    }
    doc_ref = users_ref.document(user_id)
    batch.set(doc_ref, user_data)

try:
    batch.commit()
    print(f"Successfully added 100 users to 'users' colection")
except Exception as e:
    print(f"batch failed rolledback : {e}")

print("\nSample users:")
users = users_ref.limit(5).stream()
for user in users:
    data = user.to_dict()
    print(f"ID: {user.id}, Name: {data.get('name', '(no name field)')}")

firebase_admin.delete_app(firebase_admin.get_app())

# @firestore.transactional
# def move_old_notes(transaction, user_id):
#     old_notes = list(
#         db.collection('notes')
#           .where('userId', '==', user_id)
#           .where('date', '<=', (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat())
#           .limit(3)
#           .stream()
#     )

#     for i, doc in old_notes:
#         if i == 1:
#             raise Exception("Intentional rolleback")
#         data = doc.to_dict()
#         transaction.delete(doc.reference)
#         archived_ref = db.collection('users').document(user_id).collection('archived_notes').add(data)
#         print(f"Moved {doc.id} to archived: {archived_ref[1].id}")


# transaction = db.transaction()
# move_old_notes(transaction, 'alice')
