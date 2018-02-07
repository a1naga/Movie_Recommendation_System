# To compute the similar gender movies using euclidean distance
import math
import read_files
import pandas as pd


merged_movie_df, movie_df, url_df, ratings_df = read_files.collect_movie_data()
# print(movie_df.columns)
# Convert the genres and into columns and assign binary values to them based on the genres present in each movie
movie_df_new = pd.concat([movie_df,movie_df.genres.str.get_dummies(sep="|")], axis = 1)
# print(movie_df_new.head())
# movie_df_new.columns

# The below encoding was needed in Jupyter ntebook but not here in pycharm
# movie_df_new.columns = [col.encode('ascii', 'ignore') for col in movie_df_new]

# This method calculates the euclidean distances between each movies with other movies based on genres
def euclidean_distance(row, searched_movie):

    distance_columns = ['(no genres listed)', 'Action',
                        'Adventure', 'Animation', 'Children', 'Comedy', 'Crime',
                        'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'IMAX',
                        'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War',
                        'Western']
    inner_value = 0
    for k in distance_columns:
        inner_value += (row[k] - searched_movie[k]) ** 2
    return math.sqrt(inner_value)

# searched_movie_title is from the user entered search string from the userpage.html
def find_similar_movies(searched_movie_title):
    if (movie_df_new['title'].str.contains(searched_movie_title)).sum() > 0:
        searched_movie = movie_df_new[movie_df_new['title'].str.contains(searched_movie_title)].iloc[0]
        searched_movie_id = movie_df.movieId[movie_df['title'] == searched_movie.title]

        # calculate euclidean distance for each row
        searched_movie_distance = movie_df_new.apply(euclidean_distance, args=(searched_movie,), axis=1)
        searched_movie_list = movie_df_new.movieId[movie_df_new['title'].str.contains(searched_movie_title)]
        print("searched_movie_list : ", searched_movie_list.values)

        distance_frame = pd.DataFrame(data={"dist": searched_movie_distance, "idx": searched_movie_distance.index})
        distance_frame.sort_values("dist", inplace=True)

        # Find the most similar movie to the searched movie (the lowest distance to searched movie is itself, so we need to remove it from our list)
        sim_movie_idx = distance_frame.iloc[0:6]["idx"]
        print(sim_movie_idx.values)
        similar_movies_list = []
        # Based on the index get the movie ids corresponding to that index
        for result_index in sim_movie_idx:
            similar_movies_list.append(movie_df_new.loc[int(result_index)]["movieId"])
        # Seperating the searched movie from similar movies
        if searched_movie_id.values[0] in similar_movies_list:
            similar_movies_list.remove(searched_movie_id.values[0])
        searched_movie_dict = {}
        # The searched movies list will be displayed separately in search results
        for val in searched_movie_list.values:
            matched_row = url_df[url_df["movieId"] == val]
            searched_movie_dict[val] = (matched_row.values[0][2], matched_row.values[0][3])
        similar_movie_dict = {}
        #  Similar movies list contains list of similar genre movies to the first movie in the searched movie list
        for movie_id in similar_movies_list:
            #     print(movie_id)
            matched_row = url_df[url_df["movieId"] == movie_id]
            similar_movie_dict[movie_id] = (matched_row.values[0][2], matched_row.values[0][3])
        return searched_movie_dict, similar_movie_dict
    else:
        searched_movie_dict = {}
        similar_movie_dict = {}
        return searched_movie_dict, similar_movie_dict


