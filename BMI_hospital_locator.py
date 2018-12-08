from flask import Flask, request
import requests,wget,json,os
from pymessenger.bot import Bot
import urllib.request
import pandas as pd
from haversine import haversine

# site='http://flask-env.iir8am5aem.ap-southeast-1.elasticbeanstalk.com/'

app = Flask(__name__)
# c_ACCESS_TOKEN='EAADrWWKPR2EBAG8rdlU9ZA5MteZA2ZCtobvV44YJPT3B1522EmjqK53XufVCFTVa8VIU8qnMiU8g7da1RZALEaalQVv4uSaPTxswKSSLnoZCLMYRR7zy6bbu9V0lvXnEVGb8VNOL4CnZASzhaZCqtF4FuC6xcDToPOtTgAkyLNGjYjf16G0opv'
c_ACCESS_TOKEN='EAADrWWKPR2EBAJcorxLoOdI8lldETu3EXY54hrOZAzMRNFHvORM9B3tTHC1zIa4gZBTYmJnuw1hd34BZCeRiBPRFag3eEx5dUEhMmROjLqzQ24xt1ZCl2aItZCEyeGvrxjMVgRR2ikWTDFYNBWgNxNPmXzZClWkcqDYcJYuNqHBZBrlgApy7tJU'
VERIFY_TOKEN = 'VERIFY_TOKEN'
bot = Bot(c_ACCESS_TOKEN)



hospital_data=pd.read_csv('Hospitals_geotagged.csv',encoding='ISO-8859-1')
hospital_data['result']=hospital_data.apply(lambda x: (x['lat'],x['lon']),axis=1)

def DBrw(address,image):
	db={'address':address,'image':image}
	with open('db.txt','w') as file:
		file.write(json.dumps(db))	


def give_ans_bmi(file_name):
  f={'image_data':open(file_name,'rb')}
  r=requests.post('http://13.67.65.44:8000/images',files=f,data={'image_ext':'jpg','id':'1234'})
  answer=r.json()
  try:
  	if answer['Status']=='Failed':
  		return 'BMI detector in development!'
  	else:
  		return "Your BMI is " + answer['BMI']+"  Your Age is in the range of " +answer['Age'] + "  And we detected you as a " + answer['Gender']
  except:
  	return "404 error"


def quickreply(id,text,qr_payload):
	params = (('access_token', c_ACCESS_TOKEN),)
	data = {"recipient":{"id":id},
			"message":{"text": text,"quick_replies":qr_payload }}
	headers = {'Content-Type': 'application/json',}
	requests.post('https://graph.facebook.com/v2.6/me/messages?access_token=EAADrWWKPR2EBAG8rdlU9ZA5MteZA2ZCtobvV44YJPT3B1522EmjqK53XufVCFTVa8VIU8qnMiU8g7da1RZALEaalQVv4uSaPTxswKSSLnoZCLMYRR7zy6bbu9V0lvXnEVGb8VNOL4CnZASzhaZCqtF4FuC6xcDToPOtTgAkyLNGjYjf16G0o6pv', headers=headers, data=json.dumps(data))


#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'
	

def get_hosp(query_location):
	hospital_data['query']=hospital_data.apply(lambda x: query_location,axis=1)
	hospital_data['distance']=hospital_data.apply(lambda x: haversine(x['result'],x['query']),axis=1)
	hospital_data.sort_values('distance',inplace=True)
	sorted_list=list(hospital_data.head(2)['name'])
	return 'Your nearest hospitals are '+  ' and '.join(sorted_list)

### Initialise the db at 0
DBrw(address=0,image=0)

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
			
						print(message_text)
						sender_id = messaging_event["sender"]["id"]
						recipient_id=messaging_event["recipient"]["id"]
						print(sender_id,recipient_id)
						if message_text=='FACEBOOK_WELCOME':
							send_message(sender_id,"Hello there! I am a bot and I was built to estimate your BMI and find the nearest hospital")


						if message_text=='menu':
							buttons=[{"type":"postback","title":"BMI Indicator","payload":"bmi"},
									{"type":"postback",	"title":"Get nearest hospital","payload":"Address"}
									]
							message="Hi! We currently provide you these two services \nPlease select one to continue"		
							bot.send_button_message(sender_id,message,buttons)

						if (message_text == "Address"):
					
							quickreply(id=sender_id,text='Please click on the button!',qr_payload=[{"content_type":"location"}])

						if (message_text=="bmi"):

							DBrw(address=0,image=1)

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
							print(db.get('image'))	

							if messaging_event['message'].get('text'):
								text_message_callback=messaging_event['message'].get('text')
								# if text_message_callback != 'Type your address' and not re.search('BMI',text_message_callback):
								'''
								read content of db here 
								'''
								#db=eval(open('db.txt','r').read())
								### echo is when the flask app sends a message
								print(text_message_callback)
								if not 'is_echo' in messaging_event.get('message').keys():
									print(messaging_event.get('message').keys())
									send_message( recipient_id,'Hi, This bot currently allows hospital locator and BMI recognition')

									
								# else:

								# 	data = {"recipient":
								# 	{"id":recipient_id},"message":
								# 	{"text": "The answer from diag api do you want to continue?","quick_replies":
								# 	[{"content_type":"text",
								# 		"title":"yes",
								# 		"payload":"ok"},
								# 		{
								# 		"content_type":"text",
								# 		"title":"no",
								# 		"payload":"not ok"
								# 		}]
								# 	}
								# 	}
								# 	headers = {'Content-Type': 'application/json',}
								# 	response = requests.post('https://graph.facebook.com/v2.6/me/messages?access_token=EAADrWWKPR2EBAG8rdlU9ZA5MteZA2ZCtobvV44YJPT3B1522EmjqK53XufVCFTVa8VIU8qnMiU8g7da1RZALEaalQVv4uSaPTxswKSSLnoZCLMYRR7zy6bbu9V0lvXnEVGb8VNOL4CnZASzhaZCqtF4FuC6xcDToPOtTgAkyLNGjYjf16G0o6pv', headers=headers, data=json.dumps(data))

									# send_message( recipient_id,'Hi, This bot currently allows hospital locator and BMI recognition')

							# else:
								# send_message(recipient_id,'howdy mate!')
			
							if messaging_event['message'].get('attachments') and db.get('image'):
								print('bmi')
								'''
								if latest db record=[address=0, jpg=1]
								'''
								DBrw(address=0,image=0)	
								if messaging_event['message'].get('attachments')[0].get('type')=='image':		
									file_name=messaging_event['message'].get('attachments')[0]['payload']['url']
								#os.makedirs(os.path.dirname(pic_folder_path+'/'+file_name), exist_ok=True)
									file_download_name=wget.download(file_name)
								#os.rename(file_name,pic_folder_path)
									response=give_ans_bmi(file_download_name)
									print("executed bmi")
									send_message(recipient_id, response)
								#send_message(recipient_id,"executed bmi")
								'''
									Reset the records of the database [address=0,jpg=0] and write it back ; conversation completed
								'''	


							if messaging_event['message'].get('attachments'):
								if messaging_event['message'].get('attachments')[0].get('type')=='location':

									DBrw(address=0,image=0)

									coords=messaging_event['message'].get('attachments')[0].get('payload').get('coordinates')
									query_location=(coords.get('lat'),coords.get('long'))	
									nearest_hospital=get_hosp(query_location)
									print(nearest_hospital)
									send_message(recipient_id,nearest_hospital )


	return "Message Processed"


if __name__ == "__main__":
    app.run()
	
