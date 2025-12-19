# Sistema de Detecção de EPIs

Sistema de detecção em tempo real de Equipamentos de Proteção Individual (EPIs) utilizando YOLOv8 e processamento de vídeo.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![React](https://img.shields.io/badge/React-18.2+-blue.svg)
![YOLO](https://img.shields.io/badge/YOLO-v8-orange.svg)

## 📋 Funcionalidades

- ✅ Detecção de EPIs em tempo real usando YOLOv8
- ✅ Suporte a múltiplas câmeras/streams de vídeo
- ✅ Interface web moderna e responsiva
- ✅ Configuração de FPS por câmera
- ✅ Alertas visuais para não conformidades
- ✅ Gerenciamento de câmeras (CRUD)

## 🏗️ Arquitetura

```
detec_epi/
├── backend/                 # API FastAPI
│   ├── main.py             # Ponto de entrada da API
│   ├── requirements.txt    # Dependências Python
│   ├── models/
│   │   └── detector.py     # Detector YOLOv8
│   ├── routers/
│   │   ├── cameras.py      # CRUD de câmeras
│   │   └── stream.py       # Streaming de vídeo
│   └── schemas/
│       └── camera.py       # Modelos Pydantic
│
└── frontend/               # React + Vite
    ├── src/
    │   ├── App.tsx
    │   ├── pages/
    │   │   ├── Dashboard.tsx    # Visualização
    │   │   └── AddCamera.tsx    # Cadastro
    │   ├── components/
    │   │   ├── Layout.tsx
    │   │   └── CameraCard.tsx
    │   └── services/
    │       └── api.ts          # Cliente HTTP
    └── package.json
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- Node.js 18+
- Webcam ou vídeos de teste

### Backend

```bash
# Navegar para o diretório do backend
cd backend

# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar o servidor
python main.py
```

O servidor será iniciado em `http://localhost:8000`

### Frontend

```bash
# Navegar para o diretório do frontend
cd frontend

# Instalar dependências
npm install

# Executar em modo de desenvolvimento
npm run dev
```

O frontend será iniciado em `http://localhost:5173`

## 📖 Uso

### Adicionar uma Câmera

1. Acesse a página "Adicionar Câmera"
2. Preencha os campos:
   - **Nome**: Identificação única da câmera
   - **URL**: Link do stream (RTSP, HTTP) ou caminho do vídeo
   - **FPS**: Taxa de detecção (1-30 frames por segundo)
3. Clique em "Adicionar Câmera"

### Fontes de Vídeo Suportadas

- **Webcam**: Use `0`, `1`, `2`, etc.
- **Arquivo local**: Caminho completo do arquivo (ex: `C:\videos\teste.mp4`)
- **Stream RTSP**: `rtsp://usuario:senha@ip:porta/stream`
- **Stream HTTP**: `http://ip:porta/video`

### Exemplo de Uso com Webcam

1. Adicione uma câmera com URL `0` (webcam padrão)
2. Defina o nome como "Webcam Principal"
3. Ajuste o FPS conforme desejado (5-10 recomendado)
4. Acesse a página de Monitoramento para ver as detecções

## 🔧 Configuração

### EPIs Detectados

O sistema está configurado para detectar:
- 👷 Capacetes de segurança
- 🦺 Coletes refletivos
- 🧤 Luvas de proteção
- 👓 Óculos de segurança
- 👢 Botas de segurança

### Modelo YOLO

Por padrão, o sistema usa o modelo `yolov8n.pt` (nano), que é mais rápido. Para maior precisão, você pode usar:

- `yolov8s.pt` - Small
- `yolov8m.pt` - Medium
- `yolov8l.pt` - Large
- `yolov8x.pt` - Extra Large

Para alterar, edite o arquivo `backend/models/detector.py`:

```python
def __init__(self, model_path: str = "yolov8m.pt"):
```

### Modelo Customizado para EPIs

Para usar um modelo treinado especificamente para EPIs:

1. Treine seu modelo YOLOv8 com dataset de EPIs
2. Coloque o arquivo `.pt` no diretório `backend/`
3. Atualize o caminho no detector:

```python
def __init__(self, model_path: str = "epi_model.pt"):
```

## 📡 API Endpoints

### Câmeras

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/cameras/` | Lista todas as câmeras |
| POST | `/api/cameras/` | Cria uma nova câmera |
| GET | `/api/cameras/{id}` | Obtém uma câmera |
| PUT | `/api/cameras/{id}` | Atualiza uma câmera |
| DELETE | `/api/cameras/{id}` | Remove uma câmera |

### Streaming

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/stream/{id}` | Stream de vídeo com detecções |
| POST | `/api/stream/{id}/stop` | Para o stream |
| GET | `/api/stream/{id}/status` | Status do stream |

## 🔒 Segurança

⚠️ **Este projeto é um protótipo para demonstração.**

Para uso em produção, considere:
- Implementar autenticação (JWT, OAuth)
- Usar HTTPS
- Configurar CORS apropriadamente
- Armazenar dados em banco de dados persistente
- Implementar rate limiting

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.

