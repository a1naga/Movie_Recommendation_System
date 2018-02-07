# This program predicts the ratings for movies that are not watched/rated by the users based on their
# previous ratings and stores the high rating predictions in a mysql table.
import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
import mysql.connector
from type_convertor_mysql import NumpyMySQLConverter
import read_files

def recommendation(svd_applied_ratings_df, userId, movie_df, ratings_df,recommendations_count=6):
    u_row_num = userId - 1
    # Get and sort the user's predictions
    sorted_predicted_ratings = svd_applied_ratings_df.iloc[u_row_num].sort_values(ascending=False)
    # Get the users_Data and merge it with the movie info
    user_values = ratings_df[ratings_df.userId == (userId)]
    merge_user_movie = (user_values.merge(movie_df, how='left', left_on ='movieId', right_on = 'movieId').
                        sort_values(['rating'], ascending=False))

    print("user: {0} has already rated {1} movies ".format(userId, merge_user_movie.shape[0]))
    print("Recommending the highest {0} predicted ratings for movies that are not already watched by user: {1}".format(recommendations_count, userId))

    # Recommend the highest predicted rating movies that the user hasn't watched yet
    recommendations = (movie_df[~movie_df['movieId'].isin(merge_user_movie['movieId'])].
                      merge(pd.DataFrame(sorted_predicted_ratings).reset_index(), how='left', left_on='movieId', right_on='movieId').
                      rename(columns = {u_row_num: 'Predictions'}).
                      sort_values('Predictions', ascending = False).
                      iloc[:recommendations_count, :-1])

    return merge_user_movie, recommendations

def main():
    # Get connection to MySql database
    conn = mysql.connector.connect(user='root', password='mysql101', host='localhost', database='COEN499')
    conn.set_converter_class(NumpyMySQLConverter)
    new_cursor = conn.cursor()
    # read the ratings file into a pandas dataframe

    merged_movie_df, movie_df, url_df, ratings_df = read_files.collect_movie_data()
    # ratings_df = pd.read_csv("/Users/aarthi/COEN499/Recommendation_system/ml-latest-small/ratings.csv")
    # # ratings_df.head()
    #
    # # Read the movies file into a pandas dataframe
    # movie_df = pd.read_csv("/Users/aarthi/COEN499/Recommendation_system/ml-latest-small/movies.csv", sep=',', encoding="latin-1")
    # # movie_df.head()
    #
    # # Read the links_with_url file, which contains image url and read it into a pandas dataframe
    # image_url_df = pd.read_csv("/Users/aarthi/COEN499/Recommendation_system/ml-latest-small/links_with_url.csv")
    # image_url_df.head()

    # make a pivot table from ratings_df with userId as index and movieId as columns. Also, fill all Nan's as 0.
    ratings_pivot = ratings_df.pivot(index = 'userId', columns='movieId', values='rating').fillna(0)
    ratings_pivot.head()

    # Normalise the ratings_pivot dataframe by subtracting the average rating of user
    ratings_pivot_matrix = ratings_pivot.as_matrix()
    user_ratings_mean = np.mean(ratings_pivot_matrix, axis = 1)
    ratings_normalized = ratings_pivot_matrix - user_ratings_mean.reshape(-1, 1)

    # Singular Value Decompostion for prediction of ratings imported from python scipy sparse library
    U, sigma, Vt = svds(ratings_normalized, k=50)

    # Make the sigma into a diagonal matrix
    sigma = np.diag(sigma)

    # multiply the decomposed matrices
    matrix_merging = np.dot(np.dot(U,sigma),Vt)

    # Add the Average ratings to get back the original rating norm
    denormalized = matrix_merging + user_ratings_mean.reshape(-1,1)

    # Make the matrix into a pandas dataframe with the index as
    # ratings_pivot index (userId) and columns as ratings_pivot columns(MovieId)
    svd_applied_ratings_df = pd.DataFrame(denormalized, columns=ratings_pivot.columns)

    # The resultant predicted rating values for the original sparse matrix
    # svd_applied_ratings_df.head()

    user_list = ratings_df['userId'].unique()
    count = 0
    for user in user_list:
        previously_rated, new_predictions = recommendation(svd_applied_ratings_df, int(user), movie_df, ratings_df, 10)
        old_rating_ctr = 0
        for index, row in previously_rated.iterrows():
            # This counter is to insert only top 5 highly rated previosuly watched movies by the user
            old_rating_ctr += 1
            if old_rating_ctr <= 5:
                query1 = "INSERT INTO PREV_RATED_MOVIES(USERID, MOVIEID, RATING) VALUES (%s, %s, %s)"
                new_cursor.execute(query1, (row['userId'], row['movieId'], row['rating']))
            else:
                break
        for index, row in new_predictions.iterrows():
            query2 = "INSERT INTO PREDICTIONS(USERID, MOVIEID) VALUES (%s, %s)"
            new_cursor.execute(query2, (user, row['movieId']))
        count += 1
        # print the total number of records inserted into db for every 100 records
        if (count % 100) == 0:
            print("Inserted " + str(count) + " user records")
    new_cursor.execute("COMMIT")
    new_cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
# print(previously_rated.head())       
#                                      
# print(new_predictions)               

