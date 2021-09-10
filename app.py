import sqlite3
import datetime
import logging
import sys

from flask import Flask, render_template, request, url_for, redirect, flash


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    update_db_connection_count(connection)
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


def update_db_connection_count(connection):
    query = None
    try:
        # get current count in db
        current_metric_value = get_db_connection_count(connection)
        # add one
        new_metric_value = current_metric_value + 1
        # update value
        current_date_time = datetime.datetime.now()
        query = 'UPDATE metrics SET value = ?, last_updated = ? WHERE name = ?'
        metric_name = 'db_connection_count'
        connection.execute(query, (new_metric_value, current_date_time, metric_name))
        connection.commit()
    except Exception as err:
        current_date_time = datetime.datetime.now()
        app.logger.info('%s, Query Failed: %s\nError: %s' % (current_date_time.strftime('%m/%d/%Y, %H:%M:%S'),
                                                             query, str(err)))

        # print('Query Failed: %s\nError: %s' % (query, str(err)))


def get_db_connection_count(connection):
    metric_name = 'db_connection_count'
    query = 'SELECT value FROM metrics WHERE name = ?'
    db_connection_count = int(connection.execute(query, (metric_name,)).fetchone()[0])
    return db_connection_count


def get_post_count(connection):
    query = 'SELECT COUNT(*) FROM posts'
    post_count = int(connection.execute(query).fetchone()[0])
    return post_count


def update_post_count(connection, post_count):
    query = None
    try:
        current_date_time = datetime.datetime.now()
        query = 'UPDATE metrics SET value = ?, last_updated = ? WHERE name = ?'
        metric_name = 'post_count'
        connection.execute(query, (post_count, current_date_time, metric_name))
        connection.commit()
    except Exception as err:
        current_date_time = datetime.datetime.now()
        app.logger.info('%s, Query Failed: %s\nError: %s' % ((current_date_time.strftime('%m/%d/%Y, %H:%M:%S'),
                                                              query, str(err))))
        print('Query Failed: %s\nError: %s' % (query, str(err)))


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['DEBUG'] = False


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    update_db_connection_count(connection)
    posts = connection.execute('SELECT * FROM posts ORDER BY created DESC').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        current_date_time = datetime.datetime.now()
        app.logger.info("%s, A non-existing article accessed and the 404 page returned" % (current_date_time.strftime('%m/%d/%Y, %H:%M:%S')))
        return render_template('404.html'), 404
    else:
        current_date_time = datetime.datetime.now()
        app.logger.info('%s, Article "%s" retrieved!' % (current_date_time.strftime('%m/%d/%Y, %H:%M:%S'),
                                                         str(post['title'])))
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    current_date_time = datetime.datetime.now()
    app.logger.info('%s, "About Us" page retrieved!' % (current_date_time.strftime('%m/%d/%Y, %H:%M:%S')))
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            update_db_connection_count(connection)
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            current_date_time = datetime.datetime.now()
            app.logger.info('%s, Article "%s" Created!' % (current_date_time.strftime('%m/%d/%Y, %H:%M:%S'), str(title)))
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route("/healthz")
def healthCheck():
    response = {'result': 'OK - healthy'}
    current_date_time = datetime.datetime.now()
    app.logger.info('%s, Status request successful' % (current_date_time.strftime('%m/%d/%Y, %H:%M:%S')))
    return response, 200


@app.route("/metrics")
def metrics():
    connection = None
    try:
        connection = get_db_connection()
        update_db_connection_count(connection)
        db_connection_count = get_db_connection_count(connection)
        post_count = get_post_count(connection)
        update_post_count(connection, post_count)
        response = {'db_connection_count': db_connection_count, 'post_count': post_count}
        current_date_time = datetime.datetime.now()
        app.logger.info('%s, Metrics request successful' % (current_date_time.strftime('%m/%d/%Y, %H:%M:%S')))
        return response, 200
    except Exception as err:
        current_date_time = datetime.datetime.now()
        app.logger.info('%s, %s' % (current_date_time.strftime('%m/%d/%Y, %H:%M:%S'), str(err)))
        print(err)
    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    # stream logs to app.log file and console
    logging.basicConfig(level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[
                            logging.StreamHandler(sys.stdout),
                            logging.StreamHandler(sys.stderr)
                            # ,logging.FileHandler('logs/app.log')
                        ])

    # start the application on port 3111
    app.run(host='0.0.0.0', port='3111')
