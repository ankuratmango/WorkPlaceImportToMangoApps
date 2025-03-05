import os

class Constants():

    def __init__(self):
        pass
    current_directory = os.getcwd()
    META_ACCESS_TOKEN = "DQWRLZA29QUVprNDNaZAjk1d3ZAud2xPT0JmWmZAPVmhacXpXQ0daMGhBQ3YwamhhRU03LUxKNTJWbkdTTGlQWU5OLUtaX2RSOUJBdHJSd19nQWRzaTJWeGY4Y2p3QU95ZAkViZAHkwTGlIX3BUWmNkdnktRnNNUXpCSFFiTTllQVlkczdJNzRES1ByT2psN2pHTG55ekpVV1BHaEFlOW9YcjA0U3hpWGM1U0JIYnA5aFBHR3FZAeWZAlRFZAfTzFMdWdJY19jT0xjdG9xeTJVNDhSWUhjYktB" 
    GRAPH_URL_PREFIX = 'https://graph.workplace.com/'
    FIELDS_CONJ = '?fields='
    CONVERSATIONS_SUFFIX = '/conversations'
    MESSAGES_FIELDS = 'messages{id, created_time,message,to,from,attachments}'
    JSON_KEY_DATA = 'data'
    JSON_KEY_PAGING = 'paging'
    JSON_KEY_NEXT = 'next'
    JSON_KEY_EMAIL = 'email'

    MANGOAPPS_URL = 'https://ankur.engageexpress.com/'
    MANGOAPPS_API_KEY = 'b670ba431addc6d50f84c89a157e1d58a65aeafc'
    MANGOAPPS_USERNAME = 'admin@ankur.com'
    MANGOAPPS_PASSWORD = 'dGVtcDEyMzQ='

    # MANGOAPPS_URL = 'https://ankurqa.mangopulse.com/'
    # MANGOAPPS_API_KEY = 'bdc43dc4a8908ae7a2022c3a7873140b03df8dc6'
    # MANGOAPPS_USERNAME = 'admin@ankurqa.com'

    ALL_USER_DATA = current_directory + "\\importdata\\users.csv"
    ALL_GROUP_DATA = current_directory + "\\importdata\\groups.csv"
    ALL_GROUP_MEMBDER_DATA = current_directory + "\\importdata\\members.csv"
    ALL_MANGO_META_GROUP_ID = current_directory + "\\importdata\\group_meta_mango.csv"
    ALL_MANGO_USER_ID_PSWD = current_directory + "\\importdata\\mango_user_pssd.csv"
    FOLDER_GROUPFEEDS = current_directory + "\\importdata\\groupfeeds"

    DOWNLOAD_FOLDER_META = current_directory + "\\download_file_meta"




