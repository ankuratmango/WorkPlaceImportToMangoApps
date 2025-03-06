import os
import pandas as pd
import json
import mysql.connector
import glob
from Constants.constants import Constants

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='mangoapps_dev'
)
cursor = db.cursor()
csv_files = glob.glob(os.path.join(Constants.FOLDER_GROUPFEEDS, "*.csv"))
for csv_file in csv_files:
    data = pd.read_csv(csv_file)
    for index, row in data.iterrows():
        feed_id = row['mango_id']
        feed_time = row['meta_time']
        comments_json = row['comments']
    
        update_feed_query = '''
        UPDATE feeds
        SET created_at = %s, updated_at = %s
        WHERE id = %s
        '''
        cursor.execute(update_feed_query, (feed_time, feed_time, feed_id))
    
        if pd.notnull(comments_json):
            comments = json.loads(comments_json)
            update_comment_query = '''
            UPDATE feed_comments
            SET created_at = CASE id
            '''
            update_times = []
            comment_ids = []
            for comment_id, comment_time in comments.items():
                update_comment_query += f'WHEN %s THEN %s ' 
                update_times.extend([comment_id, comment_time])
                comment_ids.append(comment_id)
            update_comment_query += '''
            END,
            updated_at = CASE id
            '''
            for comment_id, comment_time in comments.items():
                update_comment_query += f'WHEN %s THEN %s ' 
                update_times.extend([comment_id, comment_time])
            update_comment_query += '''
            END
            WHERE id IN (%s)
            ''' % ','.join(['%s'] * len(comment_ids))
            if(len(comment_ids) > 0):
                cursor.execute(update_comment_query, update_times + comment_ids)

db.commit()
cursor.close()
db.close()

print('Update completed successfully!')
