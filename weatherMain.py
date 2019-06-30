import os, sys
from urllib import request
import json
from datetime import datetime
from collections import OrderedDict

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import weatherAPIKeyProvider


openWeatherEndpoint = "http://api.openweathermap.org/data/2.5/forecast"
cityDict = {"1277333":"Bangalore", "5368361": "Los Angeles", "6176823": "Waterloo"}
conditionDataContainer = { 
	"Rainy":{
		"filterWord" : ["Rain","Storm","Drizzle"],
		"markerType" : "X",
		"markerColor" : "#217291"
	},
	"Snowy":{
		"filterWord" : "Snow",
		"markerType" : "*",
		"markerColor" : "#707070"
	},
	"Clear":{
		"filterWord" : "Clear",
		"markerType" : "P",
		"markerColor":"#ffa600"
	},
	"Cloudy":{
		"filterWord" : "Cloud",
		"markerType" : "o",
		"markerColor" : "#96b586"
	}
}

APIKey = weatherAPIKeyProvider.return_APIKey();


def getJSONOutputFromServer(locationArray, mode):
	global APIKey
	resultObjects = {}
	if(mode == "CityID"):
		for cityID, cityName in locationArray.items():
			resultObjects[cityID] = request.urlopen(openWeatherEndpoint + "?id=" + str(cityID) + "&APPID=" + APIKey)
			resultObjects[cityID] = json.loads(resultObjects[cityID].read().decode('utf-8'))
	return resultObjects

def filterForWeatherCondition(condition, jsonObjsDict, filterMode):
	todaysAlerts = {}
	for location, jsonObj in jsonObjsDict.items():
		locationAlerts = []
		currLoc = jsonObj["city"]["name"]
		entries = jsonObj["list"]
		currDate = datetime.now()

		if(filterMode == "SingleWordFilter"):
			for weatherEntry in entries:
				timeStamp = weatherEntry["dt_txt"]
				dateFromEntry = datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S")
				if((dateFromEntry.day > currDate.day) or (dateFromEntry.month > currDate.month)):
					break

				weatherDetails = weatherEntry["weather"]

				if(condition.lower() in weatherDetails[0]["description"].lower()):
					alertEntry = (location, condition, dateFromEntry, weatherDetails[0]["description"].title() )
					locationAlerts.append(alertEntry)
		
		elif(filterMode=="MultiWordFilter"):
			print("Condition:", condition, "Mode: Multi")
			for weatherEntry in entries:
				timeStamp = weatherEntry["dt_txt"]
				dateFromEntry = datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S")
				if((dateFromEntry.day > currDate.day) or (dateFromEntry.month > currDate.month)):
					break

				weatherDetails = weatherEntry["weather"]

				for filterWord in condition:
					if(filterWord.lower() in weatherDetails[0]["description"].lower()):
						# print(filterWord, weatherDetails[0]["description"])
						alertEntry = (location, condition, dateFromEntry, weatherDetails[0]["description"].title() )
						locationAlerts.append(alertEntry)
						break


		todaysAlerts[currLoc] = locationAlerts
	return todaysAlerts

def createDataDict(conditionList, conditionAlertObjList):

	finalDataDict = {}

	for condition in conditionList:
		alertsObj = conditionAlertObjList[condition]
		cityAlertDict = {}
		
		for cityName, alertEntryList in alertsObj.items():
			cityAlertTimesForCondition = []
			for entry in alertEntryList:
				cityAlertTimesForCondition.append(entry[2])
			cityAlertDict[cityName] = cityAlertTimesForCondition

		finalDataDict[condition] = cityAlertDict

	return finalDataDict

def plotWeatherCharts(finalDataDict):
	print(finalDataDict)
	plt.style.use("ggplot")
	fig, axs = plt.subplots(1)
	
	axs.set_axisbelow(True)
	axs.set_xlabel("Time", fontweight="bold")
	axs.set_ylabel("City", fontweight="bold")
	axs.tick_params(axis='x',rotation=45)
	axs.tick_params(axis='y',rotation=45)
	axs.title.set_text("Today's Weather Conditions")


	todayStartObj = datetime.strptime(datetime.now().strftime("%Y%m%d") + " 00:00", "%Y%m%d %H:%M")
	todayEndObj = datetime.strptime(datetime.now().strftime("%Y%m%d") + " 23:59", "%Y%m%d %H:%M")  

	axs.set_xlim([todayStartObj, todayEndObj])
	# fig.set_title("Weather Conditions")

	locator = None

	while locator == None:
		try:
			locator = mdates.HourLocator(byhour=range(0,24,3))
		except RunTimeError:
			continue


	axs.xaxis.set_major_locator(locator)
	axs.xaxis.set_major_formatter(mdates.DateFormatter("%I %p"))

	for conditionName, conditionDict in finalDataDict.items():
		currAx = axs
		currMarker = conditionDataContainer[conditionName]["markerType"]
		currMarkerColor = conditionDataContainer[conditionName]["markerColor"]

		for cityName, timeStamps in conditionDict.items():
			yVals = [cityName for i in range(len(timeStamps))]
			xVals = [timeStamp for timeStamp in timeStamps]
			currAx.scatter(xVals, yVals, marker=currMarker, c=currMarkerColor, label=conditionName, s=10**2)

	
	handles, labels = axs.get_legend_handles_labels()
	by_label = OrderedDict(zip(labels, handles))
	axs.legend(by_label.values(), by_label.keys(), loc="best")


	plt.tight_layout()
	plt.show()



if(__name__ == "__main__"):
	conditionAlertDict = {}

	jsonObjs = getJSONOutputFromServer(cityDict, "CityID")

	for conditionName, conditionData in conditionDataContainer.items():
		if(isinstance(conditionData["filterWord"], list)):
			conditionAlertDict[conditionName] = filterForWeatherCondition(conditionData["filterWord"], jsonObjs, "MultiWordFilter")
		else:
			conditionAlertDict[conditionName] = filterForWeatherCondition(conditionData["filterWord"], jsonObjs, "SingleWordFilter")

	
	finalDataDict = createDataDict(conditionDataContainer.keys(), conditionAlertDict)

	plotWeatherCharts(finalDataDict)
	



