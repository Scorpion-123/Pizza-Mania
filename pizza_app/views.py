from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import pickle

# For the authentication purpose
from django.contrib.auth import login, authenticate, logout


# Using the Selection Sort in Order to place the correct element in correct position. (In Decreasing Order)
# Helper Function. (Function i.e used to return the querySet in the Descending Order).
def costliest_items(item_list):
    
    item_list = list(item_list)
    
    i = 0
    while (i < len(item_list) - 1):
        
        current_largest = i
        for j in range(i+1, len(item_list)):
            
            if (item_list[current_largest].prize < item_list[j].prize):
                current_largest = j
        
        item_list[i], item_list[current_largest] = item_list[current_largest], item_list[i]
        
        i += 1

    return item_list


# Create your views here.
def home_page(request):

    all_pizzas = Items.objects.filter(category = 'Pizza')
    all_burgers = Items.objects.filter(category = 'Burger')
    all_drinks = Items.objects.filter(category = 'Drink')
    all_pasta = Items.objects.filter(category = 'Pasta')

    # Just to display the most costliest pizza of the store. 
    # Because only 3 items of the other food items is present so that are not filtered.
    costliest_pizza = costliest_items(all_pizzas)[:3]

    # Costliest Items from all the categories of Items available on the store.
    hot_items = [costliest_items(all_pizzas)[0], costliest_items(all_burgers)[0], costliest_items(all_drinks)[0], costliest_items(all_pasta)[0]]

    context = { 'pizzas': all_pizzas[:9], 
                'length': len(all_pizzas),
                'pizza_set_1': all_pizzas[:5],
                'pizza_set_2': all_pizzas[5:],
                'costliest_pizza': costliest_pizza,
                'burgers': all_burgers,
                'drinks': all_drinks,
                'pastas': all_pasta,
                'hot_items': hot_items,
            }

    return render(request, "index.html", context = context)


def about(request):
    return render(request, "about.html")


def contact(request):

    if (request.method == "POST"):
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            new_message = ContactMessages(name = name, email = email, subject = subject, message = message)
            new_message.save()
            messages.success(request, "The Message Has Been Successfully Sent to The Customer Service, Please Check you're email regularly, our team will reach out to you soon.")
            
        else:
            messages.warning(request, "Data Missing 😞 Please Check whether all the fields are filled properly.")

    return render(request, "contact.html")


# After the User adds a New Item into the Cart, the user will be sent to the particular section of the website from where he was adding elements into the cart.
# "retrace_location" contains id of the section of the webpage, where the user will be redirected after the item is added to the cart.
def add_to_cart(request, pk, retrace_location):
    if (request.user.is_anonymous):
        return redirect('/')
    
    item = Items.objects.get(id = pk)
    user = request.user

    # creating a cart-object, hence adding the object in the particular user's cart.
    cart_object = CartItem(user = user, item = item)
    cart_object.save()
    messages.success(request, f"You're {item.category} | {item.food_name} has been added to the Cart Successfully ✅️.")

    return redirect(f'/#{retrace_location}')


def login_user(request):

    if (request.method == 'POST'):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        
        else:
            messages.warning(request, "User Credentials didn't match, Please Enter Correct Credentials !!")

    return render(request, "login.html")


def logout_user(request):
    logout(request)
    return redirect('/login/')



def calculate_total_cart_price(cart_items):
    price = 0

    for item in cart_items:
        price += item.item.prize

    return price


# We'll assume that there are 2 types of delivaery available.
# 1, Standard Delivery : costing ₹10
# 2, Express Delivery : costing ₹50

def user_cart(request):
    if (request.user.is_authenticated):
            
        cart_items = CartItem.objects.filter(user = request.user)
        total_prize = calculate_total_cart_price(cart_items)

        context = {
            'cart_items': cart_items,
            'no_of_items': len(cart_items),
            'prize': total_prize,
            'updated_prize' : total_prize + 100
        }

        # POST request will be made by the user when the user wants to Checkout with the desired items and options in his cart.
        if (request.method == "POST"):
            
            # If the cart for a user is Empty, then he will be redirected to the menu section to order some new items.
            if (len(cart_items) == 0):
                messages.warning(request, "Please Add Some Food Products in you're cart in order to checkOut.")
                return redirect('/#order-now')

            
            delivery_mode = request.POST.get('delivery-category')
            coupon_code = request.POST.get('coupon-code')

            # This are the methods set for delivery charges.
            if "Rs.100.00" in delivery_mode:
                delivery_mode = "Standard-Delivery"
                delivery_amount = 100
            else:
                delivery_mode = "Express-Delivery"
                delivery_amount = 250

            # Currently Coupon Code is not configuered.

            new_order = OrderObject(
                                        user = request.user,
                                        item_count = len(cart_items),
                                        all_items_ordered = pickle.dumps(cart_items),
                                        delivery_category = delivery_mode,
                                        delivery_charge = delivery_amount,
                                        total_price = total_prize + delivery_amount,
                                    )
            
            new_order.save()
            
            # Once the Order Has Been Created the Cart for the user should be empty.
            for item in cart_items:
                item.delete()

            return redirect('/make_payment/')
        
        return render(request, "cart.html", context=context)

    return redirect('/login/')


def delete_from_cart(request, pk):

    if (request.user.is_authenticated):
        cart_item = CartItem.objects.get(user = request.user, item__id = pk)
        messages.success(request, f"The Item {cart_item.item.food_name} has been deleted from the Cart ✅️.")
        cart_item.delete()
        
        return redirect('/cart')
    
    return redirect('/')


# This views are handeling the payment requests that are sent to the Backend Server.

def make_payment(request):
    order_item = OrderObject.objects.get(user = request.user, is_paid = False)
    
    context = {
                    'all_items_ordered' : pickle.loads(order_item.all_items_ordered),
                    'item_price': order_item.total_price - order_item.delivery_charge,
                    'total_price': order_item.total_price,
                    'delivery_charge': order_item.delivery_charge,
                    'delivery_mode': order_item.delivery_category,
                    'item_count': order_item.item_count,
    }

    return render(request, "make_payment.html", context=context)


def confirm_payment(request):
    
    allowed_cards = {
                        'card_1': {
                                        'card_num': '9023 6729 9032 6741',
                                        'card_name': 'JAYASHREE MAJI',
                                        'card_cvv': '801',
                                        'card_date': '01/32'
                        },

                        'card_2': {
                                        'card_num': '6732 1829 8934 7281',
                                        'card_name': 'ANKIT DEY',
                                        'card_cvv': '901',
                                        'card_date': '12/28'
                        },

                        'card_3': {
                                        'card_num': '1111 9999 1111 0000',
                                        'card_name': 'PARNA DEY',
                                        'card_cvv': '101',
                                        'card_date': '11/25'
                        }
    }

    saved_cards = saved_card.objects.all()
    order_item = OrderObject.objects.get(user = request.user, is_paid = False)

    context = {
        'card_num_1': saved_cards[1].card_number,
        'card_date_1': saved_cards[1].card_date,
        'card_name_1': saved_cards[1].user_name,
        'card_prov_1': saved_cards[1].card_provider,

        'card_num_2': saved_cards[0].card_number,
        'card_date_2': saved_cards[0].card_date,
        'card_name_2': saved_cards[0].user_name,
        'card_prov_2': saved_cards[0].card_provider,

        'item_price': order_item.total_price,
        'delivery_price': order_item.delivery_charge,
        'total_price': order_item.total_price
    }

    if (request.method == "POST"):
        card_number = request.POST.get('credit-number')
        card_date = request.POST.get('credit-date')
        cvv = request.POST.get('credit-cvv')
        card_name = request.POST.get('credit-name')

        
        for card in allowed_cards:
            current_card = allowed_cards[card]
            
            if (current_card['card_num'] == card_number and current_card['card_name'] == card_name and  current_card['card_date'] == card_date and current_card['card_cvv'] == cvv):
                
                # If all the details of the current card match with the allowed card. Then payment will be successfull.
                order_item.is_paid = True
                order_item.save()
                return redirect(f'/payment_successful/{order_item.id}/')
                
        else:
            messages.warning(request, "The Card You Have Entered is a InValid Card. 💳")


    return render(request, "confirm_payment.html", context=context)


def payment_successful(request, order_id):

    total_price = OrderObject.objects.get(id = order_id).total_price
    return render(request, "payment_successful.html", context={'total_price': total_price})