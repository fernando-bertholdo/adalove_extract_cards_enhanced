# ✅ TODO - Tarefas Técnicas

Lista de tarefas técnicas e melhorias pontuais. Para features de longo prazo, ver [ROADMAP.md](./ROADMAP.md).

---

## 🔥 Urgente / Próximos Passos

- [ ] Revisar e testar extração em diferentes módulos/turmas
- [ ] Validar se todas as frentes estão sendo detectadas corretamente
- [ ] Documentar casos conhecidos de falha na ancoragem

---

## 🐛 Bugs Conhecidos

- [ ] Timeout em semanas com muitos cards (>50)
- [ ] Cards sem data/hora quebram normalização temporal
- [ ] Professor não detectado quando há múltiplos nomes no texto

---

## 🔧 Melhorias Técnicas

### Código
- [ ] Adicionar type hints em todas as funções
- [ ] Refatorar função `enrich_cards()` (muito longa)
- [ ] Extrair constantes mágicas para arquivo de config
- [ ] Adicionar docstrings em formato Google/NumPy

### Performance
- [ ] Profiling para identificar gargalos
- [ ] Cache de páginas já visitadas
- [ ] Paralelização de extração de cards (se possível)

### Documentação
- [ ] Adicionar exemplos de uso avançado
- [ ] Criar FAQ com erros comuns
- [ ] Documentar estrutura do HTML do AdaLove (para manutenção)

---

## 📦 Infraestrutura

- [ ] Configurar GitHub Actions para CI/CD
- [ ] Adicionar pre-commit hooks (black, isort, flake8)
- [ ] Configurar dependabot para atualização de dependências
- [ ] Criar Docker image para execução isolada

---

## 📊 Análise de Dados

- [ ] Criar notebook Jupyter com análises exploratórias
- [ ] Gerar relatórios estatísticos por módulo
- [ ] Visualizações de distribuição temporal de cards
- [ ] Análise de correlação entre frentes e horários

---

## 🎯 Quick Wins (Baixo Esforço, Alto Impacto)

- [ ] Adicionar barra de progresso com `tqdm`
- [ ] Implementar modo `--dry-run` para testar sem extrair
- [ ] Adicionar flag `--verbose` para logs detalhados
- [ ] Criar comando `--version` para mostrar versão instalada

---

**Legenda**:
- 🔥 Urgente
- 🐛 Bug
- 🔧 Melhoria
- 📦 Infraestrutura
- 📊 Análise
- 🎯 Quick Win


