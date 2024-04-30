
# Cheatsheet Modèles Scikit-learn

## Configuration et Outils
```python
from sklearn import set_config
set_config(display='diagram')  # Diagramme visuel des pipelines
```

## Estimators Base
- **Estimator**: base.BaseEstimator
- **Classifier**: base.ClassifierMixin
- **Regressor**: base.RegressorMixin
- **Cluster**: base.ClusterMixin
- **Transformer**: base.TransformerMixin

## Prétraitement
```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, MaxAbsScaler
from sklearn.preprocessing import RobustScaler, Normalizer, Binarizer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, OrdinalEncoder
```
- **StandardScaler**: Centre et réduit
- **MinMaxScaler**: Rééchelonne entre un min et un max
- **MaxAbsScaler**: Rééchelonne par la valeur absolue max
- **RobustScaler**: Centre et réduit en utilisant la médiane et l'écart interquartile
- **Normalizer**: Normalise les échantillons individuellement à la norme unitaire
- **Binarizer**: Convertit en valeurs binaires selon un seuil
- **OneHotEncoder**: Encode les variables catégorielles en tant que matrice One-hot / N-hot
- **LabelEncoder**: Encode les étiquettes cibles avec une valeur entre 0 et n_classes-1
- **OrdinalEncoder**: Convertit les caractéristiques catégorielles en entiers

## Régression
```python
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.linear_model import ElasticNet, Lars, BayesianRidge
```
- **LinearRegression**: Régression linéaire simple
- **Ridge**: Régression de crête (L2 penalty)
- **Lasso**: Régression Lasso (L1 penalty)
- **ElasticNet**: Régression élastique Net (pénalités L1 et L2)
- **Lars**: Moindres angles régression
- **BayesianRidge**: Régression bayésienne de crête

## Classification
```python
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
```
- **LogisticRegression**: Régression logistique pour la classification binaire
- **SVC**: Machines à vecteurs de support pour la classification
- **KNeighborsClassifier**: Classification basée sur les k-plus proches voisins

## Clustering
```python
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
```
- **KMeans**: K-Means clustering
- **DBSCAN**: Clustering basé sur la densité (DBSCAN)
- **AgglomerativeClustering**: Regroupement hiérarchique agglomératif

## Sélection de modèles
```python
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
```
- **train_test_split**: Divise les données en ensembles de formation et de test
- **GridSearchCV**: Recherche exhaustive sur une grille de paramètres
- **cross_val_score**: Évaluation de la validation croisée

## Métriques
```python
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import roc_auc_score, roc_curve
```
- **accuracy_score**: Précision de classification
- **confusion_matrix**: Matrice de confusion
- **mean_squared_error**: Erreur quadratique moyenne pour la régression
- **mean_absolute_error**: Erreur absolue moyenne pour la régression
- **roc_auc_score**: Aire sous la courbe ROC
- **roc_curve**: Courbe ROC

## Sauvegarde et chargement de modèles
```python
from joblib import dump, load
# Sauvegarde
dump(model, 'model.joblib')
# Chargement
model = load('model.joblib')
```


## sklearn.base: Classes de base et fonctions utilitaires
- **BaseEstimator** : Classe de base pour tous les estimateurs. `from sklearn.base import BaseEstimator`
- **ClassifierMixin** : Mixin pour les classificateurs. `from sklearn.base import ClassifierMixin`
- **RegressorMixin** : Mixin pour les régresseurs. `from sklearn.base import RegressorMixin`

## sklearn.ensemble: Méthodes d'ensemble
- **RandomForestClassifier** : Classificateur d'ensemble utilisant des arbres de décision. `from sklearn.ensemble import RandomForestClassifier`
- **GradientBoostingClassifier** : Optimisation basée sur les arbres de régression. `from sklearn.ensemble import GradientBoostingClassifier`

## sklearn.utils: Utilitaires
- **shuffle** : Mélange des ensembles de données. `from sklearn.utils import shuffle`

## sklearn.tree: Arbres de décision
- **DecisionTreeClassifier** : Classificateur d'arbre de décision. `from sklearn.tree import DecisionTreeClassifier`

## sklearn.preprocessing: Prétraitement et normalisation
- **StandardScaler** : Standardise les caractéristiques en éliminant la moyenne et en mettant à l'échelle la variance. `from sklearn.preprocessing import StandardScaler`

## sklearn.pipeline: Pipeline
- **Pipeline** : Chaîne de transformations avec un estimateur final. `from sklearn.pipeline import Pipeline`

## sklearn.neural_network: Modèles de réseau neuronal
- **MLPClassifier** : Perceptron multicouche, un type de réseau de neurones. `from sklearn.neural_network import MLPClassifier`

## sklearn.neighbors: Plus proches voisins
- **KNeighborsClassifier** : Classifieur implémentant le vote des k-plus proches voisins. `from sklearn.neighbors import KNeighborsClassifier`

## sklearn.naive_bayes: Naive Bayes
- **GaussianNB** : Classificateur Naive Bayes pour des caractéristiques gaussiennes. `from sklearn.naive_bayes import GaussianNB`

## sklearn.multioutput: Régression et classification multi-sorties
- **MultiOutputClassifier** : Stratégie pour étendre les classificateurs pour supporter la classification multi-sortie. `from sklearn.multioutput import MultiOutputClassifier`

## sklearn.multiclass: Classification multiclasses
- **OneVsRestClassifier** : Stratégie pour réaliser une classification multi-classe/multi-étiquette. `from sklearn.multiclass import OneVsRestClassifier`

## sklearn.model_selection: Sélection de modèles
- **cross_val_score** : Évaluer un score en utilisant la validation croisée. `from sklearn.model_selection import cross_val_score`

## sklearn.metrics: Métriques
- **accuracy_score** : Calcule l'exactitude, la fraction de bonnes prédictions. `from sklearn.metrics import accuracy_score`

## sklearn.manifold: Apprentissage de variété
- **TSNE** : Incorporation de voisins stochastiques distribués en T pour la réduction de dimensionnalité. `from sklearn.manifold import TSNE`

## sklearn.linear_model: Modèles linéaires
- **LinearRegression** : Régression linéaire. `from sklearn.linear_model import LinearRegression`

## sklearn.kernel_approximation: Approximation du noyau
- **RBFSampler** : Approximation de la fonction de base radiale (RBF). `from sklearn.kernel_approximation import RBFSampler`

## sklearn.impute: Imputation
- **SimpleImputer** : Imputation des valeurs manquantes en utilisant différentes stratégies. `from sklearn.impute import SimpleImputer`

## sklearn.gaussian_process: Processus gaussiens
- **GaussianProcessClassifier** : Classificateur basé sur des processus gaussiens. `from sklearn.gaussian_process import GaussianProcessClassifier`

## sklearn.feature_selection: Sélection de caractéristiques
- **SelectKBest** : Sélectionne les K meilleures caractéristiques basées sur les tests statistiques univariés. `from sklearn.feature_selection import SelectKBest`

## sklearn.feature_extraction: Extraction de caractéristiques
- **CountVectorizer** : Convertit une collection de documents texte en une matrice de dénombrements de jetons. `from sklearn.feature_extraction.text import CountVectorizer`

## sklearn.exceptions: Exceptions et avertissements &#8203;``【oaicite:0】``&#8203;

