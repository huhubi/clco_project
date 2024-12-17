from flask import Flask, render_template, request
import random

app = Flask(__name__)

# European Roulette red numbers:
# 18 red numbers: 1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bet_type = request.form.get('bet_type')
        bet_value = request.form.get('bet_value', '')

        # Spin the roulette wheel
        winning_number = random.randint(0, 36)
        winning_color = "red" if winning_number in RED_NUMBERS else ("green" if winning_number == 0 else "black")

        # Determine if the user won
        if bet_type == 'number':
            # User bets on a specific number
            try:
                user_number = int(bet_value)
                if user_number == winning_number:
                    result_message = f"Congratulations! You won by guessing the correct number {winning_number}."
                else:
                    result_message = f"Sorry, you lost. The winning number was {winning_number}, not {user_number}."
            except ValueError:
                result_message = "Invalid number input."

        else:
            # User bets on a color
            user_color = bet_value.lower()
            if user_color == winning_color:
                result_message = f"Congratulations! You won. The winning number {winning_number} is {winning_color}."
            else:
                result_message = f"Sorry, you lost. The winning number {winning_number} is {winning_color}, not {user_color}."

        return render_template('result.html',
                               winning_number=winning_number,
                               winning_color=winning_color,
                               result_message=result_message)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)