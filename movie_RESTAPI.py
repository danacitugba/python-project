import requests

def get_movies_from_tastedive(word, key="XXXXXXXXX"):
    baseurl = "https://tastedive.com/api/similar"
    param_diction = {}
    param_diction["q"] = word
    param_diction["type"] = "movies"
    param_diction["limit"] = "5"
    param_diction["k"] = key
    resp = requests.get(baseurl, params=param_diction)
    filmler = resp.json()
    return filmler


def extract_movie_titles(word):
    benzer_filmler = [i["Name"] for i in word["Similar"]["Results"]]
    return benzer_filmler


def get_related_titles(movie_input):
    ana_liste = []
    for i in movie_input:
        for j in extract_movie_titles(get_movies_from_tastedive(i)):
            if j not in ana_liste:
                ana_liste.append(j)
    return ana_liste


def get_movie_data(movieName, key="XXXXXXXXXXX"):
    baseurl = "http://www.omdbapi.com/"
    params_d = {}
    params_d["t"] = movieName
    params_d["r"] = "json"
    params_d["apikey"] = key
    resp = requests.get(baseurl, params=params_d)
    respDic = resp.json()
    return respDic


def get_movie_rating(liste):
    rating = 0
    for d in liste["Ratings"]:
        if d["Source"] is "Rotten Tomatoes":
            rating = int(d["Value"][:2])
    return rating


def get_sorted_recommendations(filmler):
    benzer_filmler = get_related_titles(filmler)
    benzer_filmler = sorted(benzer_filmler, key=lambda isim: (get_movie_rating(get_movie_data(isim)), isim),
                            reverse=True)
    return benzer_filmler


#This project will take you through the process of mashing up data from two different APIs to make movie recommendations. The TasteDive API lets you provide a movie (or bands, TV shows, etc.) as a query input, and returns a set of related items. The OMDB API lets you provide a movie title as a query input and get back data about the movie, including scores from various review sites (Rotten Tomatoes, IMDB, etc.).
#You will put those two together. You will use TasteDive to get related movies for a whole list of titles. You’ll combine the resulting lists of related movies, and sort them according to their Rotten Tomatoes scores (which will require making API calls to the OMDB API.)
#The documentation for the API is at https://tastedive.com/read/api.
#The documentation for the API is at https://www.omdbapi.com/
#1. def get_movies_from_tastedive(movieName, key="ExampleKey"):It should take two input parameter, a string that is the name of a movie or music artist and the API key's. The function should return the 5 TasteDive results that are associated with that string; rigth now it only get movies, not other kinds of media. It will return a python dictionary with just one key, ‘Similar’.
#2. def extract_movie_titles(movieName):Extracts just the list of movie titles from a dictionary
#3. def get_related_titles(listMovieName):It takes a list of movie titles as input. It gets five related movies for each from TasteDive, extracts the titles for all of them, and combines them all into a single list. Don’t include the same movie twice.
#4. def get_movie_data(movieName, key="ExampleKey"):It takes in one parameter which is a string that should represent the title of a movie you want to search. The function should return a dictionary with information about that movie.
#5. def get_movie_rating(movieNameJson):It takes an OMDB dictionary result for one movie and extracts the Rotten Tomatoes rating as an integer. If there is no Rotten Tomatoes rating, return 0.
#6. get_sorted_recommendations(listMovieTitle):