from flask import Flask, request
import random,requests,wget,json,os
from pymessenger.bot import Bot
import urllib.request
import pandas as pd
from haversine import haversine

site='http://flask-env.iir8am5aem.ap-southeast-1.elasticbeanstalk.com/'

app = Flask(__name__)
c_ACCESS_TOKEN='EAADrWWKPR2EBAG8rdlU9ZA5MteZA2ZCtobvV44YJPT3B1522EmjqK53XufVCFTVa8VIU8qnMiU8g7da1RZALEaalQVv4uSaPTxswKSSLnoZCLMYRR7zy6bbu9V0lvXnEVGb8VNOL4CnZASzhaZCqtF4FuC6xcDToPOtTgAkyLNGjYjf16G0o6pv'

VERIFY_TOKEN = 'VERIFY_TOKEN'
bot = Bot(c_ACCESS_TOKEN)



df=pd.read_csv('Hospitals_geotagged.csv',encoding='ISO-8859-1')
df['result']=df.apply(lambda x: (x['lat'],x['lon']),axis=1)





params = (
    ('access_token', c_ACCESS_TOKEN),
)

#data = '{\n  "recipient":{\n    "id":"121"\n  },\n"message":{\n"text": "Here is a quick reply!",\n "quick_replies":[\n {\n "content_type":"text",\n "title":"Test",\n"payload":"test load",\n      }\n    ]\n  }\n}'

#response = requests.post('https://graph.facebook.com/v2.6/me/messages?access_token=EAADrWWKPR2EBAG8rdlU9ZA5MteZA2ZCtobvV44YJPT3B1522EmjqK53XufVCFTVa8VIU8qnMiU8g7da1RZALEaalQVv4uSaPTxswKSSLnoZCLMYRR7zy6bbu9V0lvXnEVGb8VNOL4CnZASzhaZCqtF4FuC6xcDToPOtTgAkyLNGjYjf16G0o6pv', headers=headers, data=data)

db={'address':0,'jpg':0}
with open('db.txt','w') as file:
	file.write(json.dumps(db))

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])

def webook():
 
# endpoint for processing incoming messaging events
	if request.method == 'GET':

		token_sent = request.args.get("hub.verify_token")
		return verify_fb_token(token_sent)
 
	else:

		data = request.get_json()
	 
		if data["object"] == "page":
	 
			for entry in data["entry"]:
				for messaging_event in entry["messaging"]:
					print(messaging_event)
					if messaging_event.get("postback"):
						#print("Post back event activated")
						
			# user clicked/tapped "postback" button in earlier message
			 
						message_text = messaging_event["postback"]["payload"]
						# the button's payload
						 
						# log("Inside postback")
						print(message_text)
						sender_id = messaging_event["sender"]["id"]
						recipient_id=messaging_event["recipient"]["id"]
						print(sender_id,recipient_id)
						if message_text=='FACEBOOK_WELCOME':
							send_message(sender_id,"Hello there! I am a bot and I was built to estimate your BMI and find the nearest hospital")


						if (message_text == "Address"):

							#send_message(sender_id, "Type your address")

							print(sender_id)
							headers = {'Content-Type': 'application/json',}
							#data = '{\n  "recipient":{\n    "id":"2029039910496885"\n  },\n"message":{\n"text": "Please click on the button!",\n "quick_replies":[\n {\n "content_type":"location",\n "title":"Test",\n"payload":"test load",\n}\n]\n  }\n}'
							data = {"recipient":
		{"id":sender_id},"message":
		{"text": "Please click on the button!","quick_replies":
		[{"content_type":"location"}]
		}
		}
							response = requests.post('https://graph.facebook.com/v2.6/me/messages?access_token=EAADrWWKPR2EBAG8rdlU9ZA5MteZA2ZCtobvV44YJPT3B1522EmjqK53XufVCFTVa8VIU8qnMiU8g7da1RZALEaalQVv4uSaPTxswKSSLnoZCLMYRR7zy6bbu9V0lvXnEVGb8VNOL4CnZASzhaZCqtF4FuC6xcDToPOtTgAkyLNGjYjf16G0o6pv', headers=headers, data=json.dumps(data))
							print(sender_id)
						if (message_text=="bmi"):

							'''
							update the data structure; write to a db (address=0, jpg=1)
							'''
							db={'address':0,'jpg':1}
							with open('db.txt','w') as file:
								file.write(json.dumps(db))

							send_message(sender_id, "Please upload your selfie")

						if (message_text=='ok'):
							send_message(sender_id, "Next question asked by api")

						if (message_text=='not ok'):
							send_message(sender_id, "bye!")							

					else:
						# print('this is where you write the condition')
						# print(messaging_event)
						print(request.method)
						if messaging_event.get('message'):
							recipient_id=messaging_event['sender']['id']
							
							db=eval(open('db.txt','r').read())
							print(db.get('jpg'))	

							if messaging_event['message'].get('text'):
								text_message_callback=messaging_event['message'].get('text')
								# if text_message_callback != 'Type your address' and not re.search('BMI',text_message_callback):
								'''
								read content of db here 
								'''
								#db=eval(open('db.txt','r').read())
								### echo is when the flask app sends a message
								if not 'is_echo' in messaging_event.get('message').keys() and db.get('address'):
									'''
									if not echo and latest db record =[address=1 , jpg=0] ; only then write this
									'''
									print(messaging_event.get('message').values())
									hospital=get_address(messaging_event['message'].get('text'))
									send_message(recipient_id,hospital)
									'''
									Reset the records of the database [address=0,jpg=0] and write it back ; conversation completed

									'''
									db={'address':0,'jpg':0}
									with open('db.txt','w') as file:
										file.write(json.dumps(db))
															# if not 'is_echo' in messaging_event.get('message').keys() and :
								else:

									buttons=[{
									"type":"postback",
									"title":"answer question",
									"payload":"ok"
									},
									{"type":"postback",
									"title":"exit diag app",
									"payload":"not ok"
									}
									]
									# bot.send_button_message(recipient_id,"Some question asked from the diag api", buttons)
									data = {"recipient":
									{"id":recipient_id},"message":
									{"text": "The answer from diag api do you want to continue?","quick_replies":
									[{"content_type":"text",
										"title":"yes",
										"payload":"ok"},
										{
										"content_type":"text",
										"title":"no",
										"payload":"not ok"
										}]
									}
									}
									headers = {'Content-Type': 'application/json',}
									response = requests.post('https://graph.facebook.com/v2.6/me/messages?access_token=EAADrWWKPR2EBAG8rdlU9ZA5MteZA2ZCtobvV44YJPT3B1522EmjqK53XufVCFTVa8VIU8qnMiU8g7da1RZALEaalQVv4uSaPTxswKSSLnoZCLMYRR7zy6bbu9V0lvXnEVGb8VNOL4CnZASzhaZCqtF4FuC6xcDToPOtTgAkyLNGjYjf16G0o6pv', headers=headers, data=json.dumps(data))

									# send_message( recipient_id,'Hi, This bot currently allows hospital locator and BMI recognition')

							# else:
								# send_message(recipient_id,'howdy mate!')
			
							if messaging_event['message'].get('attachments') and db.get('jpg'):
								print('bmi')
								'''
								if latest db record=[address=0, jpg=1]
								'''

								db={'address':0,'jpg':0}
								with open('db.txt','w') as file:
									file.write(json.dumps(db))
								if messaging_event['message'].get('attachments')[0].get('type')=='image':		
									file_name=messaging_event['message'].get('attachments')[0]['payload']['url']
								#os.makedirs(os.path.dirname(pic_folder_path+'/'+file_name), exist_ok=True)
									file_download_name=wget.download(file_name)
								#os.rename(file_name,pic_folder_path)
									response=give_ans(file_download_name)
									print("executed bmi")
									send_message(recipient_id, response)
								#send_message(recipient_id,"executed bmi")
								'''
									Reset the records of the database [address=0,jpg=0] and write it back ; conversation completed
								'''	


							if messaging_event['message'].get('attachments'):
								if messaging_event['message'].get('attachments')[0].get('type')=='location':
									

									db={'address':0,'jpg':0}
									with open('db.txt','w') as file:
										file.write(json.dumps(db))

									coords=messaging_event['message'].get('attachments')[0].get('payload').get('coordinates')
									query_location=(coords.get('lat'),coords.get('long'))	
									nearest_hospital=get_hosp(query_location)
									print(nearest_hospital)
									send_message(recipient_id,nearest_hospital )








	return "Message Processed"



def give_ans(file_name):
  f={'image_data':open(file_name,'rb')}
  r=requests.post('http://13.67.65.44:8000/images',files=f,data={'image_ext':'jpg','id':'1234'})
  answer=r.json()
  if answer['Status']=='Failed':
     return 'BMI detector in development!'
  else:
     return "Your BMI is " + answer['BMI']+"  Your Age is in the range of " +answer['Age'] + "  And we detected you as a " + answer['Gender']
  


#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

def get_address(address):
	address=str(address).replace(" ","")
	new_address=site+address
	print(new_address)
	fp = urllib.request.urlopen(new_address)
	json_address= fp.read()
	return (eval(json_address)['name']['0'])

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'
	

def get_hosp(query_location):
	df['query']=df.apply(lambda x: query_location,axis=1)
	df['distance']=df.apply(lambda x: haversine(x['result'],x['query']),axis=1)
	df.sort_values('distance',inplace=True)
	sorted_list=list(df.head(2)['name'])
	return 'Your nearest hospitals are '+  ' and '.join(sorted_list)



if __name__ == "__main__":
    app.run()
	
