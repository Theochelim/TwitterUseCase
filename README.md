# Architecture Data - Twitter metrics

Afin de proposer une solution fiable, de mise à disposition de données liées aux tweets mentionnant #Arcane, et pouvant supporter des grands volumes de données, l'architecture est basée sur Google Cloud Platform et est composée des éléments suivants : 

- L'API v2 de Twitter, proposant une API HTTP permettant notamment de rechercher des tweets ou d'obtenir des métriques (nombre de like, RT, réponses, vues...) sur des tweets donnés. 
- Une base de données BigQuery permettant de stocker un grand volume de données sur les tweets.
- Une Google Cloud Fonction, permettant de stocker/mettre à jour les données dans BigQuery. Un exemple (POC) de google cloud function écrit en Python est disponible dans le dossier src (main.py).
- Data Studio, outil Google permettant d'explorer les données présents dans les tables BigQuery et d'en créer des rapports visuels.

![Architecture](images/architecture.png?raw=true "Twitter metrics architecture")

Le choix de Google Cloud Platform, est un choix qui peut être facilement justifié par le fait que l'équipe utilise déjà les outils Google. 
En partant sur ce postulat, les bases de données BigQuery et l'outil de visualisation Data Studio sont les outils de référence pour ce fournisseur de Cloud. En stockant les données sur BigQuery, les data analysts connaissant le SQL, peuvent aisément récupérer les données pour les traiter et les analyser. 

L'intérêt d'utiliser une Google Cloud Function, va être de permettre de simplifier l'automatisation du traitement de mise à jour des données. 
En effet, cette fonction peut être appelé de manière quotidienne (cron), ou "manuellement" via un envoi de requête. 
L'implémentation de cette fonction est écrite en python. Ce language permet facilement de faire des requêtes HTTP pour la communication avec l'API Twitter, et possède également une librairie permettant d'exécuter des requêtes SQL directement sur notre base de données BigQuery. 

![Exemple de métriques stockées dans BigQuery](images/POC_metrics.png?raw=true "Exemple de métriques stockées dans BigQuery")

En conclusion, l'API Twitter étant assez limitée dans sa version free (essential), ce POC n'a testé qu'une volumétrie assez faible de tweets. Cependant, l'architecture proposée est réfléchie pour la mise à l'échelle. 