# 📚 Processador de Anotações Kindle

Ferramenta simples para processar e organizar anotações do Kindle.

## 🎯 O que faz?

- Lê o arquivo `My Clippings.txt` do seu Kindle
- Extrai todas as anotações
- Organiza cada livro em uma pasta separada
- Salva em arquivo de texto formatado

## 🚀 Como usar?

### 1. Setup inicial (primeira vez)

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar
source venv/bin/activate

# Instalar dependências (se houver)
pip install -r requirements.txt
```

### 2. Colocar seu arquivo

Copie seu `My Clippings.txt` para a pasta `input/`:

```bash
cp "My Clippings.txt" input/
```

### 3. Executar

```bash
python main.py
```

Escolha opção **1** no menu.

## 📁 Resultado

As anotações serão organizadas em `output/`:

```
output/
├── Livro 1/
│   └── anotacoes.txt
├── Livro 2/
│   └── anotacoes.txt
└── ... (mais livros)
```

## 📋 Estrutura

```
.
├── input/                    ← Coloque My Clippings.txt aqui
├── output/                   ← Anotações organizadas
├── main.py                   ← Menu principal
├── clippings_processor.py    ← Processa anotações
├── venv/                     ← Ambiente virtual
└── README.md
```

## ⚙️ Dependências

- Python 3.8+

## 💡 Dica

Seu `My Clippings.txt` fica em:
- **Kindle USB**: `/Kindle/documents/My Clippings.txt`
- **Kindle Cloud**: Na pasta de documentos sincronizados

---

**Simples, rápido e funcional!** 📚✨
