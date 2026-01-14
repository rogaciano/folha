# 📸 Novos Campos: Foto e Chave PIX

## ✅ Campos Adicionados

### 1. **Foto do Funcionário**
- **Tipo**: ImageField
- **Obrigatório**: Não
- **Upload**: `media/funcionarios/fotos/`
- **Uso**: Exibida na tela de detalhes do funcionário

### 2. **Chave PIX**
- **Tipo**: CharField (até 200 caracteres)
- **Obrigatório**: Não
- **Formatos aceitos**: CPF, E-mail, Telefone ou Chave Aleatória
- **Uso**: Para pagamentos via PIX

---

## 🔧 Como Usar

### Cadastrar/Editar Funcionário:

1. Acesse **Funcionários** → **Novo Funcionário** (ou edite um existente)
2. Preencha os campos:
   - **Foto**: Clique em "Escolher arquivo" e selecione uma imagem
   - **Chave PIX**: Digite a chave PIX do funcionário
3. Salvar

### Visualizar:

1. Acesse **Funcionários** → Clique no funcionário
2. Na aba **"Informações"**:
   - A foto aparecerá no topo à esquerda (se cadastrada)
   - A chave PIX aparecerá nos dados pessoais

---

## 📁 Estrutura de Arquivos

```
media/
└── funcionarios/
    └── fotos/
        ├── foto1.jpg
        ├── foto2.png
        └── ...
```

---

## ⚙️ Migrações Aplicadas

```bash
# Já executado automaticamente:
python manage.py makemigrations funcionarios
python manage.py migrate
```

Migração criada: `funcionarios/migrations/0002_funcionario_chave_pix_funcionario_foto.py`

---

## 🖼️ Formatos de Imagem Suportados

- **JPG/JPEG**
- **PNG**
- **GIF**
- **BMP**
- **WebP**

**Recomendação**: Use imagens no formato **JPEG** ou **PNG** com resolução máxima de **800x800px** para melhor performance.

---

## 🔐 Segurança

- As fotos são armazenadas no diretório `media/` fora do controle de versão (`.gitignore`)
- Em produção, configure o servidor web (Nginx) para servir os arquivos media
- A chave PIX não é validada automaticamente (aceita qualquer formato)

---

## 📝 Próximas Melhorias (Opcionais)

- [ ] Validação automática de chave PIX
- [ ] Redimensionamento automático de fotos
- [ ] Crop/preview de imagem antes do upload
- [ ] Limite de tamanho de arquivo
- [ ] Suporte a múltiplas chaves PIX

---

**Funcionalidade implementada e pronta para uso!** ✅
