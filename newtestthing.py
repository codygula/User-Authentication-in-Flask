import boto3
from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash


dbclient = boto3.resource("dynamodb")
searchdatabase = dbclient.Table("searchItems")
AuthTable = dbclient.Table("email_list")
            
            
            
user = "codygula@yahoo.com"
password = "888888888"
# print(user)

response = AuthTable.get_item(
    TableName="email_list",
    Key={
        "email": user
    })
# dbemail = response['Item']['email']
dbpassword = response['Item']['passwordhash']
print('dbpassword = ', type(dbpassword))
print('password = ', password)


if check_password_hash(dbpassword, password):
# if dbpassword == password:

    print("logging in!!!!!!!!!!!!")
    
else:
    print("check pasword failed")

