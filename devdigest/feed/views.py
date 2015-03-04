from datetime import datetime
import pickle

from flask import request, Blueprint, render_template, url_for, redirect
from flask.ext.paginate import Pagination

import feedparser


feed_blueprint = Blueprint('feed_blueprint', __name__)


def write_to_file(data):
    with open('/home/samuel/work/developer-digest/links.txt', 'wb') as stored_data:
        pickle.dump(data, stored_data)


def read_from_file():
    try:
        with open('/home/samuel/work/developer-digest/links.txt', 'rb') as stored_data:
            return pickle.load(stored_data)
    except IOError:
        return {}


def get_region(host):
    region = host.split(':')[0]
    region = region.split('.')[0]
    return region


@feed_blueprint.route('/')
def list_feeds():
    region = get_region(request.host)
    links = read_from_file().get(region, {})
    sorted_links = sorted(links.items(), key=lambda x: x[1]['date_sort'], reverse=True)

    per_page = 10
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    pagination = Pagination(page=page, total=len(sorted_links), per_page=per_page)
    index_shown = per_page * (page - 1)
    sorted_links = sorted_links[index_shown:index_shown + per_page]

    return render_template('feed/list.html',
                           links=sorted_links,
                           pagination=pagination,
                           region=region,
                           add_feed_url=url_for('feed_blueprint.add_feed'))


@feed_blueprint.route('/add-feed', methods=['POST', 'GET'])
def add_feed():
    if request.method == 'POST':
        links = read_from_file()
        request.form['author']

        parsed = feedparser.parse(request.form['feed-link'])
        region = get_region(request.host)
        for entry in parsed.entries:
            try:
                author = entry.author
            except AttributeError:
                author = request.form['author']

            try:
                published_parsed = entry.published_parsed
            except AttributeError:
                published_parsed = entry.updated_parsed

            if not links.get(region):
                links[region] = {}

            links[region][entry.id] = {
                'title': entry.title,
                'author': author,
                'link': entry.link,
                'published': datetime(published_parsed.tm_year, published_parsed.tm_mon, published_parsed.tm_mday).strftime('%b %d, %Y'),
                'date_sort': published_parsed
            }
        write_to_file(links)
        return redirect(url_for('feed_blueprint.list_feeds'))

    return render_template('feed/add_feed.html', )
