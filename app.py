from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time

app = Flask(__name__)
CORS(app)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# ============================================
# ROTA PRINCIPAL
# ============================================
@app.route('/')
def home():
    return jsonify({"status": "online", "app": "Supremo TV API com múltiplos sites"})

# ============================================
# ROTA DE FILMES (tenta vários sites)
# ============================================
@app.route('/filmes')
def filmes():
    todos_filmes = []
    
    # LISTA DE SITES PARA BUSCAR FILMES
    sites_filmes = [
        {
            'nome': 'Pobreflix',
            'url': 'https://verfilmeshdgratis.net/inicio/',
            'seletor': '.poster, .movie-card, .item',
            'titulo_sel': 'h2, h3, .title',
            'imagem_sel': 'img'
        },
        {
            'nome': 'Filmow',
            'url': 'https://filmow.com/filmes/',
            'seletor': '.movie-card, .card',
            'titulo_sel': '.title, h3',
            'imagem_sel': 'img'
        },
        {
            'nome': 'JustWatch',
            'url': 'https://www.justwatch.com/br/filmes',
            'seletor': '.title-card, .card',
            'titulo_sel': '.title, h3',
            'imagem_sel': 'img'
        },
        {
            'nome': 'Filmelier',
            'url': 'https://www.filmelier.com/br/assistir-filmes-online',
            'seletor': '.movie-card, .card',
            'titulo_sel': 'h3, .title',
            'imagem_sel': 'img'
        },
        {
            'nome': 'AdoroCinema VOD',
            'url': 'https://www.adorocinema.com/vod/',
            'seletor': '.card, .entity-card',
            'titulo_sel': '.meta-title a, h3',
            'imagem_sel': 'img'
        },
        {
            'nome': 'FilmesOnlineHD',
            'url': 'https://filmesonlinehd.gratis/',
            'seletor': '.poster, .movie-item',
            'titulo_sel': 'h3, .title',
            'imagem_sel': 'img'
        },
        {
            'nome': 'BoraFilmes',
            'url': 'https://www.borafilmes.com/',
            'seletor': '.movie-card, .item',
            'titulo_sel': 'h3, .title',
            'imagem_sel': 'img'
        },
        {
            'nome': 'FlixFilmesOnline',
            'url': 'https://flixfilmesonline.com/',
            'seletor': '.poster, .movie',
            'titulo_sel': 'h3, .title',
            'imagem_sel': 'img'
        },
        {
            'nome': 'CinemaESeries',
            'url': 'https://cinemaeseries.com.br/assistir-filmes-online-gratis/?amp=1',
            'seletor': '.post, .movie-item',
            'titulo_sel': 'h2, h3',
            'imagem_sel': 'img'
        },
        {
            'nome': 'Libreflix',
            'url': 'https://libreflix.org/',
            'seletor': '.card, .movie',
            'titulo_sel': 'h3, .title',
            'imagem_sel': 'img'
        }
    ]
    
    for site in sites_filmes:
        try:
            print(f"Buscando filmes em: {site['nome']}")
            response = requests.get(site['url'], headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Encontra os cards de filmes
            cards = soup.select(site['seletor'])[:10]  # Pega só 10 de cada site
            
            for card in cards:
                try:
                    # Tenta encontrar título
                    titulo_elem = card.select_one(site['titulo_sel'])
                    titulo = titulo_elem.text.strip() if titulo_elem else "Sem título"
                    
                    # Tenta encontrar imagem
                    img_elem = card.select_one(site['imagem_sel'])
                    imagem = img_elem.get('src') if img_elem else ""
                    if imagem and imagem.startswith('//'):
                        imagem = 'https:' + imagem
                    
                    # Tenta encontrar link
                    link_elem = card.select_one('a')
                    link = link_elem.get('href') if link_elem else ""
                    
                    if titulo and titulo != "Sem título":
                        todos_filmes.append({
                            'titulo': titulo[:100],
                            'imagem': imagem,
                            'link': link,
                            'fonte': site['nome']
                        })
                except:
                    continue
                    
        except Exception as e:
            print(f"Erro no site {site['nome']}: {e}")
            continue
    
    # Remove duplicatas (mesmo título)
    seen = set()
    filmes_unicos = []
    for filme in todos_filmes:
        if filme['titulo'] not in seen:
            seen.add(filme['titulo'])
            filmes_unicos.append(filme)
    
    return jsonify(filmes_unicos[:50])  # Retorna no máximo 50 filmes

# ============================================
# ROTA DE SÉRIES
# ============================================
@app.route('/series')
def series():
    series_lista = []
    
    sites_series = [
        {
            'nome': 'Pobreflix Series',
            'url': 'https://verfilmeshdgratis.net/series/',
            'seletor': '.poster, .series-card',
            'titulo_sel': 'h3, .title'
        },
        {
            'nome': 'Filmow Series',
            'url': 'https://filmow.com/series/',
            'seletor': '.movie-card',
            'titulo_sel': '.title'
        }
    ]
    
    for site in sites_series:
        try:
            response = requests.get(site['url'], headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            cards = soup.select(site['seletor'])[:10]
            
            for card in cards:
                try:
                    titulo_elem = card.select_one(site['titulo_sel'])
                    titulo = titulo_elem.text.strip() if titulo_elem else "Sem título"
                    
                    img_elem = card.select_one('img')
                    imagem = img_elem.get('src') if img_elem else ""
                    
                    series_lista.append({
                        'titulo': titulo,
                        'imagem': imagem,
                        'fonte': site['nome']
                    })
                except:
                    continue
        except:
            continue
    
    return jsonify(series_lista[:30])

# ============================================
# ROTA PARA BUSCAR VÍDEO REAL
# ============================================
@app.route('/buscar_video', methods=['POST'])
def buscar_video():
    dados = request.json
    titulo = dados.get('titulo')
    
    print(f"Buscando vídeo para: {titulo}")
    
    # Sites para buscar o vídeo
    sites_video = [
        {
            'nome': 'Pobreflix',
            'url_busca': f'https://verfilmeshdgratis.net/?s={titulo.replace(" ", "+")}',
            'seletor_resultado': '.poster a, .movie-card a',
            'seletor_video': 'iframe[src*="player"], video source'
        },
        {
            'nome': 'BoraFilmes',
            'url_busca': f'https://www.borafilmes.com/?s={titulo.replace(" ", "+")}',
            'seletor_resultado': '.movie-item a',
            'seletor_video': 'iframe[src*="player"]'
        },
        {
            'nome': 'FlixFilmesOnline',
            'url_busca': f'https://flixfilmesonline.com/?s={titulo.replace(" ", "+")}',
            'seletor_resultado': '.post a',
            'seletor_video': 'iframe'
        }
    ]
    
    for site in sites_video:
        try:
            print(f"Tentando site: {site['nome']}")
            
            # Buscar resultado
            r1 = requests.get(site['url_busca'], headers=HEADERS, timeout=10)
            soup1 = BeautifulSoup(r1.text, 'html.parser')
            
            # Pegar primeiro resultado
            resultado = soup1.select_one(site['seletor_resultado'])
            if resultado:
                link_filme = resultado.get('href')
                
                # Acessar página do filme
                r2 = requests.get(link_filme, headers=HEADERS, timeout=10)
                soup2 = BeautifulSoup(r2.text, 'html.parser')
                
                # Procurar player
                player = soup2.select_one(site['seletor_video'])
                if player:
                    video_url = player.get('src')
                    if video_url:
                        return jsonify({
                            "sucesso": True,
                            "video_url": video_url,
                            "titulo": titulo,
                            "fonte": site['nome']
                        })
                
                # Procurar padrões de URL
                padroes = [
                    r'https?://[^\s"\']+\.(mp4|m3u8)',
                    r'https?://[^\s"\']+player[^\s"\']+'
                ]
                for padrao in padroes:
                    matches = re.findall(padrao, r2.text)
                    if matches:
                        return jsonify({
                            "sucesso": True,
                            "video_url": matches[0],
                            "titulo": titulo,
                            "fonte": site['nome']
                        })
                        
        except Exception as e:
            print(f"Erro no site {site['nome']}: {e}")
            continue
    
    # Se não encontrar em nenhum site
    return jsonify({
        "sucesso": False,
        "erro": "Vídeo não encontrado",
        "titulo": titulo
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
