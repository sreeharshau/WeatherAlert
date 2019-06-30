import os, sys
from urllib import request
import json
from datetime import datetime

import matplotlib.pyplot as plt

import weatherAPIKeyProvider

openWeatherEndpoint = "http://api.openweathermap.org/data/2.5/forecast"
cityDict = {"1277333":"Bangalore", "1269843": "Hyderabad", "5368361": "Los Angeles", "6176823": "Waterloo"}


def getJSONOutputFromServer(locationArray, mode):
	resultObjects = {}
	APIKey = weatherAPIKeyProvider.return_APIKey();
	if(mode == "CityID"):
		for cityID, cityName in locationArray.items():
			resultObjects[cityID] = request.urlopen(openWeatherEndpoint + "?id=" + str(cityID) + "&APPID=" + APIKey)
			resultObjects[cityID] = json.loads(resultObjects[cityID].read())
	
	return resultObjects

def filterForWeatherCondition(condition, jsonObjsDict):
	todaysAlerts = {}
	for location, jsonObj in jsonObjsDict.items():
		locationAlerts = []
		currLoc = jsonObj["city"]["name"]
		# print("Scanning today's weather patterns at location:", location, "-", currLoc)
		entries = jsonObj["list"]
		for weatherEntry in entries:
			timeStamp = weatherEntry["dt_txt"]
			currDate = datetime.now()
			dateFromEntry = datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S")

			if(dateFromEntry.day > currDate.day):
				break

			weatherDetails = weatherEntry["weather"]
			if(condition.lower() in weatherDetails[0]["description"].lower()):
				# print("Condition", condition, "detected at:", dateFromEntry.strftime("%Y-%m-%d %H:%M:%S"), "at location", currLoc)
				alertEntry = (location, condition, dateFromEntry, weatherDetails[0]["description"].title() )
				locationAlerts.append(alertEntry)
		todaysAlerts[currLoc] = locationAlerts
	return todaysAlerts

def plotWeatherChart(condition, alertsObj):

	if(condition == "Rain"):
		marker = '\\star'
		markerColor = "blue"
	elif(condition == "Snow"):
		marker = '\\diamondsuit'
		markerColor = "grey"

	for cityName, alertEntryList in alertObj.items():
		cityAlertTimesForCondition = []

			





if(__name__ == "__main__"):
	print("Checking city mode")
	jsonObjs = getJSONOutputFromServer(cityDict, "CityID")
	rainAlertsObj = filterForWeatherCondition("Rain", jsonObjs)
	snowAlertsObj = filterForWeatherCondition("Snow", jsonObjs)

	print(rainAlertsObj)

	



