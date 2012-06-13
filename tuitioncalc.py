# tuitioncalc.py
# NWCS tuition calculator 
# NWCS rates and schedule based on 2012-2013 academic year

baseTuition = 470
grade12Tuition = 235
discountSchedule = {1:0,2:-20,3:-60,4:-100,5:-140}
adultClassTuitionandMaterial = 320
familyRegistrationFee = 20

bookfee = {
'NEW':50,'--':0,
'PK':0,
'KA':10,'KB':10,
'1A':30,'1B':30,
'2A':20,'2B':0,
'3A':20,'3B':20,
'4A':0,'4B':20,
'5A':20,'5B':0,
'6A':20,'6B':20,
'7A':20,'7B':20,
'8A':20,'8B':0,
'9A':30,'9B':20,
'10A':0,'10B':0,
'11A':20,'11B':20,
'12A':0,'12B':0}

materialfee = {
'default':0,'--':0,
'KaraokeMovies':20,
'SAT':25,
'Origami':20,
'Calligraphy':15,
'ChinesePainting':15,
'Dance6':25,
'DancePKK':25,
'Conversation':20,
'Chess':10
}

def getElectiveFee(grade,subject):
	if subject == 'Tutor':
		return 0
	if grade == '12A':
		return 62.5
	if grade == '--' and subject != '--':
		return 200
	return 125

def getBaseTuition(grade):
	if grade == '12A' or grade == '12B':
		return grade12Tuition
	if grade == '--':
		return 0
	return baseTuition

def getBookFee(grade):
	return bookfee[grade]

def getMaterialFee(subject):
	return materialfee[subject]

def applyDiscount(numofNon12thGrade):
	return discountSchedule[numofNon12thGrade]

def addAdultClassFee():
	return adultClassTuitionandMaterial

def addChild(grade,electiveSubject):
	subtotal = 0
	subtotal += getBaseTuition(grade)
	subtotal += getBookFee(grade)
	if electiveSubject != '--':
		subtotal += getElectiveFee(grade,electiveSubject)
		subtotal += getMaterialFee(electiveSubject)
	return subtotal

# testing

total = 0
total += addChild('--','ChinesePainting')
total += addAdultClassFee()
total += applyDiscount(1)
total += familyRegistrationFee
print total

total = 0
total += addChild('1A','Chess')
total += addChild('12B','SAT')
total += applyDiscount(1)
total += familyRegistrationFee
print total

total = 0
total += addChild('2A','--')
total += addChild('1A','--')
total += applyDiscount(2)
total += familyRegistrationFee
print total

total = 0
total += addChild('6B','ChinesePainting')
total += addAdultClassFee()
total += applyDiscount(1)
total += familyRegistrationFee
print total
	
		
	
