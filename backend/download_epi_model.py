"""
Script para baixar modelo de detecção de EPIs.

Modelos disponíveis:
1. PPE Detection (Hardhat, Vest, etc.) - Roboflow
2. Safety Equipment Detection

Execute: python download_epi_model.py
"""

import urllib.request
import os
import sys

# URLs de modelos de EPI públicos
# Nota: Estes são exemplos. Para uso em produção, treine seu próprio modelo.
MODELS = {
    "ppe_yolov8": {
        "url": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt",
        "description": "Modelo YOLOv8 nano (base para fine-tuning)",
        "note": "Este é o modelo base. Para EPIs reais, você precisa treinar com um dataset de EPIs."
    }
}


def download_file(url: str, destination: str):
    """Baixa arquivo da URL."""
    print(f"Baixando de: {url}")
    print(f"Salvando em: {destination}")
    
    def progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\rProgresso: {percent}%")
        sys.stdout.flush()
    
    try:
        urllib.request.urlretrieve(url, destination, progress_hook)
        print("\n✅ Download concluído!")
        return True
    except Exception as e:
        print(f"\n❌ Erro no download: {e}")
        return False


def main():
    print("=" * 60)
    print("  DOWNLOAD DE MODELO DE DETECÇÃO DE EPIs")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANTE:")
    print("   O modelo YOLOv8 padrão NÃO detecta EPIs!")
    print("   Para detectar capacetes, coletes, etc., você precisa de")
    print("   um modelo treinado especificamente para EPIs.")
    print()
    print("📋 OPÇÕES PARA OBTER UM MODELO DE EPI:")
    print()
    print("1. ROBOFLOW (Recomendado - Modelos prontos):")
    print("   - Acesse: https://universe.roboflow.com/")
    print("   - Pesquise por 'PPE detection' ou 'safety equipment'")
    print("   - Baixe o modelo no formato YOLOv8")
    print("   - Renomeie para 'epi_model.pt' e coloque na pasta 'backend/'")
    print()
    print("2. TREINAR SEU PRÓPRIO MODELO:")
    print("   - Colete imagens de trabalhadores com EPIs")
    print("   - Anote as imagens (capacete, colete, luvas, etc.)")
    print("   - Treine com YOLOv8:")
    print("     yolo train data=seu_dataset.yaml model=yolov8n.pt epochs=100")
    print()
    print("3. DATASETS PÚBLICOS DE EPI:")
    print("   - https://universe.roboflow.com/roboflow-universe-projects/construction-site-safety")
    print("   - https://universe.roboflow.com/objet-detect-yolov5/ppe-detection-yolov5")
    print()
    print("=" * 60)
    
    # Criar arquivo de instrução
    instructions = """
# Como adicionar modelo de detecção de EPIs

## Passo 1: Obter o modelo

### Opção A: Roboflow (mais fácil)
1. Acesse https://universe.roboflow.com/
2. Pesquise por "PPE detection" ou "hardhat detection"
3. Escolha um modelo com boas avaliações
4. Clique em "Download" e selecione formato "YOLOv8"
5. Baixe o arquivo .pt

### Opção B: Treinar seu próprio modelo
```bash
# Instale o ultralytics
pip install ultralytics

# Baixe um dataset de EPI do Roboflow
# Treine o modelo
yolo train data=path/to/data.yaml model=yolov8n.pt epochs=100 imgsz=640
```

## Passo 2: Instalar o modelo

1. Renomeie o arquivo baixado para `epi_model.pt`
2. Coloque na pasta `backend/`
3. Reinicie o servidor

## Classes típicas em modelos de EPI:
- Hardhat / helmet (Capacete)
- NO-Hardhat / head (Sem capacete)
- Safety Vest / vest (Colete)
- NO-Safety Vest (Sem colete)
- Mask (Máscara)
- Gloves (Luvas)
- Goggles (Óculos)
- Boots (Botas)
- Person / worker (Pessoa/Trabalhador)

## Links úteis:
- Roboflow Universe: https://universe.roboflow.com/
- Ultralytics YOLOv8: https://docs.ultralytics.com/
- Dataset de construção: https://universe.roboflow.com/roboflow-universe-projects/construction-site-safety
"""
    
    with open("COMO_ADICIONAR_MODELO_EPI.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📄 Arquivo de instruções criado: COMO_ADICIONAR_MODELO_EPI.md")
    print()
    
    # Perguntar se quer baixar modelo base
    print("Deseja baixar o modelo YOLOv8 base? (será necessário treinar para EPIs)")
    response = input("Digite 's' para sim ou 'n' para não: ").strip().lower()
    
    if response == 's':
        model_path = os.path.join(os.path.dirname(__file__), "yolov8n.pt")
        if download_file(MODELS["ppe_yolov8"]["url"], model_path):
            print()
            print("✅ Modelo base baixado!")
            print("⚠️  Lembre-se: Este modelo NÃO detecta EPIs.")
            print("   Você precisa treiná-lo com um dataset de EPIs.")
    else:
        print("Ok! Siga as instruções acima para obter um modelo de EPI.")


if __name__ == "__main__":
    main()

