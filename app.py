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
    return jsonify({"status": "online", "app": "Supremo TV API", "versao": "2.0"})

# ============================================
# ROTA DE FILMES (COM MAIS FILMES E CAPAS FILTRADAS)
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
            
            # PEGA 30 FILMES DE CADA SITE
            cards = soup.select(site['seletor'])[:30]
            
            for card in cards:
                try:
                    # TÍTULO
                    titulo_elem = card.select_one(site['titulo_sel'])
                    titulo = titulo_elem.text.strip() if titulo_elem else "Sem título"
                    
                    # IMAGEM (FILTRANDO PLACEHOLDERS)
                    img_elem = card.select_one(site['imagem_sel'])
                    imagem = ""
                    if img_elem:
                        imagem = img_elem.get('src') or img_elem.get('data-src') or ""
                    
                    # IGNORA IMAGENS INVÁLIDAS (base64, gif, svg)
                    if imagem and (imagem.startswith('data:image') or 'base64' in imagem or 'gif' in imagem):
                        imagem = ""
                    elif imagem and imagem.startswith('//'):
                        imagem = 'https:' + imagem
                    
                    # LINK
                    link_elem = card.select_one('a')
                    link = link_elem.get('href') if link_elem else ""
                    
                    if titulo and titulo != "Sem título" and imagem:
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
    
    return jsonify(filmes_unicos[:100])  # Retorna até 100 filmes

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
            
            cards = soup.select(site['seletor'])[:20]
            
            for card in cards:
                try:
                    titulo_elem = card.select_one(site['titulo_sel'])
                    titulo = titulo_elem.text.strip() if titulo_elem else "Sem título"
                    
                    img_elem = card.select_one('img')
                    imagem = img_elem.get('src') if img_elem else ""
                    if imagem and imagem.startswith('//'):
                        imagem = 'https:' + imagem
                    
                    series_lista.append({
                        'titulo': titulo,
                        'imagem': imagem,
                        'fonte': site['nome']
                    })
                except:
                    continue
        except:
            continue
    
    return jsonify(series_lista[:50])

# ============================================
# ROTA PARA BUSCAR VÍDEO REAL (MELHORADA)
# ============================================
@app.route('/buscar_video', methods=['POST'])
def buscar_video():
    dados = request.json
    titulo = dados.get('titulo')
    
    print(f"Buscando vídeo para: {titulo}")
    
    # Lista de sites para buscar vídeos
    sites_video = [
        {
            'nome': 'Pobreflix',
            'url_busca': f'https://verfilmeshdgratis.net/?s={titulo.replace(" ", "+")}',
            'seletor_resultado': '.poster a, .movie-card a',
            'seletor_video': 'iframe[src*="player"], video source'
        },
        {
            'nome': 'AdoroCinema',
            'url_busca': f'https://www.adorocinema.com/filmes/busca/?q={titulo.replace(" ", "+")}',
            'seletor_resultado': '.meta-title a',
            'seletor_video': '.player iframe, video source'
        },
        {
            'nome': 'BoraFilmes',
            'url_busca': f'https://www.borafilmes.com/?s={titulo.replace(" ", "+")}',
            'seletor_resultado': '.movie-item a',
            'seletor_video': 'iframe[src*="player"]'
        }
    ]
    
    for site in sites_video:
        try:
            print(f"Tentando site: {site['nome']}")
            
            # 1. Buscar resultado
            r1 = requests.get(site['url_busca'], headers=HEADERS, timeout=10)
            soup1 = BeautifulSoup(r1.text, 'html.parser')
            
            resultado = soup1.select_one(site['seletor_resultado'])
            if not resultado:
                continue
                
            link_filme = resultado.get('href')
            if link_filme.startswith('/'):
                link_filme = 'https://verfilmeshdgratis.net' + link_filme
            
            # 2. Acessar página do filme
            r2 = requests.get(link_filme, headers=HEADERS, timeout=15)
            soup2 = BeautifulSoup(r2.text, 'html.parser')
            
            # 3. Procurar player
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
            
            # 4. Procurar padrões de URL
            padroes = [
                r'https?://[^\s"\']+\.(mp4|m3u8)',
                r'https?://[^\s"\']+player[^\s"\']+',
                r'https?://[^\s"\']+embed[^\s"\']+'
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
    
    # Se não encontrar em nenhum site, retorna vídeo de exemplo
    return jsonify({
        "sucesso": True,
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "titulo": titulo,
        "fonte": "exemplo"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
