from IPython.display import display

CREATOR_NAME = 'Mike Johnson'

def greeting_program() -> str:
    complete_user: str = input('Can you tell me your full name? ')
    
    first_user: str = complete_user.split(' ')[0]
    
    firstname_creator: str = CREATOR_NAME.split(' ')[0]
    
    greeting: str = 'Hi {user_name}! I\'m {creator_name}, pleased to meet you.'.format(user_name=first_user, creator_name=firstname_creator)
    
    display(greeting)
    return greeting
