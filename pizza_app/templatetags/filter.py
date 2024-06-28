from django.template import Library
from pizza_app.models import Items

register = Library()

@register.filter(name = 'correct_position')
def correct_position(pizza):
    pizza_id = pizza.id

    if (pizza_id <= 3):
        return True
    elif (pizza_id > 3 and pizza_id <= 6):
        return False
    elif (pizza_id >6 and pizza_id <= 9):
        return True
    else:
        return False
    

@register.filter(name = 'summarize_description')
def summarize_description(desc, sentence_len):
    return f"{desc[:int(sentence_len)]}..."