# Agent Catalog

Repositorio de agentes e skills reutilizaveis para analise, planejamento, implementacao, revisao e orquestracao de fluxos de engenharia de software.

## Estrutura

- `workflow-orchestrator/`: roteamento e sintese multiagente.
- `shared-skills/`: runtime, utilitarios de contexto e ordenacao de execucao.
- `engineering-specialists/`: especialistas de arquitetura, dados, build, interface, testes, contexto e manutencao.
- `quality-specialists/`: especialistas de revisao, impacto e gates de qualidade.
- `documentation-specialist/`, `performance-specialist/`, `security-specialist/`: especialistas independentes.
- `design-specialists/design-system-specialist/`: skill de design system com referencia visual reutilizavel.

## Convencoes

- Todo agente e descrito por `skill.json`.
- Todos os agentes executam via Python usando o mesmo runtime compartilhado.
- Nomes, aliases e tags sao usados pelo workflow-orchestrator para roteamento.
- Dependencias opcionais entre agentes sao declaradas por `depends_on`.

## Uso

Listar agentes:

```powershell
python .\autoload_skills.py --list
```

Executar um agente especifico:

```powershell
python .\autoload_skills.py architecture-specialist "projetar arquitetura para plataforma multi-tenant"
```

Roteamento automatico:

```powershell
python .\workflow-orchestrator\main.py "planejar migracao, revisar impacto e definir estrategia de testes"
```

Validacao completa do catalogo:

```powershell
python .\validate_catalog.py
```
