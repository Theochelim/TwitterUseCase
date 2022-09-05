import os
import requests

from google.cloud import bigquery

BEARER_TOKEN = os.getenv('BEARER_TOKEN')

TWITTER_API_URL = 'https://api.twitter.com/2/tweets'

BIGQUERY_PROJECT_NAME = 'empyrean-verve-361519'
BIGQUERY_METRICS_TABLE = 'tweets.metrics'

client = bigquery.Client(project=BIGQUERY_PROJECT_NAME)


def get_recents_tweets():
    """
    Get the latest tweets with #arcane in text

    :return: returns the list of tweet IDs 
    """
    params = {
        'query': '#arcane -is:retweet',
        'max_results':  100
    }

    headers = {
        'Authorization': f"Bearer {BEARER_TOKEN}",
    }

    response = requests.get(
        TWITTER_API_URL + "/search/recent", params=params, headers=headers).json()

    recent_tweets = []
    for tweet in response['data']:
        recent_tweets.append(tweet['id'])

    return recent_tweets


def get_metrics_from_twitter(tweet_id):
    """
    Get some metrics about a tweet

    :param tweet_id: The tweet ID
    :return: returns metrics object or None
    """
    params = {
        'ids': tweet_id,
        'tweet.fields': 'public_metrics',
        'expansions': 'attachments.media_keys',
        'media.fields': 'public_metrics'
    }

    headers = {
        'Authorization': f"Bearer {BEARER_TOKEN}",
    }

    response = requests.get(TWITTER_API_URL, params=params, headers=headers)
    json_data = response.json()

    if response.status_code != 200 or 'data' not in json_data:
        print(f'Unable to get metrics for tweet {tweet_id}')
        return None

    tweet_data = json_data['data'][0]

    metrics = {
        'tweet_id': tweet_id,
        'text': tweet_data['text'],
        'retweet_count': int(tweet_data['public_metrics']['retweet_count']),
        'reply_count': int(tweet_data['public_metrics']['reply_count']),
        'like_count': int(tweet_data['public_metrics']['like_count']),
    }

    if 'includes' in json_data and 'media' in json_data['includes']:
        for media in json_data['includes']['media']:
            if media['type'] == 'video' and 'public_metrics' in media:
                metrics['view_count'] = media['public_metrics']['view_count']
    return metrics


def get_tweets_id():
    """
    Get the IDs list in database to update

    :return: returns IDs list
    """
    query_job = client.query(
        f'SELECT tweet_id FROM {BIGQUERY_METRICS_TABLE}')
    return [result.tweet_id for result in query_job.result()]


def insert_new_tweets(tweets_to_update):
    """
    Insert latest tweets in bigquery database

    :param tweets_to_update: tweet IDs list in databse 
    :return: returns nothing
    """
    rows_to_insert = []
    recent_tweets = get_recents_tweets()

    for tweet_id in recent_tweets:
        if tweet_id not in tweets_to_update:
            metrics = get_metrics_from_twitter(tweet_id)
            rows_to_insert.append(metrics)

    if len(rows_to_insert) > 0:
        errors = client.insert_rows_json(
            f'{BIGQUERY_PROJECT_NAME}.{BIGQUERY_METRICS_TABLE}', rows_to_insert)

        if errors == []:
            print(f'New rows ({len(rows_to_insert)}) have been added.')
        else:
            print("Encountered errors while inserting rows: {}".format(errors))


def update_tweets_metrics(request):
    """
    Update tweet informations in database

    :param request: request (context) of google cloud function call
    :return: returns nothing
    """
    print(request) 
    tweets_to_update = get_tweets_id()

    for tweet_id in tweets_to_update:
        metrics = get_metrics_from_twitter(tweet_id)
        client.query(
            f'''UPDATE {BIGQUERY_METRICS_TABLE}
              SET retweet_count = {metrics["retweet_count"]},
                  reply_count = {metrics["reply_count"]},
                  like_count = {metrics["like_count"]},
              WHERE
                    tweet_id = "{tweet_id}"
               ''')

    insert_new_tweets(tweets_to_update)


update_tweets_metrics(None)
