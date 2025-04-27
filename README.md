# PlantConnectome Database

Welcome to the Plant Connectome project!  The latest version of this project is live at: [https://plant.connectome.tools/](https://plant.connectome.tools/).

This GitHub repository is publicly-accessible and serves as a means of hosting the project's application and storing the code generated for this project.

## What is PlantConnectome?

PlantConnetome is a database that contains over 2.7 million entities comprising genes, metabolites, tissues, organs, and other biological components, with several 4.8 million interaction types between the said amount of entities.  These entities and interactions were obtained from having GPT-4o process over 71000 paper abstracts and full-texts from various popular scientific journals.

## Folders of this Repository

This repository contains files and folders that are crucial in getting PlantConnectome up and running, of which include:

1.  `static`

    This folder contains images, CSS, and JavaScript that PlantConnectome's pages use.  All CSS are stored in the `css` sub-directory while all JS are stored in the `js` sub-directory.

2.  `templates`

    This folder contains HTML templates that will be rendered and displayed to the user.

3.  `tests`

    This folder contains unit tests (so far) to ensure that the application is running smoothly.

4.  `utils`

    This folder contains utility functions that are used by the routes to perform certain functionalities.

5.  `routes`

    This folder contains the applicaton's routes.


## Setting up local dev environment

### Prerequisites

Have a working install of MongoDB, or you can run them via docker. https://www.mongodb.com/docs/manual/tutorial/install-mongodb-community-with-docker/

Have a working copy of Python installed. Versions known to have worked successfully: 3.12.2, ... (add on to the list)

### Python enviroment

You may want to setup a virtual environment for this project via venv, virtualenv or poetry supported tools.

Install Python package dependencies via pip and the requirements.txt file

```
pip install -r requirements.txt
```

### Database setup

Ensure you have these 4 json files in root directory, each json file should be a list of dictionaries:

- all_dic.json (all the information in the entity-entity relationship)
- authors.json (contains the pubmedID, gene, pub_date, doi, title, authors, journal)
- gene_alias.json (each gene as a key and value will contain its alias names)
- scientific_chunks.json (pmid section number as the key and values are the text chunk)

They should be uploaded to a MongoDB database named "PlantConnectome". The collection names are the names of the 4 files.

The mongodb python client is currently connecting via "mongodb://localhost:27017".


### Running local development env

```
python app.py
```

### Colab code for manuscript
Colab code for manuscript can be found at PlantConnectome_2025version/connectome_files/previews/Connectome2025_Figures.ipynb