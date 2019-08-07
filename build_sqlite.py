import sqlite3


def connect_to_db(db_name):
    """Check if db_name exists using uri lookup and create it if it 
    does not exist. Then return a connection to the db.
    
    :param db_name: name of db
    :type db_name: connection to db
    """
    uri = 'file:{}?mode=rw'.format(db_name)
    if db_name.lower().endswith(('.db', '.sqlite3')):
        try:
            conn = sqlite3.connect(uri, uri=True)
            print('{} was found. Connecting to {}.'.format(db_name, db_name))
        except sqlite3.OperationalError:
            conn = sqlite3.connect(db_name)
            print('{} was NOT found. Creating and connecting to {}.'.format(
                db_name, db_name))
    else:
        conn = None
        print('Please provide valid file name.')
    return conn


# define schema and create table
def build_transcript_table(cursor):
    cursor.execute("""
        CREATE TABLE transcripts (
            Statement_number,
            Speaker,
            Timestamp,
            Statement,
            Speaker_type,
            Night,
            Debate,
            PRIMARY KEY (Statement_number, Night, Debate)
        )
    """)


# call each build table function here
def main():
    conn = connect_to_db("dem_debate.db")
    cursor = conn.cursor()
    build_transcript_table(cursor)


if __name__ == '__main__':
    main()
