from django.shortcuts import render
from lxml import etree
import sys
import os
from django.http import HttpResponse
import requests
import lxml.etree as ET
from BaseXClient import BaseXClient
from EDC_Project.settings import BASE_DIR
import os

MOVIES_NEWS = "https://www.cinemablend.com/rss/topic/news/movies"
MOVIES_SITE = "http://image.tmdb.org/t/p/w200"
session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
QUERY_TOP_MOVIES = "import module namespace funcs = \"com.funcs.catalog\"; funcs:top-movies()"
NO_IMAGE = os.path.join(BASE_DIR, "webapp/files/NoImage.jpg")


def get_top_rated_movies():
    # create query instance
    movies_xml = os.path.join(BASE_DIR, "webapp/files/movies.xml")
    query = session.query(QUERY_TOP_MOVIES).execute()
    print(query)
    movies_list = []
    tree = etree.XML(query)
    movies = tree.xpath(".//movie")

    for movie in movies:
        movie_temp = []
        movie_temp.append(movie.find("original_title").text)
        movie_temp.append(movie.find("vote_average").text)
        if movie.find("poster_path").text is not None:
            poster_url = MOVIES_SITE + movie.find("poster_path").text
        else:
            poster_url = NO_IMAGE
        movie_temp.append(poster_url)

        movies_list.append(movie_temp)

    return movies_list


def get_rss():
    response = requests.get(MOVIES_NEWS)
    tree = etree.XML(response.text)
    movies = []
    items = tree.xpath(".//item")
    for item in items:
        if item.find("title") is not None and item.find("description") is not None:

            description = item.find("description").text.replace("<p>","")
            description = description.replace("</p>","")
            description = description.replace("<em>","")
            description = description.replace("</em>", "")

            movie = []
            movie.append(item.find("title").text)
            movie.append(description)

            if item.find("enclosure") is not None:
                movie.append(str(item.find("enclosure").get('url')))
            if item.find("guid") is not None:
                movie.append(item.find("guid").text)
            movies.append(movie)

    return movies


def index(request):
    top_movies = get_top_rated_movies()
    news = get_rss()
    t_params = {'news': news,
                'top_movies': top_movies}

    return render(request, 'index.html', t_params)


def movies(request):
    pxml = 'movies.xml'
    pxslt = 'movies-list.xsl'
    fxml = os.path.join(BASE_DIR, 'webapp/files/' + pxml)
    fxslt = os.path.join(BASE_DIR, 'webapp/files/' + pxslt)

    tree = ET.parse(fxml)
    xslt = ET.parse(fxslt)
    transform = ET.XSLT(xslt)
    html = transform(tree)

    genres = get_movie_genres()

    tparams = {
        'html': html,
        'movie_genres': genres,
    }

    return render(request, 'movies_list.html', tparams)

def get_movie_genres():
    fname = 'movies.xml'
    pname = os.path.join(BASE_DIR, 'webapp/files/' + fname)
    xml = ET.parse(pname)
    info = []
    query = '//movie/genres/item/name'
    genres = xml.xpath(query)

    for g in genres:
        info.append(g.text)

    return info

def series(request):
    pxml = 'series.xml'
    pxslt = 'series-list.xsl'
    fxml = os.path.join(BASE_DIR, 'webapp/files/' + pxml)
    fxslt = os.path.join(BASE_DIR, 'webapp/files/' + pxslt)

    tree = ET.parse(fxml)
    xslt = ET.parse(fxslt)
    transform = ET.XSLT(xslt)
    html = transform(tree)
    tparams = {
        'html_series': html,
    }

    return render(request, 'series_list.html', tparams)

def detail_info(request):

    m_review = movie_review()

    tparams = {
        'html_review': m_review
    }

    return render(request, 'info.html', tparams)

def movie_review():
    pxml = 'reviews.xml'
    pxslt = 'movie-reviews.xsl'
    fxml = os.path.join(BASE_DIR, 'webapp/files/' + pxml)
    fxslt = os.path.join(BASE_DIR, 'webapp/files/' + pxslt)

    tree = ET.parse(fxml)
    xslt = ET.parse(fxslt)
    transform = ET.XSLT(xslt)
    html = transform(tree)

    return html
