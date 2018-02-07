import mysql.connector
import csv
import pandas as pd
import similar_movie
from flask import Flask, request, render_template, url_for
import read_files

# Path for the csv which contains url for poster images for all movies
imagefile_path = "/Users/aarthi/COEN499/Recommendation_system/ml-latest-small/links_with_url.csv"
app = Flask(__name__)

# This is the first page when we connect to local host
@app.route('/')
def login_page():
    return render_template("login.html")

# This page is the user specific page which displays his recommended movies
@app.route('/userpage', methods=["POST", "GET"])
def user_page():
    if request.method == 'POST':
        user_id = request.form.get("userid")
        print("userpage", user_id)
        password = request.form.get("password")
        movie_dict, movie_pred_dict = fetch_data_from_table(user_id)
        return render_template("userpage.html", user_page = user_id, movie_info = movie_dict, pred_info = movie_pred_dict,search = False)
    else:
        return "invalid method"

# This page gets displayed when user searches for movies
# search is a boolean value set to true only if user clicks on search in order to diaplay the search results and handle the error in search
# Here we have used user id as a hidden field in order to display the userdetails back again after the search results got loaded
@app.route('/userpage/search', methods=["POST", "GET"])
def user_page_search():
    if request.method == 'POST':
        user_id = request.form.get("userid")
        print("user_id : ", user_id)
        searched_movie = request.form.get("movie_title")
        print("searched_movie title: ", searched_movie)
        movie_dict, movie_pred_dict = fetch_data_from_table(user_id)
        searched_movie_dict, similar_movie_dict = similar_movie.find_similar_movies(searched_movie)
        return render_template("userpage.html", user_page = user_id,movie_info = movie_dict,
                               pred_info = movie_pred_dict, search_movies = searched_movie_dict, sim_movies = similar_movie_dict, search = True)
    else:
        return "invalid search string"

@app.route('/movies/')
def movies():
    return "Hi"
# Fetching the recommended movies data and previously watched highly rated movies data for each user.
# It fetches the data based on the user id entered int eh first page
def fetch_data_from_table(userId):
    conn = mysql.connector.Connect(user='root', password='mysql101', host='localhost', database='COEN499')
    data_cursor = conn.cursor()
    old_rating_fetch_query = "SELECT MOVIEID FROM PREV_RATED_MOVIES WHERE USERID = %s"
    data_cursor.execute(old_rating_fetch_query, (userId,))
    data = data_cursor.fetchall()
    movie_dict = {}
    for movie_id in data:
        print("------------------------------")
        print("movie_id_to_search: ", movie_id[0])
        print("------------------------------")
        matched_row = merged_movie_df.loc[merged_movie_df['movieId'] == movie_id[0]]
        movie_dict[movie_id] = (matched_row.values[0][2], matched_row.values[0][3], matched_row.values[0][4], matched_row.values[0][5])

    recommendation_query = "SELECT MOVIEID FROM PREDICTIONS WHERE USERID = %s"
    data_cursor.execute(recommendation_query, (userId,))
    pred_data = data_cursor.fetchall()
    movie_pred_dict = {}
    for movie_id in pred_data:
        print("------------------------------")
        print("movie_id_to_search: ", movie_id[0])
        print("------------------------------")
        matched_row = merged_movie_df.loc[merged_movie_df['movieId'] == movie_id[0]]
        movie_pred_dict[movie_id] = (matched_row.values[0][2], matched_row.values[0][3], matched_row.values[0][4])
    # print(movie_dict.items())
    return movie_dict, movie_pred_dict
    data_cursor.close()
    conn.close()


if __name__ == '__main__':
    merged_movie_df, movie_df, url_df, ratings_df = read_files.collect_movie_data()
    app.run(debug=True)

