import os
import json
import datetime
import random
from typing import List, Dict

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'global_warming.json')

app = Flask(__name__, static_folder=None)


def load_question_pool() -> List[Dict]:
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('questions', [])


def shuffle_question(q: Dict, rng: random.Random) -> Dict:
    # Shuffle options but preserve correct answer mapping
    opts = list(enumerate(q['options']))
    rng.shuffle(opts)
    new_options = [text for (_idx, text) in opts]
    # Find new index of the original correct answer
    correct_old_idx = q['answer']
    for new_idx, (old_idx, _text) in enumerate(opts):
        if old_idx == correct_old_idx:
            correct_new_idx = new_idx
            break
    return {
        'q': q['q'],
        'options': new_options,
        'answer': correct_new_idx,
        'explanation': q.get('explanation', '')
    }


@app.get('/api/quiz/global-warming')
def api_quiz_global_warming():
    pool = load_question_pool()
    # Params: count, seed
    count_param = request.args.get('count', type=int)
    count = max(1, min(len(pool), count_param if count_param else len(pool)))

    seed = request.args.get('seed')
    if not seed:
        # Use random seed if none provided
        seed = str(random.random())
    rng = random.Random(str(seed))

    # Shuffle pool, take count, then shuffle options per question
    pool_copy = pool[:]
    rng.shuffle(pool_copy)
    selected = pool_copy[:count]
    result = [shuffle_question(q, rng) for q in selected]
    return jsonify({
        'seed': seed,
        'count': count,
        'questions': result
    })


# Static file routes (serve app under same origin)
@app.get('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.get('/global-warming-quiz.html')
def serve_quiz():
    return send_from_directory(BASE_DIR, 'global-warming-quiz.html')


@app.get('/quiz.css')
def serve_css():
    return send_from_directory(BASE_DIR, 'quiz.css')


@app.get('/background.jpg')
def serve_bg():
    # Optional background image
    return send_from_directory(BASE_DIR, 'background.jpg')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    app.run(host='0.0.0.0', port=port, debug=False)

