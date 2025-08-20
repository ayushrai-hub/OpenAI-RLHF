from IPython.display import display
def greeting_program():
    CREATOR_NAME = "Mike Johnson"
    complete_user: str = input('Can you tell me your full name? ')
    first_user: str = complete_user.split(' ')[0]
    firstname_creator: str = CREATOR_NAME.split(' ')[0]
    greeting: str = "Hi {user_name}! I'm {CREATOR_NAME}, pleased to meet you.".format(user_name=first_user, CREATOR_NAME=firstname_creator)
    display(greeting)
    return greeting 

if __name__ == "__main__":
    greeting_program()