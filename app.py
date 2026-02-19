from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time

app = Flask(__name__)
CORS(app)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# ============================================
# ROTA PRINCIPAL
# ============================================
@app.route('/')
def home():
    return jsonify({
        "status": "online", 
        "app": "Supremo TV - Pobreflix",
        "versao": "2.0",
        "filmes_por_pagina": 100
    })

# ============================================
# ROTA DE FILMES - POBREFLIX (100 FILMES)
# ============================================
@app.route('/filmes')
def filmes():
    filmes_lista = []
    
    try:
        # Tenta acessar a página inicial
        url = "https://verfilmeshdgratis.net/inicio/"
        
        print("Acessando Pobreflix...")
        response = requests.get(url, headers=HEADERS, timeout=30)  # Timeout maior
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Vários seletores para garantir que pega os filmes
        seletores = ['.poster', '.movie-card', '.item', 'article', '.filme-item', '.card']
        
        itens = []
        for seletor in seletores:
            itens = soup.select(seletor)
            if itens:
                print(f"Encontrados {len(itens)} itens com seletor: {seletor}")
                break
        
        # PEGA 100 FILMES (ou todos se tiver menos)
        quantidade = min(len(itens), 100)
        print(f"Processando {quantidade} filmes...")
        
        for i, item in enumerate(itens[:100]):
            try:
                # Título
                titulo = "Sem título"
                titulo_elem = (item.select_one('h2') or 
                              item.select_one('h3') or 
                              item.select_one('.title') or 
                              item.select_one('a') or
                              item.select_one('strong'))
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                
                # Imagem
                imagem = ""
                img_elem = item.select_one('img')
                if img_elem:
                    imagem = img_elem.get('src') or img_elem.get('data-src') or ""
                    if imagem and imagem.startswith('//'):
                        imagem = 'https:' + imagem
                
                # Link
                link = ""
                link_elem = item.select_one('a')
                if link_elem:
                    link = link_elem.get('href') or ""
                
                # Só adiciona se tiver título válido
                if titulo and titulo != "Sem título" and len(titulo) > 2:
                    filmes_lista.append({
                        'id': i,
                        'titulo': titulo[:100],
                        'imagem': imagem,
                        'link': link,
                        'fonte': 'Pobreflix'
                    })
                    
                # Pequena pausa para não sobrecarregar
                if i % 20 == 0:
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"Erro ao processar item {i}: {e}")
                continue
                
        print(f"Total de filmes encontrados: {len(filmes_lista)}")
        
    except Exception as e:
        print(f"Erro ao acessar Pobreflix: {e}")
        return jsonify({
            "erro": str(e),
            "mensagem": "Erro ao buscar filmes"
        }), 500
    
    return jsonify(filmes_lista)

# ============================================
# ROTA PARA BUSCAR VÍDEO (MELHORADA)
# ============================================
@app.route('/buscar_video', methods=['POST'])
def buscar_video():
    dados = request.json
    titulo = dados.get('titulo')
    
    print(f"Buscando vídeo para: {titulo}")
    
    # Lista de variações do título para busca
    titulo_busca = titulo.lower()
    titulo_busca = re.sub(r'[^\w\s]', '', titulo_busca)  # Remove pontuação
    
    try:
        # Buscar no Pobreflix
        url_busca = f"https://verfilmeshdgratis.net/?s={titulo_busca.replace(' ', '+')}"
        print(f"URL de busca: {url_busca}")
        
        r1 = requests.get(url_busca, headers=HEADERS, timeout=15)
        soup1 = BeautifulSoup(r1.text, 'html.parser')
        
        # Múltiplos seletores para encontrar resultado
        resultado = (soup1.select_one('.poster a') or 
                    soup1.select_one('.movie-card a') or 
                    soup1.select_one('article a') or
                    soup1.select_one('h2 a') or
                    soup1.select_one('h3 a') or
                    soup1.select_one('.title a'))
        
        if resultado:
            link_filme = resultado.get('href')
            print(f"Link do filme: {link_filme}")
            
            # Acessar página do filme
            r2 = requests.get(link_filme, headers=HEADERS, timeout=15)
            soup2 = BeautifulSoup(r2.text, 'html.parser')
            
            # Múltiplos seletores para encontrar player
            player = (soup2.select_one('iframe[src*="player"]') or
                     soup2.select_one('iframe[src*="video"]') or
                     soup2.select_one('iframe[src*="embed"]') or
                     soup2.select_one('video source') or
                     soup2.select_one('iframe'))
            
            if player:
                video_url = player.get('src')
                if video_url:
                    print(f"Vídeo encontrado: {video_url}")
                    return jsonify({
                        "sucesso": True,
                        "video_url": video_url,
                        "titulo": titulo,
                        "fonte": "Pobreflix"
                    })
            
            # Procurar padrões de URL no texto da página
            padroes = [
                r'https?://[^\s"\']+\.(mp4|m3u8)',
                r'https?://[^\s"\']+player[^\s"\']+',
                r'https?://[^\s"\']+embed[^\s"\']+',
                r'https?://[^\s"\']+video[^\s"\']+',
                r'https?://[^\s"\']+watch[^\s"\']+'
            ]
            
            for padrao in padroes:
                matches = re.findall(padrao, r2.text)
                if matches:
                    print(f"Vídeo encontrado por padrão: {matches[0]}")
                    return jsonify({
                        "sucesso": True,
                        "video_url": matches[0],
                        "titulo": titulo,
                        "fonte": "Pobreflix"
                    })
                    
    except Exception as e:
        print(f"Erro na busca: {e}")
    
    # Vídeo de exemplo se não encontrar
    print("Usando vídeo de exemplo")
    return jsonify({
        "sucesso": True,
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "titulo": titulo,
        "fonte": "exemplo"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
