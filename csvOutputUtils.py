import os
import csv

class CSVDomainOutput():
    def __init__(self, outputDir) -> None:
        self.outputDir = outputDir

        self.rows = []
        self.header = ["Domain Name", "Potential Goal", "Initial", "isRealGoal", "Time to Extract Landmarks", "Extracted Landmarks"]
    
    def addNewRow(self):
        row = CSVDomainRow()
        self.rows.append(row)
        return row
    
    def writeToCSV(self, filename):
        f = open(os.path.join(os.path.dirname(__file__),
                                  self.outputDir) + f"/{filename}.csv", "a")
        writer = csv.writer(f)
        writer.writerow(self.header)
        for row in self.rows:
            writer.writerow(row.dataToWrite())
        f.close()
        
class CSVDomainRow():
    def __init__(self) -> None:
        self.domainName = "not provided"
        self.goalState = "not provided"
        self.initialState = "not provided"
        self.isRealGoal = False
        self.extractionTime = -1
        self.landmarks = "not provided"
    
    def dataToWrite(self):
        return [self.domainName, self.goalState, self.initialState, self.isRealGoal, self.extractionTime, self.landmarks]

class CSVApproachOutput():
    def __init__(self, outputDir) -> None:
        self.outputDir = outputDir
        
        self.rows = []
        self.header = ["Approach", "Initial", "Goal", "Time to Order Landmarks", "Time to Generate Plan", "Path Length", "Path", "Deceptive Cost", "Deceptive Quality", "Deception Score"]
    
    def addNewRow(self):
        row = CSVApproachRow()
        self.rows.append(row)
        return row
    
    def writeToCSV(self, filename):
        f = open(os.path.join(os.path.dirname(__file__),
                                  self.outputDir) + f"/{filename}.csv", "a")
        writer = csv.writer(f)
        writer.writerow(self.header)
        for row in self.rows:
            writer.writerow(row.dataToWrite())
        f.close()

class CSVApproachRow():
    def __init__(self) -> None:
        self.approachName = "not provided"
        self.initialState = "not provided"
        self.goalState = "not provided"
        self.orderingTime = -1
        self.planTime = -1
        self.pathLength = -1
        self.path = "not provided"
        self.deceptiveCost = 0
        self.deceptiveQuality = 0
        self.deception = 0
    
    def dataToWrite(self):
        return [self.approachName, self.initialState, self.goalState, self.orderingTime, self.planTime, self.pathLength, self.path, self.deceptiveCost, self.deceptiveQuality, self.deception]
