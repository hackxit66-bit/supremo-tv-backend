from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"status": "online", "app": "Supremo TV"})

@app.route('/filmes')
def filmes():
    filmes = []
    try:
        url = "https://www.adorocinema.com/filmes/todos-filmes/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for card in soup.select('.card')[:5]:
            titulo = card.select_one('.meta-title a').text.strip()
            imagem = card.select_one('img')['src']
            filmes.append({'titulo': titulo, 'imagem': imagem})
    except:
        pass
    return jsonify(filmes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
