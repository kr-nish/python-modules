from typing import Optional, Union, List

import json, csv

def greet(name: str, age: int) -> str:
    return f"Greetings {name}, you are {age} years old!"

print(greet(30, "Nishant"));

def find_user(id: int) -> Optional[str]:
    if id == 1:
        return "Nishant"
    return None

def parse_value(x: Union[int, str]) -> str:
    return str(x)

def process_scores(scores: List[int]) -> float:
    return sum(scores)/ len(scores)


with open("user.txt", "w") as f:
    f.write("username is Nishant! \n")
    f.write("User is fond of Python. \n")


with open("user.txt", "a") as f:
    f.write("Adding a new line to show apended data \n")

with open("user.txt", "r") as f:
    content = f.read()

print("File content:\n", content)

data = {"Name":"Ankit","age":30,"Skills":["GCP","Python"]}

with open("menu.json", "w") as f:
    json.dump(data, f)

with open("menu.json", "r") as f:
    loaded_menu = json.load(f)

print("Menu Json is ", loaded_menu)


new_menu_data = {"Name":"Nishant","age":30,"Skills":["GCP","Python"]}


with open("menu.json", "r") as f:
    existing_data = json.load(f)

existing_data.update(new_menu_data)

with  open("menu.json", "w") as f:
    json.dump(existing_data, f, indent=4)

print("Updated Json:", existing_data)

#Write CSV
with open("users.csv", "w", newline="") as f: 
    writer = csv.writer(f)
    writer.writerow(["Username", "Identi-fier","One-time password"])
    writer.writerow(["booker12", "9012","04ap67"])
    writer.writerow(["booker123", "9013","12se74"])
    writer.writerow(["booker124", "9014","30no86"])

with open("users.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
        