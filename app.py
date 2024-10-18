from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import json
import base64

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set your secret key for session management

@app.route('/')
def home():
    # Your dictionary data with multiple books
    OOP = [
        {
            "legal_basis": "DAO-110",
            "Description": "Lorem Ipsum",
            "Amount": 500,
        },
        {
            "legal_basis": "DAO-111",
            "Description": "Dolor Sit Amet",
            "Amount": 600,
        },
        {
            "legal_basis": "DAO-112",
            "Description": "Consectetur Adipiscing Elit",
            "Amount": 700,
        }
    ]
    return render_template('OOP.html', OOP=OOP)

@app.route("/pay", methods=["POST"])
def pay():
    PAYMONGO_API_KEY = " " #add your own paympongo key
    url = 'https://api.paymongo.com/v1/links'

    # Get the total amount from the form submission (assuming you send a total amount)
    total_amount = request.form.get('total_amount', type=int)
    print("Total Amount: ", total_amount)  # Debugging line

    if total_amount is None or total_amount <= 0:
        flash("Invalid total amount.")
        return redirect(url_for('home'))

    # Convert amount to centavos
    amount_in_centavos = total_amount * 100  # Convert to centavos

    payload = {
        "data": {
            "attributes": {
                "amount": amount_in_centavos,  # Amount in centavos
                "description": "Permittree Online Application",
                "remarks": "Thank you for your purchase!",
                "currency": "PHP",
                "redirect": {
                    "success": url_for('success', _external=True),
                    "failed": url_for('failed', _external=True)
                }
            }
        }
    }

    api_key_encoded = base64.b64encode(f"{PAYMONGO_API_KEY}:".encode("utf-8")).decode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {api_key_encoded}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f'Status Code: {response.status_code}')  # Debugging line
        response.raise_for_status()  # Raises an error for 4xx or 5xx responses

        response_data = response.json()
        print('Response Data:', response_data)  # Debugging line

        payment_url = response_data['data']['attributes']['checkout_url']
        print("Payment URL: ", payment_url)  # Debugging line

        return redirect(payment_url)

    except requests.exceptions.RequestException as e:
        flash(f'Error with payment: {e}')
        return redirect(url_for('home'))

    except KeyError:
        flash('Unexpected response structure from PayMongo')
        return redirect(url_for('home'))

@app.route('/success')
def success():
    flash("Payment successful!")
    return redirect(url_for('home'))  # Redirect to the home page

@app.route('/failed')
def failed():
    flash("Payment failed. Please try again.")
    return redirect(url_for('home'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        flash(f'Thank you for signing up for our deals, {email}!')
        return redirect(url_for("home"))  # Redirect to the home page
    else:
        flash('Invalid email address.')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
