# Git integration native

## 1. Principe

Snowflake peut se connecter directement à un repo Git

* il ne “clone” pas comme en local
* il crée un **objet `GIT REPOSITORY`** dans Snowflake

## 2. Étapes pour connecter GitHub à Snowflake

### 🔐 Étape 1 - Créer une intégration API

Dans Snowflake :

```sql
CREATE OR REPLACE API INTEGRATION github_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/USER')
  ENABLED = TRUE;
```

Remplace `USER` par le user ou org GitHub

### 🔑 Étape 2 - Authentification (token GitHub)

Créer un **Personal Access Token (PAT)** sur GitHub :

1. GitHub → Settings
2. Developer settings
3. Personal access tokens
4. Génère un token avec :
   * `repo` (lecture)

Ensuite dans Snowflake :

```sql
CREATE OR REPLACE SECRET github_secret
  TYPE = PASSWORD
  USERNAME = 'TON_USER_GITHUB'
  PASSWORD = 'TON_TOKEN';
```

### 🔗 Étape 3 - Lier le secret à l’intégration

```sql
ALTER API INTEGRATION github_integration
SET API_AUTHENTICATION = (
  TYPE = BASIC,
  SECRET = github_secret
);
```

### 📦 Étape 4 - Créer le repo dans Snowflake

```sql
CREATE OR REPLACE GIT REPOSITORY my_repo
  API_INTEGRATION = github_integration
  ORIGIN = 'https://github.com/TON_USER/NOM_DU_REPO.git';
```

### 🔄 Étape 5 - Fetch le repo
Pour synchroniser Snowflake avec GitHub:

```sql
ALTER GIT REPOSITORY my_repo FETCH;
```

## ✅ 3. Utiliser le repo pour Streamlit

Créer une app directement depuis le repo :

```sql
CREATE OR REPLACE STREAMLIT my_app
FROM GIT REPOSITORY my_repo
MAIN_FILE = 'streamlit_app/app.py'
QUERY_WAREHOUSE = my_warehouse;
```

## ✅ 4. Workflow derrière

👉 Ton flow devient :

1. Tu modifies ton code en local
2. Tu pushes sur GitHub
3. Snowflake fait :
   ```sql
   ALTER GIT REPOSITORY my_repo FETCH;
   ```
4. Ton app est à jour

## ⚠️ 5. Points importants

### ❗ Limites actuelles

* pas d’auto-sync → nécessite de faire `FETCH`
* auth parfois tricky
* pas un remplacement complet de Git

### ✅ Bonnes pratiques

* utiliser **branches** (main / dev)
* garder Git comme source de vérité
* utiliser Snowflake juste pour exécuter

***

# Streamlit en local


## Lancer Streamlit en local

```bash
streamlit run app.py
```


* L'app s’ouvre automatiquement dans ton navigateur
* en général sur : `http://localhost:8501`

## Installer Streamlit (si pas déjà fait)

```bash
pip install streamlit
```

## Structure minimale

```
streamlit_app/
  app.py
```

### Bon pattern

```python
# local
import pandas as pd

# snowflake
from snowflake.snowpark.context import get_active_session
```

À adapter avec :

```python
try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    df = session.table("MY_TABLE").to_pandas()
except:
    import pandas as pd
    df = pd.read_csv("data/sample.csv")
```

## Simuler les données Snowflake en local

* export CSV depuis Snowflake

```python
df = pd.read_csv("data/my_data.csv")
```

## Récap

1. dev en local (`streamlit run`)
2. commit sur Git
3. push sur GitHub
4. Snowflake → `FETCH`
5. test dans Snowflake

# Guest User

Oui ✅ — c’est **tout à fait possible**, et c’est même un cas d’usage classique pour un stand ou un salon.  
Par contre, avec **Snowflake + Streamlit**, il y a quelques points importants à comprendre pour que ça fonctionne correctement (et de manière sécurisée).

***

# 🎯 Objectif

> QR code → téléphone → accès au quiz  
> ✅ sans édition  
> ✅ utilisation simple  
> ✅ sans friction pour des visiteurs externes

***

# ⚠️ Contrainte principale Snowflake

Les applications **Streamlit in Snowflake (SiS)** ne sont **PAS publiques par défaut**.

👉 Elles nécessitent :

* un compte Snowflake
* un rôle avec des permissions
* une authentification

Donc ❌ tu **ne peux pas directement exposer** ton app via un simple lien public comme un site web classique.

***

# ✅ Les solutions possibles (du plus simple au plus robuste)

## ✅ Option 1 — Créer un accès invité (recommandé pour ton cas)

👉 Tu crées un utilisateur générique (*type guest*) que tous les visiteurs utiliseront

### Étapes

1. Créer un rôle minimal :

```sql
CREATE ROLE quiz_role;
```

2. Donner uniquement accès à l’app :

```sql
GRANT USAGE ON DATABASE db TO ROLE quiz_role;
GRANT USAGE ON SCHEMA db.schema TO ROLE quiz_role;
GRANT USAGE ON STREAMLIT app TO ROLE quiz_role;
```

3. Créer un utilisateur partagé :

```sql
CREATE USER quiz_guest
  PASSWORD='MotDePasseFort123!'
  DEFAULT_ROLE=quiz_role
  MUST_CHANGE_PASSWORD=FALSE;
```

4. Donner le rôle :

```sql
GRANT ROLE quiz_role TO USER quiz_guest;
```


### QR Code

Générer un QR code vers :

```
https://<account>.snowflakecomputing.com
```

- https://app.snowflake.com/mlrpkfc/ho25547 
- https://mlrpkfc-ho25547.snowflakecomputing.com

➡️ afficher :

* login : `quiz_guest`
* mot de passe : sur le stand


# 💡 Générer un QR Code

Générer un QR vers ton URL :

```python
import qrcode

url = "https://ton-quiz.streamlit.app"
img = qrcode.make(url)
img.save("qr_code_quiz.png")
```
