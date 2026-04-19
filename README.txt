## Como iniciar o projeto no seu computador

### 1. Clonar o repositório
```bash
git clone https://github.com/David-Mandel0707/diego-clean.git
cd diego-clean
```

### 2. Criar e ativar o ambiente virtual
```bash
python -m venv .venv
```
Windows:
  ```bash
  .venv\Scripts\activate
  ```
Mac/Linux:
  ```bash
  source .venv/bin/activate
  ```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Criar o arquivo .env
Peça ao David as seguintes variáveis e crie um arquivo `.env` na raiz do projeto contendo o seguinte:
  SECRET_KEY=***********
  DATABASE_URL=*********
  DEBUG=****************
  ALLOWED_HOSTS=********

### 5. Criar seu branch
```bash
git checkout -b seu-nome
```
> Nunca trabalhe diretamente no main.

## Uso diário

### Adicionar novos módulos obrigatórios ao requirements.txt
```bash
pip freeze > requirements.txt
```

### Trabalhar e enviar alterações
```bash
git add .
git commit -m "descrição do que foi feito"
git push origin seu-nome
```

### Receber atualizações do main
```bash
git fetch origin
git merge main
```