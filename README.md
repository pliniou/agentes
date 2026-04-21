# Agent Catalog

Repositorio de agentes e skills reutilizaveis para analise, planejamento, implementacao, revisao e orquestracao de fluxos de engenharia de software.

## Estrutura

- `core/`: runtime compartilhado, contexto, catalogo e ordenacao de execucao.
- `especialistas/`: especialistas por dominio tecnico, incluindo arquitetura, dados, build, interface, testes e concerns transversais.
- `orchestrators/workflow-orchestrator/`: roteamento e sintese multiagente.

## Convencoes

- Todo agente e descrito por `skill.json`.
- Todos os agentes executam via Python usando o mesmo runtime compartilhado.
- Cada manifesto declara `type` (`specialist` ou `orchestrator`) e `depends_on`, mesmo quando a lista esta vazia.
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
python .\orchestrators\workflow-orchestrator\main.py "planejar migracao, revisar impacto e definir estrategia de testes"
```

Validacao completa do catalogo:

```powershell
python .\validate_catalog.py
```
