'''
    CA02 by LZX0014

'''
import time as _time
import Angle as angle
from datetime import tzinfo, timedelta, datetime
from xml.dom.minidom import parse
from math import sqrt, tan, pi
import os


STDOFFSET = timedelta(seconds=-_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds=-_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return 0

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0

localtime = LocalTimezone()

def LogTimeStamp():
    return datetime.now(localtime).replace(microsecond=0).isoformat(' ')

class Fix():

    def writeLogEntry(self, logFile, stringEntry):
        with open(logFile, "a+") as openlog:
            openlog.write("LOG:\t" + LogTimeStamp() + "\t" + stringEntry + "\n")

    def __init__(self, logFile=None):
        functionName = "Fix.__init__:  "
        if logFile == None:
            logFile = "log.txt"
        if not(isinstance(logFile, str)):
            raise ValueError(functionName + "Input should be a string")
        if logFile == "":
            raise ValueError(functionName + "Name length should be greater or equal to 1")
        try:
            logString = "Log file:\t" + os.path.abspath(logFile)
            self.writeLogEntry(logFile, logString)
        except IOError:
            raise ValueError (functionName + "This file can not be created or appended")
        self.logFile = logFile            
        self.sightingFile = ""
        self.ariesFile = ""
        self.starFile = ""
        
    def setSightingFile(self, sightingFile=None):
        functionName = "Fix.setSightingFile:  "
        if not(isinstance(sightingFile, str)):
            raise ValueError(functionName + "Input is not a xml file")
        if not(sightingFile[-4:] == ".xml"):
            raise ValueError(functionName + "Input is not a xml file")
        if sightingFile[0:-4] == "":
            raise ValueError(functionName + "Name length should be greater or equal to 1")
        try:
            open(sightingFile, "r")
        except IOError:
            raise ValueError (functionName + "This file can not opened")        
        self.sightingFile = sightingFile
        logString = "Sighting file:\t" + os.path.abspath(self.sightingFile)
        self.writeLogEntry(self.logFile, logString)
        return self.sightingFile
    
    def setAriesFile(self, ariesFile=None):
        functionName = "Fix.setAriesFile:  "
        if not(isinstance(ariesFile, str)):
            raise ValueError(functionName + "Input is not a txt file")
        if not(ariesFile[-4:] == ".txt"):
            raise ValueError(functionName + "Input is not a txt file")
        if ariesFile[0:-4] == "":
            raise ValueError(functionName + "Name length should be greater or equal to 1")
        try:
            open(ariesFile, "r")
        except IOError:
            raise ValueError (functionName + "This file can not opened")        
        self.ariesFile = ariesFile
        logString = "Aries file:\t" + os.path.abspath(self.ariesFile)
        self.writeLogEntry(self.logFile, logString)
        return os.path.abspath(self.ariesFile)
    
    def setStarFile(self, starFile=None):
        functionName = "Fix.setStarFile:  "
        if not(isinstance(starFile, str)):
            raise ValueError(functionName + "Input is not a txt file")
        if not(starFile[-4:] == ".txt"):
            raise ValueError(functionName + "Input is not a txt file")
        if starFile[0:-4] == "":
            raise ValueError(functionName + "Name length should be greater or equal to 1")
        try:
            open(starFile, "r")
        except IOError:
            raise ValueError (functionName + "This file can not opened")        
        self.starFile = starFile
        logString = "Star file:\t" + os.path.abspath(self.starFile)
        self.writeLogEntry(self.logFile, logString)
        return os.path.abspath(self.starFile)
    
    
    def _getText(self, sighting, tagName):
        elementNodelist = sighting.getElementsByTagName(tagName)
        textNodelist = elementNodelist[0].childNodes
        data = textNodelist[0].data
        return data
        
    def getBody(self, sighting):
        try:
            bodyText = self._getText(sighting, "body")
        except IndexError:
            raise ValueError('Fix.getSightings:  "body" is missing in the sighting')
        bodyString = str(bodyText)
        return bodyString 
    
    def getDate(self, sighting):
        try:
            dateText = self._getText(sighting, "date")
        except IndexError:
            raise ValueError('Fix.getSightings:  "date" is missing in the sighting')
        dateString = str(dateText)
        return self.validateDate(dateString) 
    
    def validateDate(self, dateString):
        try:
            date = datetime.strptime(dateString, '%Y-%m-%d').date()
            return date
        except ValueError:
            raise ValueError('Fix.getSightings:  Wrong date format')
        
    def getTime(self, sighting):
        try:
            timeText = self._getText(sighting, "time")
        except IndexError:
            raise ValueError('Fix.getSightings:  "time" is missing in the sighting')
        timeString = str(timeText)
        return self.validateTime(timeString)
    
    def validateTime(self, timeString):
        try:
            time = datetime.strptime(timeString, '%X').time()
            return time
        except ValueError:
            raise ValueError('Fix.getSightings:  Wrong time format') 
    
    def getObservedAltitude(self, sighting):
        try:
            angleText = self._getText(sighting, "observation")
        except IndexError:
            raise ValueError('Fix.getSightings:  "observation" is missing in the sighting')
        angleString = str(angleText)
        return self.validateObservation(angleString)
        
    def validateObservation(self, angleString):
        functionName = "Fix.getSightings:  "
        parts = angleString.partition ('d')
        if (not(parts[1] == 'd')):
            raise ValueError(functionName + 'wrong observation format, d is missing')
        try:
            integpart = int(parts[0])
        except ValueError:
            raise ValueError(functionName + 'wrong observation format, X should be a integer')
        if not(0 <= integpart < 90):
            raise ValueError(functionName + 'wrong observation format, X should be in [0,90)')
        try:
            floatpart = float(parts[2])
        except ValueError:
            raise ValueError(functionName + 'wrong observation format, y should be float or integer')
        if not(0.0 <= floatpart < 60.0):
            raise ValueError(functionName + 'wrong observation format, y should be in [0.0,60.0)')
        if (not(floatpart == round(floatpart, 1))):
            raise ValueError(functionName + 'wrong observation format, y should only have one digit')
        observedAltitude = angle.Angle()
        observedAltitude.setDegreesAndMinutes(angleString)
        return observedAltitude

    def getHeight(self, sighting):
        functionName = "Fix.getSightings:  "
        try:
            heightText = self._getText(sighting, "height")
        except Exception:
            return 0.0
        try:
            height = float(heightText)
        except ValueError:
            raise ValueError(functionName + "Height should be numeric")
        if height >= 0:
            return height
        else:
            raise ValueError(functionName + "Height should be greater than 0")
    
    def getTemperature(self, sighting):
        functionName = "Fix.getSightings:  "
        try:
            temperatureText = self._getText(sighting, "temperature")
        except IndexError:
            return 72
        try:
            temperature = int(temperatureText)
        except ValueError:
            raise ValueError(functionName + "Height should be integer")
        if -20 <= temperature <= 120:
            return temperature
        else:
            raise ValueError(functionName + "Temperature should be in [-20,120]")
            
    def getPressure(self, sighting):
        functionName = "Fix.getSightings:  "
        try:
            pressureText = self._getText(sighting, "pressure")
        except IndexError:
            return 1010
        try:
            pressure = int(pressureText)
        except ValueError:
            raise ValueError(functionName + "Pressure should be integer")
        if 100 <= pressure <= 1100:
            return pressure
        else:
            raise ValueError(functionName + "Pressure should be in [100,1100]")        
    
    def isHorizonNatural(self, sighting):
        functionName = "Fix.getSightings:  "
        try:
            horizonText = self._getText(sighting, "horizon")
        except IndexError:
            return True
        horizonString = str(horizonText)
        if horizonString.lower() == "natural":
            return True
        elif horizonString.lower() == "artificial":
            return False
        else:
            raise ValueError(functionName + "Horizon category can not be identified")   
    
    def calculateDip(self, isHorizonNatural, height):
        if isHorizonNatural:
            dip = (-0.97 * sqrt(height)) / 60
        else:
            dip = 0
        return dip
    
    def calculateRefraction(self, observedAltitude, pressure, temperature):        
        functionName = "Fix.getSightings:  "
        minimumAngle = angle.Angle()
        minimumAngle.setDegreesAndMinutes("0d0.1")
        if observedAltitude.compare(minimumAngle) == -1:
            raise ValueError(functionName + "Observation should be greater or equal to 0d0.1")
        else:           
            temperatureInC = (temperature - 32) * 5 / 9
            observedAltitudeInRadian = observedAltitude.getDegrees() / 180 * pi           
            refraction = (-0.00452 * pressure) / (273 + temperatureInC) / tan(observedAltitudeInRadian)
        return refraction
    
    def getAdjustedAltitude(self, sighting):
        observedAltitude = self.getObservedAltitude(sighting)
        height = self.getHeight(sighting)
        temperature = self.getTemperature(sighting)
        pressure = self.getPressure(sighting)
        isHorizonNatural = self.isHorizonNatural(sighting) 
        dip = self.calculateDip(isHorizonNatural, height)
        refraction = self.calculateRefraction(observedAltitude, pressure, temperature)
        adjustedAltitudeDegree = observedAltitude.getDegrees() + dip + refraction
        adjustedAltitude = angle.Angle()
        adjustedAltitude.setDegrees(adjustedAltitudeDegree)
        return adjustedAltitude.getString()        
        
    def getGeographicLatitude(self, body, date):    
        functionName = "Fix.getSightings:  "
        starFile = open(self.starFile, "r")
        searchString = starFile.readlines()
        for line in searchString:
            information = line[:-1].split('\t')
            try:
                dateInformation = datetime.strptime(information[1], '%x').date()
            except IndexError:
                raise ValueError(functionName + "can not find star body in star file")
            if body == information[0]:
                if dateInformation <= date:
                    latitude = information[3]
                else:
                    return latitude
        raise ValueError(functionName + "can not find star body in star file")
    
    def getSHA(self, body, date):
        functionName = "Fix.getSightings:  "
        starFile = open(self.starFile, "r")
        searchString = starFile.readlines()
        for line in searchString:
            information = line[:-1].split('\t')
            dateInformation = datetime.strptime(information[1], '%x').date()
            if body == information[0]:
                if dateInformation <= date:
                    SHA = information[2]
                else:
                    return SHA
        raise ValueError(functionName + "can not find star body in star file")
    
    def extractGHA(self, datetime, datetimeInformation, GHA1, GHA2):
        GHA1A = angle.Angle()
        GHA2A = angle.Angle()
        GHADA = angle.Angle()
        GHA1A.setDegreesAndMinutes(GHA1)
        GHA2A.setDegreesAndMinutes(GHA2)
        timeDifference = datetime - datetimeInformation 
        s = timeDifference.total_seconds() + 3600
        GHA2A.subtract(GHA1A)
        GHADdegree = GHA2A.getDegrees() * s / 3600
        GHADA.setDegrees(GHADdegree)
        GHA1A.add(GHADA)
        return GHA1A
    
    def getGHA(self, datetime):
        functionName = "Fix.getSightings:  "
        ariesFile = open(self.ariesFile, "r")
        searchString = ariesFile.readlines()
        GHA2 = "notSet"
        for line in searchString:
            information = line[:-1].split('\t')
            try:
                datetimeInformation = datetime.strptime(information[0], '%x')
            except Exception:
                raise ValueError(functionName + "Invalid aries file")
            datetimeInformation = datetimeInformation.replace(hour=int(information[1]))
            GHA1 = GHA2
            GHA2 = information[2]
            if datetime < datetimeInformation:
                try:
                    GHA = self.extractGHA(datetime, datetimeInformation, GHA1, GHA2)
                    return GHA
                except Exception:
                    raise ValueError(functionName + "Invalid aries file")
        raise ValueError(functionName + "Invalid aries file")
        
    def getGeographicLongitude(self, body, date, datetime):
        SHA = angle.Angle()
        SHAstring = self.getSHA(body, date)
        SHA.setDegreesAndMinutes(SHAstring)
        GHA = self.getGHA(datetime)
        GHA.add(SHA)
        return GHA.getString()            
            
        
    def getSightings(self):
        functionName = "Fix.getSightings:  "
        errorNum = 0
        if self.sightingFile == "":
            raise ValueError(functionName + "No sighting files has bee set")
        if self.ariesFile == "":
            raise ValueError(functionName + "No aries files has bee set")
        if self.starFile == "":
            raise ValueError(functionName + "No star files has bee set")
        try:
            domtree = parse(self.sightingFile)
        except Exception:
            errorNum += 1
            self.writeLogEntry(self.logFile, "Sighting Errors:\t" + str(errorNum))
            self.writeLogEntry(self.logFile, "End of sighting file:\t" + self.sightingFile)
            return None
        sightings = domtree.getElementsByTagName("sighting")
        sightingList = []
        for sighting in sightings:
            try:
                body = self.getBody(sighting)
                date = self.getDate(sighting)
                time = self.getTime(sighting)
                combinedDatetime = datetime.combine(date, time)
                latitude = self.getGeographicLatitude(body, date)
                longitude = self.getGeographicLongitude(body, date, combinedDatetime)
                adjustedaltitude = self.getAdjustedAltitude(sighting)
                sightingList.append((body, date, time, adjustedaltitude, combinedDatetime, latitude, longitude))
            except ValueError:
                errorNum += 1
        sightingList.sort(key=lambda s:(s[4], s[0]))
        for sighting in sightingList:
            logString = sighting[0] + "\t" + sighting[1].isoformat() + "\t" + sighting[2].isoformat() + "\t" + sighting[3] + "\t" + sighting[5] + "\t" + sighting[6]
            self.writeLogEntry(self.logFile, logString)
        self.writeLogEntry(self.logFile, "Sighting Errors:\t" + str(errorNum))
        self.writeLogEntry(self.logFile, "End of sighting file:\t" + self.sightingFile)
        approximateLatitude = "0d0.0"
        approximateLongtitude = "0d0.0"
        return (approximateLatitude, approximateLongtitude)
