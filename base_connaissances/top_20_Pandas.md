**Importation de Pandas** :
`import pandas as pd`
**Création d'une série** :
`s = pd.Series([1, 2, 3], index=['a', 'b', 'c'])`
**Création d'un DataFrame à partir d'un dictionnaire** :
`df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})`
**Lecture d'un fichier CSV** :
`df = pd.read_csv('file.csv')`
**Écriture dans un fichier CSV** :
`df.to_csv('file.csv')`
**Lecture d'un fichier Excel** :
`df = pd.read_excel('file.xlsx')`
**Écriture dans un fichier Excel** :
`df.to_excel('file.xlsx')`
**Lecture d'une requête SQL** :
`df = pd.read_sql_query('SELECT * FROM table', connection_object)`
**Écriture dans une table SQL** :
`df.to_sql('table', connection_object)`
**Obtention des premiers éléments d'une série ou d'un DataFrame** :
`s.head()`, `df.head()`
**Obtention des derniers éléments d'une série ou d'un DataFrame** :
`s.tail()`, `df.tail()`
**Obtention de la forme d'un DataFrame** :
`df.shape`
**Obtention des types de données d'un DataFrame** :
`df.dtypes`
**Obtention des noms de colonnes d'un DataFrame** :
`df.columns`
**Sélection d'une colonne d'un DataFrame** :
`df['A']`
**Sélection de plusieurs colonnes d'un DataFrame** :
`df[['A', 'B']]`
**Sélection d'une ligne d'un DataFrame par son indice** :
`df.loc[0]`
**Sélection de plusieurs lignes d'un DataFrame par leurs indices** :
`df.loc[[0, 1, 2]]`
**Sélection d'une ligne d'un DataFrame par sa position** :
`df.iloc[0]`
**Sélection de plusieurs lignes d'un DataFrame par leurs positions** :
`df.iloc[[0, 1, 2]]`

**option pour read_csv**:
```bash
pd.read_csv(filepath_or_buffer,
            sep=',',  # separateur des colonnes , ; ou espace
            delimiter=None,
            header='infer',  #choix de l'entete, None, 0 pour la premiere ligne
            names=None,
            index_col=None,
            usecols=None,
            squeeze=False,
            prefix=None,
            mangle_dupe_cols=True,
            dtype=None, #
            engine=None,
            converters=None,
            true_values=None,
            false_values=None,
            skipinitialspace=False,
            skiprows=None,
            skipfooter=0,
            nrows=None,
            na_values=None,
            keep_default_na=True,
            na_filter=True,
            verbose=False,
            skip_blank_lines=True,
            parse_dates=False,
            infer_datetime_format=False,
            keep_date_col=False,
            date_parser=None,
            dayfirst=False,
            cache_dates=True,
            iterator=False,
            chunksize=None,
            compression='infer',
            thousands=None,
            decimal='.',
            lineterminator=None,
            quotechar='"',
            quoting=0,
            doublequote=True,
            escapechar=None,
            comment=None,
            encoding=None,  # encodage par exemple UTF8
            dialect=None,
            error_bad_lines=True,  #en cas d'erreur sur des lignes donne le numero de la ligne
            warn_bad_lines=True, # affiche un warning si erreur sur une ligne
            delim_whitespace=False,
            low_memory=True,
            memory_map=False,
            float_precision=None,
            storage_options=None)


```

