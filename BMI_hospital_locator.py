from flask import Flask, request
import random,requests,wget,json
from pymessenger.bot import Bot
import urllib.request


site='http://flask-env.iir8am5aem.ap-southeast-1.elasticbeanstalk.com/'

app = Flask(__name__)
c_ACCESS_TOKEN='EAADrWWKPR2EBAO5xfx5ayTNKULqWoRe4fEA67UxRGB0H5GqeVseyyXegcARRzxRpGWbc9d2B0aPMtOPGB0cQCkD9SVZAxBo027vOFpNck5w2TrslWqjcBVUH2LiWb6hsVpd1fw8pDR5FCu4maYPczbWTnCSrERR2eqNM4Wm8kvFGXZChND'

VERIFY_TOKEN = 'VERIFY_TOKEN'
bot = Bot(c_ACCESS_TOKEN)

db={'address':0,'jpg':0}
with open('db.txt','w') as file:
	file.write(json.dumps(db))

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])

def webook():
 
# endpoint for processing incoming messaging events
 
	data = request.get_json()
	 
	if data["object"] == "page":
	 
		for entry in data["entry"]:
			for messaging_event in entry["messaging"]:
				print(messaging_event)
				if messaging_event.get("postback"):
					print(1)
					
		# user clicked/tapped "postback" button in earlier message
		 
					message_text = messaging_event["postback"]["payload"]
					# the button's payload
					 
					# log("Inside postback")
					print(message_text)
					sender_id = messaging_event["sender"]["id"]
					 
					if (message_text == "Address"):
						'''
						update the data structure ; write to a db ( address =1, jpg=0)
						'''
						db={'address':1,'jpg':0}
						with open('db.txt','w') as file:
							file.write(json.dumps(db))

						send_message(sender_id, "Type your address")
				else:
					# print('this is where you write the condition')
					# print(messaging_event)
					print(request.method)
					if messaging_event.get('message'):
						recipient_id=messaging_event['sender']['id']
						if messaging_event['message'].get('text'):
							text_message_callback=messaging_event['message'].get('text')
							# if text_message_callback != 'Type your address' and not re.search('BMI',text_message_callback):
							'''
							read content of db here 
							'''
							db=eval(open('db.txt','r').read())

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
							else:
								send_message( recipient_id,'Hi, This bot currently allows hospital locator and BMI recognition')

						# else:
							# send_message(recipient_id,'howdy mate!')
						
						if messaging_event['message'].get('attachments'):
							print('bmi')
							'''
							if latest db record=[address=0, jpg=1]
							'''

							file_name=messaging_event['message'].get('attachments')[0]['payload']['url']
							file_download_name=wget.download(file_name)
							response=give_ans(file_download_name)
							# print(response)
							send_message(recipient_id, response)

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
	

if __name__ == "__main__":
    app.run()
	
