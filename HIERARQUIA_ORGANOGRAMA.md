# 🏢 Estrutura Hierárquica e Organograma

## ✅ Funcionalidades Implementadas

### 1. **Hierarquia de Funcionários**
Cada funcionário pode ter um **superior direto**, criando uma estrutura hierárquica completa da empresa.

**Campo adicionado ao Funcionário:**
- `superior` (ForeignKey para Funcionario) - Define quem é o responsável direto

### 2. **Chefe de Setor**
Cada setor pode ter um **chefe/responsável**.

**Campo adicionado ao Setor:**
- `chefe` (OneToOneField para Funcionario) - Define o responsável pelo setor

---

## 🎯 Como Usar

### ⚡ Hierarquia Automática (RECOMENDADO):

**A hierarquia é definida automaticamente!** Basta configurar o chefe de cada setor:

1. **Definir Chefes de Setor**:
   - Acesse **Admin** → **Setores**
   - Edite um setor
   - No campo **"Chefe do Setor"**, selecione o responsável
   - Salve

2. **Atualizar Hierarquia Existente** (se já tem funcionários cadastrados):
   ```bash
   python manage.py atualizar_hierarquia
   ```

**Regra:** O chefe do setor é automaticamente o superior de todos os funcionários daquele setor.

**Novos funcionários** já vêm com o superior definido automaticamente ao selecionar o setor!

### Visualizar Organograma:

Acesse o menu **"Organograma"** no topo da página ou:
```
http://localhost:8000/funcionarios/organograma/
```

Você terá duas visualizações:

#### **1. Visão Hierárquica** 📊
- Mostra a estrutura completa da empresa em árvore
- Começa pelos funcionários da alta direção (sem superior)
- Exibe todos os níveis de subordinação recursivamente
- Código de cores por nível hierárquico:
  - **Roxo**: Alta direção (Nível 0)
  - **Azul**: Primeiro nível
  - **Verde**: Segundo nível
  - **Amarelo/Cinza**: Níveis subsequentes

#### **2. Visão por Setores** 🏢
- Agrupa funcionários por setor/departamento
- Destaca o chefe de cada setor
- Mostra quantos subordinados cada funcionário tem
- Exibe total de funcionários por setor

---

## 📋 Informações Exibidas

### Na página de detalhes do funcionário:

**Aba "Informações":**
- **Superior Direto**: Link clicável para o perfil do superior
- **Nível Hierárquico**: Badge mostrando o nível na hierarquia (0 = topo)
- **Chefe de Setor**: Badge especial se o funcionário é chefe de algum setor

**Nova Aba "Equipe":**
- **Cadeia Hierárquica Superior**: Breadcrumb navegável mostrando todos os superiores até o topo
- **Subordinados Diretos**: Tabela com todos os funcionários que respondem diretamente a ele
  - Foto, nome, função, setor, salário
  - Quantidade de subordinados de cada um
  - Link para ver detalhes

---

## 🔧 Métodos Úteis Adicionados

### No modelo `Funcionario`:

```python
# Retorna subordinados diretos (ativos)
funcionario.get_subordinados_diretos()

# Retorna TODOS os subordinados (recursivo)
funcionario.get_todos_subordinados()

# Retorna a cadeia de comando até o topo
funcionario.get_hierarquia_superior()

# Verifica se é chefe de algum setor
funcionario.is_chefe()

# Retorna o nível hierárquico (0 = topo)
funcionario.get_nivel_hierarquico()
```

### No modelo `Setor`:

```python
# Retorna todos os funcionários ativos do setor
setor.get_funcionarios_ativos()
```

---

## 💡 Casos de Uso

### Exemplo 1: Estrutura Simples
```
CEO (Nível 0, sem superior)
├── Diretor de TI (superior: CEO)
│   ├── Coordenador de Desenvolvimento (superior: Diretor TI)
│   │   ├── Desenvolvedor A (superior: Coordenador)
│   │   └── Desenvolvedor B (superior: Coordenador)
│   └── Analista de Suporte (superior: Diretor TI)
└── Diretor Financeiro (superior: CEO)
    └── Contador (superior: Diretor Financeiro)
```

### Exemplo 2: Chefes de Setor
```
Setor: TI → Chefe: Diretor de TI
Setor: Financeiro → Chefe: Diretor Financeiro
Setor: Desenvolvimento → Chefe: Coordenador de Desenvolvimento
```

---

## 🎨 Recursos Visuais

- ✅ Fotos dos funcionários (ou iniciais em avatar)
- ✅ Badges de função e cargo
- ✅ Ícones indicando:
  - 👑 Alta direção
  - 💼 Chefe de setor
  - 👥 Quantidade de subordinados
- ✅ Cores diferenciadas por nível hierárquico
- ✅ Navegação clicável entre perfis
- ✅ Responsivo e mobile-friendly

---

## 📊 Benefícios

1. **Visibilidade**: Enxergue claramente a estrutura da empresa
2. **Navegação**: Acesse rapidamente qualquer nível da hierarquia
3. **Gestão**: Identifique facilmente quem responde para quem
4. **Análise**: Veja quantos subordinados cada gestor tem
5. **Organização**: Mantenha os setores bem estruturados

---

## 🔐 Validações

- ✅ Um funcionário **não pode ser seu próprio superior**
- ✅ O campo superior é **opcional** (alta direção não tem superior)
- ✅ Se um funcionário for removido, os subordinados não são afetados (`SET_NULL`)
- ✅ Apenas funcionários **ativos** aparecem como opções de superior

---

## 🚀 Próximos Passos Sugeridos

- [ ] Exportar organograma em PDF
- [ ] Gráfico visual interativo (tipo árvore)
- [ ] Análise de span of control (número ideal de subordinados)
- [ ] Histórico de mudanças hierárquicas
- [ ] Integração com sistema de aprovações

---

**Funcionalidade completa e pronta para uso!** 🎉
