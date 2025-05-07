'''
This module contains the routes for entities.
'''
from flask import Blueprint, request, render_template
import pickle
import sys 
import re
from utils.mongo import db
import time

sys.path.append('utils')


catalogue_search = Blueprint('catalogue_search', __name__)
@catalogue_search.route('/catalogue', methods = ['GET'])
def catalogue():

    cata = pickle.load(open('Entity_catalogue2.pkl','rb'))
    #print("Header keys:", cata[0])
    #print("Entities dictionary:", cata[1])

    return render_template("/catalogue.html", entities = cata[1], header=sorted(cata[0]))
