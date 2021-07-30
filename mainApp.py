from flask import Flask, render_template, request,session
import re,math
from urllib import parse

app = Flask(__name__)

#this is for setting session, it's nowhere else used in the code
app.secret_key = 'scientificCalculator'
numberSystem='';

#for reading history file data
def readHistory():
   f = open("history.txt", "r")
   data=""
   for x in f:
   		data = x+data+"\n"
   f.close()
   return data
#for clearing file content
def clearHistoryData():
	file = open("history.txt","r+")
	file.truncate(0)
	file.close()
#conversion of binary number to grey number
def binary_to_gray(n):
	n = int(n, 2)
	n ^= (n >> 1)
	return bin(n)[2:]
#called inside grey_to_binary function, to flip the number
def flip(c):
	return '1' if(c == '0') else '0';
#conversion of grey number to binary number
def grey_to_binary(gray):
	binary = ""
	binary += gray[0]
	for i in range(1, len(gray)):
		if (gray[i] == '0'):
			binary += binary[i - 1];
		else:
			binary += flip(binary[i - 1]);
	return binary; 

#When application is loaded, default url is localhost:5000/, this function is called
@app.route('/')
def home():
	numberSystem="decimal" #default number system is set to decimal
	session['numberSystem']=numberSystem #it is stored in session
	data=readHistory() #function to read history file is called
	#history file data and number system is returned to html file, it's printed in html
	return render_template('calculator.html',data=data,numSystem=numberSystem) 

#when user click on clearHistory button in html page, url changes to /clearHistory
@app.route('/clearHistory',methods = ['POST', 'GET'])
def clearData():
	clearHistoryData() #file content is deleted, function call
	#session number system is returned to html page
	return render_template('calculator.html',numSystem=session['numberSystem'])

#change number system to decimal, binary, grey or hexadecimal
@app.route('/changeNumSystem',methods = ['POST', 'GET'])
def changeNumberSystem():
	#get data from url, number system is passed in url and fetched here stored in the session
	url = request.url
	session['numberSystem']=parse.parse_qs(parse.urlparse(url).query)['numSystem'][0]
	data=readHistory() #reading file data and returning to html
	return render_template("calculator.html",data=data,numSystem=session['numberSystem'])

@app.route('/changeToSystem',methods = ['POST', 'GET'])
def changeToSystem():
	#get data from url, number and number system to be changed is passed in url
	try:
		url = request.url
		changeTo=parse.parse_qs(parse.urlparse(url).query)['changeTo'][0]
		question=parse.parse_qs(parse.urlparse(url).query)['question'][0]
	except:
		question=''
	doConversion="true"
	#first check for the current number system
	currentNumberSys = session['numberSystem']
	#only do the operation like addition, substraction if current system is decimal
	if(currentNumberSys=="decimal"): 
		try:
			num = eval(question)
		except:
			num = question
			doConversion="false" #if try block fails, eg question=3/0
	else:
		doConversion="true"
		num=question #else question itself is the number, that needs to be converted to other number system

	#doConversion is set true when try block passes, continue the calculation
	if(doConversion=="true"):
		question=str(num)
		flag=""
		#if the number is binary or grey, it needs to have only '1','0' and signs, so check it before you convert
		if(currentNumberSys=="binary" or currentNumberSys=="grey"):
			#check if string starts with + or -, remove if it's true
			signRemoved = question
			if(question.startswith('+')):
				signRemoved =signRemoved[1:]
			if(question.startswith('-')):
				signRemoved = signRemoved[1:]
			oneRemoved = signRemoved.replace("1","")
			zeroRemoved = oneRemoved.replace("0","")
			if(zeroRemoved==''): #if the number is binary string is set to ''
				flag="pass"
		else:
			flag="pass"

		#flag varibale is set as 'pass', if it's a proper binary number or any other number system's number
		if(flag=="pass"):
			try:
				#other system to binary conversion
				if(changeTo=="binary"):
					if(currentNumberSys=="decimal"):
						ans=bin(num).replace("0b", "")
					if(currentNumberSys=="binary"):
						ans=num
					if(currentNumberSys=="hexaDecimal"):
						ans=(bin(int(question, 16)).zfill(8)).replace("0b", "")
					if(currentNumberSys=="grey"):
						ans=grey_to_binary(question)
						print("grey to binary")				

				#other system to decimal conversion
				if(changeTo=="decimal"):
					if(currentNumberSys=="decimal"): 
						ans = num
					if(currentNumberSys=="binary"):
						ans = int(question,2) 
					if(currentNumberSys=="hexaDecimal"):
						ans = int(question, 16)
					if(currentNumberSys=="grey"):
						ans=grey_to_binary(str(num))
						ans= int(ans,2) 

				#other system to hexa decimal conversion
				if(changeTo=="hexaDecimal"):
					if(currentNumberSys=="decimal"):
						ans = hex(num)
						ans = str(ans).replace("0x","")
					if(currentNumberSys=="binary"):
						decimal_representation = int(question, 2)
						ans = hex(decimal_representation)
						ans = str(ans).replace("0x","")
					if(currentNumberSys=="hexaDecimal"):
						ans = num
						ans = str(ans).replace("0x","")
					if(currentNumberSys=="grey"):
						ans=grey_to_binary(question)
						decimal_representation = int(ans, 2)
						ans = hex(decimal_representation)
						ans = str(ans).replace("0x","")

				#from other system to grey system
				if(changeTo=="grey"):
					if(currentNumberSys=="binary"):
						ans=binary_to_gray(question)
					if(currentNumberSys=="decimal"):
						ans=bin(num).replace("0b", "")
						ans=binary_to_gray(ans)
					if(currentNumberSys=="hexaDecimal"):
						ans=(bin(int(question, 16)).zfill(8)).replace("0b", "")
						ans=binary_to_gray(ans)
					if(currentNumberSys=="grey"):
						ans=num
			except: #if any exception in conversion, like '2+3'(hexadecimal) to decimal
				ans="NaN"
		else: #flag is false, means binary/grey is not a valid number(contains other than 1 & 0)
			ans="NaN"
	else:#doConversion is false, something is failed in eval(question)
		ans="NaN"
	#write to history, conversion
	f = open("history.txt", "a+")
	f.write(str(num)+"("+session['numberSystem']+")"+" convert to "+changeTo+" = "+str(ans)+"\n")
	f.close()
	session['numberSystem']=changeTo
	data=readHistory()
	return render_template("calculator.html",data=data,numSystem=session['numberSystem'],answer=ans)

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
	    calculate = request.form
	    inputValue =request.form["display"]
	    #first check if the input contains any trigonometric values
	    inputValue = inputValue.replace("sin","math.sin")
	    inputValue = inputValue.replace("cos","math.cos")
	    inputValue = inputValue.replace("tan","math.tan")
	    #if it's any arithmatic or trigonometric, number system is considered as decimal
	    session['numberSystem']="decimal"
	    try:
		    ans = eval(inputValue)
		    ans=str(round(ans,6))
	    except:
		    ans="NaN"
	    # numSystem=numberSystem
	    # write the calculation history to a txt file
	    f = open("history.txt", "a+")
	    f.write(calculate["display"]+" = "+ans)
	    f.write("\n")
	    f.close()

	    #fecth history data
	    data=readHistory()
# round the value to 6 decimal place	    
   return render_template("calculator.html",question = calculate["display"],numSystem=session['numberSystem'],answer=ans,data=data)

if __name__ == '__main__':
   app.run(debug = True)