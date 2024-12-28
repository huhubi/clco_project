from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# Roulette setup
even_numbers = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
odd_numbers = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/play', methods=['POST'])
def play():
    bet_type = request.form.get('bet_type')
    bet_amount = int(request.form.get('bet_amount'))

    # Simulate roulette spin
    winning_number = random.randint(0, 36)

    if bet_type == 'even':
        if winning_number in even_numbers:
            result = f"Winner is {winning_number} (Even)! You win {bet_amount * 2}!"
        else:
            result = f"Winner is {winning_number} (Odd). You lose your bet of {bet_amount}."
    elif bet_type == 'odd':
        if winning_number in odd_numbers:
            result = f"Winner is {winning_number} (Odd)! You win {bet_amount * 2}!"
        else:
            result = f"Winner is {winning_number} (Even). You lose your bet of {bet_amount}."
    else:
        result = "Invalid bet type!"

    return render_template('result.html', result=result, winning_number=winning_number)


if __name__ == '__main__':
    app.run(debug=True)
