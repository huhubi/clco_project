from flask import Flask, render_template, request
import random

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/play', methods=['POST'])
def play():
    bet_number = int(request.form.get('bet_number'))
    bet_amount = int(request.form.get('bet_amount'))

    # Simulate roulette spin
    winning_number = random.randint(0, 36)

    if bet_number == winning_number:
        result = f"Winner is {winning_number}! You win {bet_amount * 35}!"
    else:
        result = f"Winner is {winning_number}. You lose your bet of {bet_amount}."

    return render_template('result.html', result=result, winning_number=winning_number)


if __name__ == '__main__':
    app.run(debug=True)
