# Referência 03 — Template do Relatório de Auditoria (Fase 2)

O relatório da Fase 2 DEVE seguir exatamente o formato abaixo (é também o formato impresso no console e salvo em `../reports/audit-project-<n>.md`).

## Formato

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-diretório-do-projeto>
Stack:   <Language + Framework>
Files:   <N> analyzed | ~<L> lines of code

## Summary
CRITICAL: <x> | HIGH: <y> | MEDIUM: <z> | LOW: <w>

## Findings

### [CRITICAL] <Título do achado>
File: <arquivo>:<linha(s)>
Description: <o que está errado, objetivo e específico>
Impact: <consequência concreta>
Recommendation: <correção apontada (pode referenciar o playbook)>

### [HIGH] <Título>
File: <arquivo>:<linha(s)>
...

### [MEDIUM] <Título> ...

### [LOW] <Título> ...

================================
Total: <N> findings
================================
```

## Regras

1. **Ordenação:** todos os findings em ordem de severidade — CRITICAL → HIGH → MEDIUM → LOW. Nunca intercale.
2. **Localização exata:** todo finding tem `arquivo:linha` ou `arquivo:linha-linha`. Confirme lendo o arquivo (não estime).
3. **Cobertura mínima:** no mínimo 5 findings por projeto; inclua pelo menos 1 CRITICAL ou HIGH. Se o catálogo não se aplicar a algum ponto, não invente — prefira precisão.
4. **Deprecated APIs:** se houver uso de API deprecated (checklist AP-14), inclua um finding específico (ex.: `### [MEDIUM] APIs deprecated (datetime.utcnow)` com a lista de ocorrências e o equivalente moderno). Se não houver, mencione explicitamente "Nenhuma API deprecated encontrada" ao final do relatório.
5. **Resumo:** os contadores do `## Summary` devem bater com a contagem real dos findings.
6. **Linguagem:** descrições em português (pt-BR), objetivas, cada uma em 1-3 linhas.
7. **Impacto e recomendação são obrigatórios** em todos os findings.
8. O arquivo salvo em `../reports/` contém o mesmo conteúdo do console (o bloco completo acima), em Markdown válido.

## Exemplo preenchido (parcial)

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~795 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] SQL Injection em todas as queries
File: models.py:28,48,57,68,109,126,140,148,158,164,174,188,220,279,289
Description: Queries montadas por concatenação de strings com dados do usuário.
Impact: Vazamento e destruição de dados; bypass de login.
Recommendation: Parametrizar todas as queries (playbook §1).

### [CRITICAL] Credenciais hardcoded
File: app.py:7
Description: SECRET_KEY fixa "minha-chave-super-secreta-123" no código.
Impact: Segredo exposto no repositório; impossível rotacionar.
Recommendation: Mover para variável de ambiente via módulo de config (playbook §2).

...

================================
Total: 14 findings
================================
```
