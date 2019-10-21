import json
import os
import uuid
from datetime import datetime

import boto3
import requests


def user_create(event, context):
    user_table = boto3.resource('dynamodb').Table(os.environ['USER_TABLE'])
    wallet_table = boto3.resource('dynamodb').Table(os.environ['WALLET_TABLE'])
    body = json.loads(event['body'])

    print('request_body: ', body)

    user_table.put_item(
        Item={
            'id': body['id'],
            'name': body['name']
        }
    )
    wallet_table.put_item(
        Item={
            'id': str(uuid.uuid4()),
            'userId': body['id'],
            'amount': 0,
            'totalChargeAmount': 0,
            'totalUseAmount': 0
        }
    )

    response = {
        'statusCode': 200,
        'body': json.dumps({'result': 'ok'})
    }
    print('res: ', response)

    return response


def wallet_charge(event, context):
    wallet_table = boto3.resource('dynamodb').Table(os.environ['WALLET_TABLE'])
    history_table = boto3.resource('dynamodb').Table(os.environ['PAYMENT_HISTORY_TABLE'])
    body = json.loads(event['body'])

    print('request_body: ', body)

    result = _queryWalletByUserId(wallet_table, body['userId'])
    user_wallet = result['Items'].pop()

    res = wallet_table.update_item(
        Key={
            'id': user_wallet['id']
        },
        UpdateExpression="ADD amount :val",
        ExpressionAttributeValues={
                    ':val': body['chargeAmount']
        },
        ReturnValues="UPDATED_NEW"
    )
<<<<<<< HEAD
    
    wallet_table.update_item(
        Key={
            'id': user_wallet['id']
        },
        UpdateExpression="ADD totalChargeAmount :val",
        ExpressionAttributeValues={
                    ':val': body['chargeAmount']
        },
        ReturnValues="UPDATED_NEW"
    )
    
    wallet_table.update_item(
        Key={
            'id': user_wallet['id']
        },
        UpdateExpression="ADD loccount_%s :val" % (body['locationId']),
        ExpressionAttributeValues={
                    ':val': 1
        },
        ReturnValues="UPDATED_NEW"
    )
    
=======


>>>>>>> 1b586111c73704395e50f082f7bc2c6b85997176
    history_table.put_item(
        Item={
            'walletId': user_wallet['id'],
            'transactionId': body['transactionId'],
            'chargeAmount': body['chargeAmount'],
            'locationId': body['locationId'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )
    requests.post(os.environ['NOTIFICATION_ENDPOINT'], json={
        'transactionId': body['transactionId'],
        'userId': body['userId'],
        'chargeAmount': body['chargeAmount'],
        'totalAmount': int(res['Attributes']['amount'])
    })

    # offload to sqs
    obj = {
        'transactionId': body['transactionId'],
        'userId': body['userId'],
        'chargeAmount': body['chargeAmount'],
        'totalAmount': int(res['Attributes']['amount'])
    }
    _send_message_to_sqs(obj)

    response = {
        'statusCode': 202,
        'body': json.dumps({'result': 'Assepted. Please wait for the notification.'})
    }
    print('res: ', response)

    return response


def wallet_use(event, context):
    wallet_table = boto3.resource('dynamodb').Table(os.environ['WALLET_TABLE'])
    history_table = boto3.resource('dynamodb').Table(os.environ['PAYMENT_HISTORY_TABLE'])
    body = json.loads(event['body'])

    print('requesr_body: ', body)

    result = _queryWalletByUserId(wallet_table, body['userId'])
    user_wallet = result['Items'].pop()

    total_amount = user_wallet['amount'] - body['useAmount']
    if total_amount < 0:
        return {
            'statusCode': 400,
            'body': json.dumps({'errorMessage': 'There was not enough money.'})
        }

    res = wallet_table.update_item(
        Key={
            'id': user_wallet['id']
        },
        UpdateExpression="ADD amount :val",
        ExpressionAttributeValues={
                    ':val': -body['useAmount']
        },
        ReturnValues="UPDATED_NEW"
    )
<<<<<<< HEAD
    wallet_table.update_item(
        Key={
            'id': user_wallet['id']
        },
        UpdateExpression="ADD totalUseAmount :val",
        ExpressionAttributeValues={
                    ':val': body['useAmount']
        },
        ReturnValues="UPDATED_NEW"
    )
    
    
    wallet_table.update_item(
        Key={
            'id': user_wallet['id']
        },
        UpdateExpression="ADD loccount_%s :val" % (body['locationId']),
        ExpressionAttributeValues={
                    ':val': 1
        },
        ReturnValues="UPDATED_NEW"
    )
    
=======

>>>>>>> 1b586111c73704395e50f082f7bc2c6b85997176
    history_table.put_item(
        Item={
            'walletId': user_wallet['id'],
            'transactionId': body['transactionId'],
            'useAmount': body['useAmount'],
            'locationId': body['locationId'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )
    requests.post(os.environ['NOTIFICATION_ENDPOINT'], json={
        'transactionId': body['transactionId'],
        'userId': body['userId'],
        'useAmount': body['useAmount'],
        'totalAmount': int(res['Attributes']['amount'])
    })

    # offload to sqs
    obj = {
        'transactionId': body['transactionId'],
        'userId': body['userId'],
        'useAmount': body['useAmount'],
        'totalAmount': int(res['Attributes']['amount'])
    }
    _send_message_to_sqs(obj)

    response = {
        'statusCode': 202,
        'body': json.dumps({'result': 'Assepted. Please wait for the notification.'})
    }
    print('res: ', response)

    return response


def wallet_transfer(event, context):
    wallet_table = boto3.resource('dynamodb').Table(os.environ['WALLET_TABLE'])
    history_table = boto3.resource('dynamodb').Table(os.environ['PAYMENT_HISTORY_TABLE'])
    body = json.loads(event['body'])

    print('requesr_body: ', body)

    from_wallet = _queryWalletByUserId(wallet_table, body['fromUserId']).get('Items').pop()
    to_wallet = _queryWalletByUserId(wallet_table, body['toUserId']).get('Items').pop()

    from_total_amount = from_wallet['amount'] - body['transferAmount']
    to_total_amount = to_wallet['amount'] + body['transferAmount']
    if from_total_amount < 0:
        return {
            'statusCode': 400,
            'body': json.dumps({'errorMessage': 'There was not enough money.'})
        }

    res = wallet_table.update_item(
        Key={
            'id': from_wallet['id']
        },
        UpdateExpression="ADD amount :val",
        ExpressionAttributeValues={
                    ':val': -body['transferAmount']
        },
        ReturnValues="UPDATED_NEW"
    )
    from_total_amount = int(res['Attributes']['amount'])
    res = wallet_table.update_item(
        Key={
            'id': to_wallet['id']
        },
        UpdateExpression="ADD amount :val",
        ExpressionAttributeValues={
                    ':val': body['transferAmount']
        },
        ReturnValues="UPDATED_NEW"
    )
    to_total_amount = int(res['Attributes']['amount'])
    
    wallet_table.update_item(
        Key={
            'id': from_wallet['id']
        },
        UpdateExpression="ADD totalUseAmount :val",
        ExpressionAttributeValues={
                    ':val': body['transferAmount']
        },
        ReturnValues="UPDATED_NEW"
    )
    wallet_table.update_item(
        Key={
            'id': to_wallet['id']
        },
        UpdateExpression="ADD totalChargeAmount :val",
        ExpressionAttributeValues={
                    ':val': body['transferAmount']
        },
        ReturnValues="UPDATED_NEW"
    )
    
    wallet_table.update_item(
        Key={
            'id': from_wallet['id']
        },
        UpdateExpression="ADD loccount_%s :val" % body['locationId'],
        ExpressionAttributeValues={
                    ':val': 1
        },
        ReturnValues="UPDATED_NEW"
    )
    wallet_table.update_item(
        Key={
            'id': to_wallet['id']
        },
        UpdateExpression="ADD loccount_%s :val" % body['locationId'],
        ExpressionAttributeValues={
                    ':val': 1
        },
        ReturnValues="UPDATED_NEW"
    )
    
    


    history_table.put_item(
        Item={
            'walletId': from_wallet['id'],
            'transactionId': body['transactionId'],
            'useAmount': body['transferAmount'],
            'locationId': body['locationId'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )
    history_table.put_item(
        Item={
            'walletId': to_wallet['id'],
            'transactionId': body['transactionId'],
            'chargeAmount': body['transferAmount'],
            'locationId': body['locationId'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )
    requests.post(os.environ['NOTIFICATION_ENDPOINT'], json={
        'transactionId': body['transactionId'],
        'userId': body['fromUserId'],
        'useAmount': body['transferAmount'],
        'totalAmount': int(from_total_amount),
        'transferTo': body['toUserId']
    })

    # offload to sqs
    obj = {
        'transactionId': body['transactionId'],
        'userId': body['fromUserId'],
        'useAmount': body['transferAmount'],
        'totalAmount': int(from_total_amount),
        'transferTo': body['toUserId']
    }
    _send_message_to_sqs(obj)

    requests.post(os.environ['NOTIFICATION_ENDPOINT'], json={
        'transactionId': body['transactionId'],
        'userId': body['toUserId'],
        'chargeAmount': body['transferAmount'],
        'totalAmount': int(to_total_amount),
        'transferFrom': body['fromUserId']
    })

    # offload to sqs
    obj = {
        'transactionId': body['transactionId'],
        'userId': body['toUserId'],
        'chargeAmount': body['transferAmount'],
        'totalAmount': int(to_total_amount),
        'transferFrom': body['fromUserId']
    }
    _send_message_to_sqs(obj)

    response = {
        'statusCode': 202,
        'body': json.dumps({'result': 'Assepted. Please wait for the notification.'})
    }
    print('res: ', response)

    return response


def get_user_summary(event, context):
    wallet_table = boto3.resource('dynamodb').Table(os.environ['WALLET_TABLE'])
    user_table = boto3.resource('dynamodb').Table(os.environ['USER_TABLE'])
    history_table = boto3.resource('dynamodb').Table(os.environ['PAYMENT_HISTORY_TABLE'])
    params = event['pathParameters']
    user = user_table.get_item(
        Key={'id': params['userId']}
    )
    
    wallet = wallet_table.scan(
        ScanFilter={
            'userId': {
                'AttributeValueList': [
                    params['userId']
                ],
                'ComparisonOperator': 'EQ'
            }
        }
    ).get('Items').pop()


    loccount = {}
    for k in wallet:
        if k.startswith("loccount_"):
            t = k[9:]
            loccount[_get_location_name(t)] = int(wallet[k])

    response = {
        'statusCode': 200,
        'body': json.dumps({
            'userName': user['Item']['name'],
            'currentAmount': int(wallet['amount']),
            #'totalChargeAmount': int(sum_charge),
            #'totalUseAmount': int(sum_payment),
            #'timesPerLocation': times_per_location
            'totalChargeAmount': int(wallet['totalChargeAmount']),
            'totalUseAmount': int(wallet['totalUseAmount']),
            'timesPerLocation': loccount,
        })
    }
    print('res: ', response)

    return response


def get_payment_history(event, context):
    wallet_table = boto3.resource('dynamodb').Table(os.environ['WALLET_TABLE'])
    history_table = boto3.resource('dynamodb').Table(os.environ['PAYMENT_HISTORY_TABLE'])
    params = event['pathParameters']

    wallet = _queryWalletByUserId(wallet_table, params['userId']).get('Items').pop()

    payment_history_result = history_table.scan(
        ScanFilter={
            'walletId': {
                'AttributeValueList': [
                    wallet['id']
                ],
                'ComparisonOperator': 'EQ'
            }
        }
    )

    payment_history = []
    for p in payment_history_result['Items']:
        if 'chargeAmount' in p:
            p['chargeAmount'] = int(p['chargeAmount'])
        if 'useAmount' in p:
            p['useAmount'] = int(p['useAmount'])
        p['locationName'] = _get_location_name(p['locationId'])
        del p['locationId']
        payment_history.append(p)

    sorted_payment_history = list(sorted(
        payment_history,
        key=lambda x:x['timestamp'],
        reverse=True))

    response = {
        'statusCode': 200,
        'body': json.dumps(sorted_payment_history)
    }
    print('res: ', response)

    return response


def _queryWalletByUserId(table, userId):
    return table.query(
        IndexName='userId-index',
        KeyConditionExpression='#k = :val',
        ExpressionAttributeNames={
            '#k': 'userId'
        },
        ExpressionAttributeValues={
            ':val': userId
        }
    )


def _get_location_name(location_id):
    import os
    import os.path
    import json
    TMPFILE = "/tmp/location.json"
    if (os.path.exists(TMPFILE)):
        locations = json.loads(open(TMPFILE, "r").read())
    else:
        locations = requests.get(os.environ['LOCATION_ENDPOINT']).json()
        open(TMPFILE, "w").write(json.dumps(locations))
    return locations[str(location_id)]


def _send_message_to_sqs(data):
    sqs = boto3.client('sqs')
    q_url = os.environ['QUEUE_URL']

    # data = {
    #     'transactionId': '1',
    #     'userId': '2',
    #     'chargeAmount': '3',
    #     'totalAmount': '4'
    # }

    response = sqs.send_message(
        QueueUrl=q_url,
        DelaySeconds=0,
        MessageBody=(
            json.dumps(data)
        )
    )

    print(response)
