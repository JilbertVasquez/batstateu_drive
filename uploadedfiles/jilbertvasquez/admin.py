# Name:  
# Student Number:  

# This file is provided to you as a starting point for the "admin.py" program of Assignment 2
# of Programming Principles in Semester 1, 2024.  It aims to give you just enough code to help ensure
# that your program is well structured.  Please use this file as the basis for your assignment work.
# You are not required to reference it.

# The "pass" command tells Python to do nothing.  It is simply a placeholder to ensure that the starter file runs smoothly.
# They are not needed in your completed program.  Replace them with your own code as you complete the assignment.


# Import the json module to allow us to read and write data in JSON format.
import json




# This function repeatedly prompts for input until an integer is entered.
# See Point 1 of the "Functions in admin.py" section of the assignment brief.
def input_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter an integer.")


# This function repeatedly prompts for input until something other than whitespace is entered.
# See Point 2 of the "Functions in admin.py" section of the assignment brief.
def input_something(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value


# This function opens "data.txt" in write mode and writes the data to it in JSON format.
# See Point 3 of the "Functions in admin.py" section of the assignment brief.
def save_data(data_list):
    with open("data.txt", "w") as file:
        json.dump(data_list, file, indent=4)




# Here is where you attempt to open data.txt and read the data into a "data" variable.
# If the file does not exist or does not contain JSON data, set "data" to an empty list instead.
# This is the only time that the program should need to read anything from the file.
# See Point 1 of the "Requirements of admin.py" section of the assignment brief.


def load_data():
    try:
        with open("data.txt", "r") as file:
            data = json.load(file)
    except:
        data = []
    return data

data = load_data()


# Print welcome message, then enter the endless loop which prompts the user for a choice.
# See Point 2 of the "Requirements of admin.py" section of the assignment brief.
# The rest is up to you.
print('Welcome to the Quiz Admin Program.')

while True:
    print('\nChoose [a]dd, [l]ist, [s]earch, [v]iew, [d]elete or [q]uit.')
    choice = input('> ')
        
    if choice == 'a':
        # Add a new question.
        # See Point 3 of the "Requirements of admin.py" section of the assignment brief.
        question = input_something("Enter the question: ")
        
        answers = []
        while True:
            ans = input_something('Enter a valid answer (enter "q" when done): ')
            if ans.lower() == 'q':
                break
            else:
                answers.append(ans.lower())
            
        difficulty = input_int("Enter question difficulty (1-5): ")
        
        question_struct = {
            "question": question,
            "answers": answers,
            "difficulty": difficulty
        }
        
        data.append(question_struct)
        save_data(data)
        
        print("Question added!")



    elif choice == 'l':
        # List the current questions.
        # See Point 4 of the "Requirements of admin.py" section of the assignment brief.
        if data:
            print("Current Questions:")
            i = 1
            for question_data in data:
                print("\t" + str(i) + ") " + question_data["question"])
                i += 1
        else:
            print("No question is saved")


    elif choice == 's':
        # Search the current questions.
        # See Point 5 of the "Requirements of admin.py" section of the assignment brief.
        if data:
            search_word = input_something("Enter a search term: ")
            print("Search results:")
            found = False
            i = 1
            for question_data in data:
                if search_word.lower() in question_data["question"]:
                    print("\t" + str(i) + ") " + question_data["question"])
                    i += 1
                    found = True
            
            if not found:
                print("No results found")
        else:
            print("No question saved")



    elif choice == 'v':
        # View a question.
        # See Point 6 of the "Requirements of admin.py" section of the assignment brief.
        if data:
            view = input_int("Question number to view: ")
            if 1 <= view <= len(data):
                question_data = data[view - 1]
                print("\nQuestion:")
                print("\t" + question_data["question"])
                if len(question_data["answers"]) == 1:
                    print("\nAnswer:", question_data["answers"][0])
                else:
                    print("Answers:", ", ".join(question_data['answers']))
                print("Difficulty:", question_data["difficulty"])
            else:
                print("Invalid index number")
        else:
            print("No question saved")



    elif choice == 'd':
        # Delete a question.
        # See Point 7 of the "Requirements of admin.py" section of the assignment brief.
        if data:
            delete = input_int("Question number to delete: ")
            if 1 <= delete <= len(data):
                del data[delete - 1]
                print("Question deleted!")
                save_data(data)
            else:
                print("Invalid index number")
        else:
            print("No questions saved")


    elif choice == 'q':
        # Quit the program.
        # See Point 8 of the "Requirements of admin.py" section of the assignment brief.
        print("Goodbye!")
        break



    else:
        # Print "invalid choice" message.
        # See Point 9 of the "Requirements of admin.py" section of the assignment brief.
        print("Invalid choice")

# If you have been paid to write this program, please delete this comment.
