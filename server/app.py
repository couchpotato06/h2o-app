from flask import Flask, request, jsonify, render_template
import redis
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS with additional options
CORS(app)

# Configure Redis
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=os.getenv('REDIS_PORT', 6379),
    decode_responses=True,
    username=os.getenv('REDIS_USER', None),
    password=os.getenv('REDIS_PASS', None)
)

WATER_GLASSES_REDIS_KEY = "glasses_of_water"

@app.route('/')
def index():
    try:
        glasses = redis_client.get(WATER_GLASSES_REDIS_KEY)
        return render_template('index.html', glasses=int(glasses) if glasses else 0)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@app.route('/update', methods=['GET', 'POST'])
def update_form():
    try:
        glasses = redis_client.get(WATER_GLASSES_REDIS_KEY)
        current_glasses = int(glasses) if glasses else 0
        
        if request.method == 'POST':
            new_glasses = request.form.get('glasses', type=int)
            if new_glasses is not None and 0 <= new_glasses <= 100:
                redis_client.set(WATER_GLASSES_REDIS_KEY, new_glasses)
                return render_template('update.html', glasses=new_glasses, message="Successfully updated!")
            else:
                return render_template('update.html', glasses=current_glasses, message="Please enter a number between 0 and 100")
        
        return render_template('update.html', glasses=current_glasses)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 8080))