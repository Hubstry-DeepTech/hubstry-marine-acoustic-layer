# HMAL Lab

Página pública de evidências do HMAL (`docs/FRONTEND_PLAN.md`). Estática, sem servidor nem banco de dados.

```
python site/build_data.py      # dados a partir do manifesto e dos resultados versionados (falha se algo divergir)
cd site && npm ci && npm run build   # página em site/dist
npm run preview                # visualização local
```

Publicação: `.github/workflows/pages.yml`, só a partir do `main`. Os dados gerados (`public/data`, `public/img`) não são versionados.
