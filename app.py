# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import Flask, jsonify, request, render_template
from pprint import pprint
import boto3
from botocore.exceptions import ClientError
import os
import json
import uuid

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb',region_name=os.environ['AWS_REGION'])
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=os.environ['AWS_REGION'])
table = dynamodb.Table(os.environ['DDB_TABLE'])


def get_movie(title, year):
    try:
        response = table.get_item(Key={'year': year, 'title': title})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


def delete_movie(title, year):
    try:
        response = table.delete_item(Key={'year': year, 'title': title})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response

#Home Page
@app.route('/')
def home():
  return render_template('index.html')

#AI Agent Chat
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Message is required.'}), 400

    session_id = data.get('session_id') or str(uuid.uuid4())
    
    try:
        response = bedrock_agent.invoke_agent(
            agentid = os.environ['BEDROCK_AGENT_ID'],
            agentAliess = os.environ['BEDROCK_AGENT_ALIAS'],
            sessionId = session_id,
            inputText = user_message
        )

        assistant_reply = ''
        for event in response.get("completion", []):
                if "chunk" in  event and "bytes" in event["chunk"]:
                    assistant_reply += event["chunk"]["bytes"].decode('utf-8')
    
        return jsonify({
            'reply': assistant_reply,
            'session_id': session_id 
        })

    except Exception as e:
        int("Error invoking agent:", e)
        return jsonify({"error": "Failed to call Bedrock Agent"}), 500

# POST /api/movie data: {name:}
@app.route('/api/movie', methods=['POST'])
def post_movie():
    request_data = request.get_json()
    try:
      plot = request_data['info']['plot']
    except:
      plot = "NA"
    try:
      actors = request_data['info']['actors'] 
    except:
      actors = ["NA"]
    try:
      release_date = request_data['info']['release_date']
    except:
      release_date = "NA"
    try:
      genres = request_data['info']['genres']
    except:
      genres = ["NA"]
    try:
      image_url = request_data['info']['image_url']
    except:
      image_url = "NA"
    try:
      directors = request_data['info']['directors'] 
    except:
      directors = ["NA"]
    try:
      rating = request_data['info']['rating'] 
    except:
      rating = 0
    try:
      rank = request_data['info']['rank']
    except:
      rank = 0
    try:
      running_time_secs = request_data['info']['running_time_secs']
    except:
      running_time_secs = 0
    response = table.put_item(
       Item={
            'year': request_data['year'],
            'title': request_data['title'],
            'info': {
                'plot': plot,
                'rating': rating,
                'actors': actors,
                'release_date': release_date,
                'genres' : genres,
                'image_url': image_url,
                'directors': directors,
                'rank': rank,
                'running_time_secs': running_time_secs
            }
        }
    )
    return response

# PUT /api/movie data: {name:}
@app.route('/api/movie', methods=['PUT'])
def put_movie():
    request_data = request.get_json()
    try:
      plot = request_data['info']['plot']
    except:
      plot = "NA"
    try:
      actors = request_data['info']['actors'] 
    except:
      actors = ["NA"]
    try:
      release_date = request_data['info']['release_date']
    except:
      release_date = "NA"
    try:
      genres = request_data['info']['genres']
    except:
      genres = ["NA"]
    try:
      image_url = request_data['info']['image_url']
    except:
      image_url = "NA"
    try:
      directors = request_data['info']['directors'] 
    except:
      directors = ["NA"]
    try:
      rating = request_data['info']['rating'] 
    except:
      rating = 0
    try:
      rank = request_data['info']['rank']
    except:
      rank = 0
    try:
      running_time_secs = request_data['info']['running_time_secs']
    except:
      running_time_secs = 0
    response = table.put_item(
       Item={
            'year': request_data['year'],
            'title': request_data['title'],
            'info': {
                'plot': plot,
                'rating': rating,
                'actors': actors,
                'release_date': release_date,
                'genres' : genres,
                'image_url': image_url,
                'directors': directors,
                'rank': rank,
                'running_time_secs': running_time_secs
            }
        }
    )
    return response

# GET /api/movie?year=<integer>&title=<string>
@app.route('/api/movie')
def get():
    query_params = request.args.to_dict(flat=False)
    year = int(query_params['year'][0])
    title = str(query_params['title'][0])
    response = get_movie(title, year)
    if (response['ResponseMetadata']['HTTPStatusCode'] == 200):
       if ('Item' in response):
           return { 'Item': str(response['Item']) }
       return { 'msg' : 'Item not found!' }
    return { 
       'msg': 'error occurred',
       'response': response
    }

# Delete /api/movie
@app.route('/api/movie', methods=['DELETE'])
def del_movie():
   query_params = request.args.to_dict(flat=False)
   year = int(query_params['year'][0])
   title = str(query_params['title'][0])
   response = delete_movie(title, year)
   if (response['ResponseMetadata']['HTTPStatusCode'] == 200):
       return {
           'msg': 'Delete successful',
       }
   return { 
       'msg': 'error occurred',
       'response': response
   }

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=8080)
