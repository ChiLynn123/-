import os

import psycopg2

def csv_export(t_path_n_file):
    querystr = "select url_id, html_origin_content from guangxi_1_url_content_1104"

    # set up our database connection.
    conn = psycopg2.connect(
        dbname="postgres", user="zlj", password="123", host="10.1.203.15", port="15435",
    )
    db_cursor = conn.cursor()
    # Use the COPY function on the SQL we created above.
    SQL_for_file_output = "COPY ({0}) TO STDOUT WITH CSV HEADER FORCE QUOTE *".format(
        querystr
    )
    # Trap errors for opening the file
    with open(t_path_n_file, "w") as f_output:
        try:
            db_cursor.copy_expert(SQL_for_file_output, f_output)
        except psycopg2.Error as error:
            print(error)
    # Success!
    # Clean up: Close the database cursor and connection
    db_cursor.close()
    conn.close()
    # Send the user on to some kind of informative screen.

if __name__ == "__main__":
    csv_export("./data/guangxi_1_url_content_1104.csv")
