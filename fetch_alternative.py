################################################################
## Script pour remplacer fetch.py de szz unleashed            ##
## Utilise l'API github                                       ##
################################################################
## sleep de 2.5 secondes pour s'assurer de ne pas être bloqué ##
## par la limite d'utilisation de l'API de githu              ##
################################################################
## Utilisation:                                               ##
## python fetch_alternative.py <propriétaire> <répertoire>    ##
################################################################
## Note: fonctionne seulement pour les projets github         ##
## utilisant un ou plusieurs labels                           ##
################################################################
## le sleep peut être enlevé pour les projets ayant moins de  ##
## 840 bogues (inclusivement) (28 pages) au total             ##
## (tout labels confondu)
################################################################
## fichier token.env contenant un token github valide         ##
## est requis pour que le script fonctionne                   ##
## GITHUB_TOKEN=<votre token>                                 ##
################################################################


# imports
import json
import math
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import requests
import sys

# load token
load_dotenv('token.env')
token = os.getenv('GITHUB_TOKEN')

# valeurs par default
nproprio = ""
repo = ""

# const and variables
BASE_URL = f"https://api.github.com/"

NUMBER_RES = 30


def convert_date_format(date_str):
    # Parse the input date string to a datetime object
    dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    
    # Convert the datetime object to the desired format
    new_date_str = dt.strftime('%Y-%m-%dT%H:%M:%S.%f+0000')
    
    return new_date_str


def findAllBugLabels(repoId, searchKeyword) :

    listeLabels = []

    try:

        verifQuery = f"{searchKeyword}&repository_id={repoId}"
        response2: requests.Response = requests.get(
            f"{BASE_URL}search/labels?q={verifQuery}&per_page=1",
            headers = {'Authorization': f'token {token}'}
        )

        voirResponse = json.loads(response2.content)

        listeLabelsJson = voirResponse["items"]

        for elem in listeLabelsJson:
            listeLabels.append(elem["name"])
        

        print("Labels trouvés sans problème! :)")


    except:
        print("Erreur lors de la recherche de labels! Bug label manquant ou erreur interne :(")

    return listeLabels


def getRepoId(owner, repo):
    id = 0
    query = "repo:\"" + owner + "/" + repo + "\""
    response: requests.Response = requests.get(
        f"{BASE_URL}search/repositories?q={query}&per_page=1",
        headers = {'Authorization': f'token {token}'}
    )

    if (response.status_code == 200):
        result = json.loads(response.content)

        result_tab = result["items"]

        for rep in result_tab:
            id = rep["id"]
    return id


# Trouver tous les bogues et les mettre dans un dictionnaire
def findAllBugs(proprio, nomRepo, listLabels):
    #resultat = ""
    currentBugs = 0
    currentBugsLabel = 0
    listIssues = []

    try:

        for label in listLabels:

            page = 1
            maxPage = 1
            while page <= maxPage :

                #verifQuery = f"repo:{proprio}/{nomRepo}+type:issue+label:{label}+is:closed"
                verifQuery = f"repo:{proprio}/{nomRepo}+label:{label}+is:closed&page={page}"
                responseVerif: requests.Response = requests.get(
                    f"{BASE_URL}search/issues?q={verifQuery}",
                    headers = {'Authorization': f'token {token}'}
                )

                responseCountJson = json.loads(responseVerif.content)

                #currentBugs += responseCountJson["total_count"]
                #currentBugsLabel = responseCountJson["total_count"]

                if page == 1:
                    currentBugs += responseCountJson["total_count"]
                    currentBugsLabel = responseCountJson["total_count"]
                    maxPage = math.ceil(currentBugsLabel/30) # nombre de page total avec 30 par page

                page += 1 # incrémentation

                bugs = responseCountJson["items"]

                for bug in bugs:
                    #id = bug["id"]
                    id = bug["number"]
                    dateCreation = convert_date_format( bug["created_at"] )
                    #dateFermeture = convert_date_format( bug["updated_at"] )
                    dateFermeture = convert_date_format( bug["closed_at"] )

                    key = nomRepo + "-" + str(id)

                    issue = {"key": key, "fields": { "created": dateCreation, "resolutiondate": dateFermeture } }
                    listIssues.append(issue)

                print("Lecture de la page " + str(page-1) + " de la recherche des bogues fermés du label:" + label)
                time.sleep(2.5) # pour empêcher d'être bloqué par la limite d'utilisation du githubAPI 30 request par minutes


        print("Il y a " + str(currentBugs) + " bogues résolus dans le projet " + proprio + "/" + nomRepo + " !!! :O")
    
    except:

        print("Erreur lors de la recherche de bogues!")

    resultat = { "expand": "schema, names", "startAt": 0, "maxResults": currentBugs, "total": currentBugs, "issues": listIssues }

    return resultat


def allStepds(proprio, nomRepo):
    repoId = getRepoId(proprio, nomRepo)
    listeLabels = findAllBugLabels(repoId, "bug")
    return findAllBugs(proprio=proprio, nomRepo=nomRepo, listLabels=listeLabels)


def execution(proprio, nomRepo):
    try:
        contenu = allStepds(proprio, nomRepo)
        #print("ici")

        if not os.path.exists("issues"):
            os.makedirs("issues")

        with open("issues/res0.json", 'w') as ecriture:
                json.dump(contenu, ecriture)
    except:
        print("Erreur lors de l'écriture du fichier! :(")


##############################################################################

# lecture des paramètres
if len(sys.argv) < 3:
    print("Veuillez indiquer le pseudo du propriétaire et le nom du répertoire svp")
    print("python fetch_alternative.py <propriétaire> <répertoire>")
    sys.exit(0)
else:
    nproprio = sys.argv[1]
    repo = sys.argv[2]


# appel
execution(nproprio, repo)