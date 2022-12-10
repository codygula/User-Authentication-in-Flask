from boto3 import resource
from boto3.dynamodb.conditions import Key
import time

# THIS ACTUALLY WORKS!!! Stolen from https://stackoverflow.com/questions/53935211/query-all-items-by-partition-key-in-dynamo-using-boto3


dynamodb_resource = resource('dynamodb')
searchdatabase = dynamodb_resource.Table("searchItems")

def query_table(table_name, key=None, value=None):
    table = dynamodb_resource.Table(table_name)

    if key is not None and value is not None:
        filtering_exp = Key(key).eq(value)
        return table.query(KeyConditionExpression=filtering_exp)

    raise ValueError('Parameters missing or invalid')



def put_info(email, site, searchterm):
    response = searchdatabase.put_item(
            Item={
                'email': email,
                'ItemNumber': int(time.time()),
                'siteURL': site,
                'searchterm': searchterm,
                })
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    print(status_code)
    print(response) 


def delete_info(email, itemnumber):
    response = searchdatabase.delete_item(
        Key={
            'email': email,
            'ItemNumber': itemnumber
        }
    )
    
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    print(status_code)




# if __name__ == '__main__':
#     response = delete_info('222222', 1670174184)
#     print('resp = ', response)
  

