from io import StringIO
from sqlalchemy import create_engine, MetaData, Table, Column, BigInteger, Date,  Integer, String
engine = create_engine('postgres://saveliy:S@veliy@ec2-54-225-188-182.compute-1.amazonaws.com:5432/msdb?sslmode=verify-full&sslrootcert=/home/saveliy/.ssh/saveliy-IAM-keypair.pem')

table_name = 'checking'
meta = MetaData()

table_name = Table(
        table_name, meta,
        Column('phone', BigInteger, primary_key = True),
        Column('first_name', String),
                    )

meta.create_all(engine)
