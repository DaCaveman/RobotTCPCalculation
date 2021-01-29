from KukaLocation import *
from scipy.spatial.transform import Rotation as R
from matplotlib import rcParams
import sqlite3, os, csv, math, scipy
import numpy as np
import matplotlib.pyplot as plt

"""
Declaration of some global variables
"""

datalist=os.listdir(".\Einlesen")
_datalist=(".\Einlesen\\")
LocationList=[]
CompleteList=[]
xList=[]
yList=[]
zList=[]
aList=[]
bList=[]
cList=[]
Base=[]
TCP=[]
QualityPerPoint=[]
rcParams["font.family"] = "serif"

#Calculates the average of the values from spXYZ
def average(spXYZ):
    value=0
    for item in spXYZ:
        value += item

    result = (1/len(spXYZ))*value
    return result

#Calculates the summary for each index of the A Matrix
def sumForA(spXYZ1,spXYZ2):
    result=0
    itemLine=average(spXYZ2)
    for n,item in enumerate(spXYZ1):
        result+=(item*(spXYZ2[n]-itemLine))/len(spXYZ1)

    return result

#Calculates the summary for each index of the B Matrix
def sumForB(spXYZ1,spXYZ2,spXYZ3,spXYZ4):
    result=0
    for i in range(0,len(spXYZ1)):
        result+=((np.square(spXYZ1[i])+np.square(spXYZ2[i])+np.square(spXYZ3[i]))*(spXYZ4[i]-average(spXYZ4)))/len(spXYZ1)

    return result

#Best-Fit sphere calculation from the given data points
def fitSphere(spX, spY, spZ):
    A=[]
    B=[]
    bestFit=[]

    # A matrix
    A=2*(np.array([[sumForA(spX,spX),sumForA(spX,spY),sumForA(spX,spZ)],
                   [sumForA(spY,spX),sumForA(spY,spY),sumForA(spY,spZ)],
                   [sumForA(spZ,spX),sumForA(spZ,spY),sumForA(spZ,spZ)]]))

    # B matrix
    B=np.array([[sumForB(spX,spY,spZ,spX)],
                [sumForB(spX,spY,spZ,spY)],
                [sumForB(spX,spY,spZ,spZ)]])

    # Transposition of the A matrix
    AT=np.transpose(A)
    # Product of transposed A matrix and A
    ATA=AT.dot(A)
    #Inverse of the product of the transposed A matrix and A
    invATA=np.linalg.inv(ATA)
    #Product of the inverse ATA and AT
    invATAdotAT=invATA.dot(AT)
    #Best-Fit Calulation / Product of invATAdotAT and B matirx
    bestFit=invATAdotAT.dot(B)

    #Calculation of the fit quality
    sumRadius=0
    for i,item in enumerate(spX):
        sumRadius+=(np.square(spX[i]-bestFit[0])+np.square(spY[i]-bestFit[1])+np.square(spZ[i]-bestFit[2]))

    radius=np.sqrt(sumRadius/len(spX))

    return bestFit, radius

#function z(x,y)
def functionZ(spX, spY, spZ, base, radius):

    funcZ=0
    if spZ < base[2]:
        funcZ=-np.sqrt(abs(np.square(radius)-np.square(spX-base[0])-np.square(spY-base[1])))+base[2]
    elif spZ >= base[2]:
        funcZ=np.sqrt(abs(np.square(radius)-np.square(spX-base[0])-np.square(spY-base[1])))+base[2]

    return funcZ

#Fit quality
def fitQualityUpper(spX, spY, spZ, base, radius):

    value=[]
    for i,item in enumerate(spX):
        value.append(np.square(spZ[i]-functionZ(spX[i], spY[i], spZ[i], base, radius)))

    return value

#Fit quality
def fitQualityLower(spZ):

    sumZ=0
    value=0
    for item in spZ:
        sumZ+=item

    for i,item in enumerate(spZ):
        value+=np.square(spZ[i]-((1/len(spZ))*sumZ))

    return value

#Creating a transformation matrix for the first data point in the list
def CreateTransMatrix(spX,spY,spZ,srZ,srY,srX):

    #Creating an identity matrix
    transMatrix=np.identity(4)

    # 1:4 matrix for X / Y / Z / 1
    helpArray=np.array([[spX],[spY],[spZ],[1]])

    #Creating a rotation 3:3 matrix from rX / rY / rZ
    rotMatrix=R.from_euler('xyz',[srX,srY,srZ],degrees=True).as_matrix()

    #Inserting the rotation matrix and position matrix in a 4:4 matrix
    transMatrix[0:0+rotMatrix.shape[0], 0:0+rotMatrix.shape[1]] = rotMatrix
    transMatrix[0:0+helpArray.shape[0], 3:3+helpArray.shape[1]] = helpArray

    return transMatrix

#Calculation of the TCP form a best fitted sphere for Base and a flange
#position
def TCP_Calc(spX,spY,spZ,srZ,srY,srX):

    #Calculatin a best fit Base
    bestFitBase, bestFitRadius = fitSphere(spX, spY, spZ)

    #Creating an position matrix from the best fitted base
    base=np.array([bestFitBase[0],bestFitBase[1],bestFitBase[2],1], dtype=object)

    #search for the best fitted position for TCP calculation
    qualityPerPoint=[]
    for i,item in enumerate(spX):
        qualityPerPoint.append(functionZ(spX[i], spY[i], spZ[i], bestFitBase, bestFitRadius)-spZ[i])

    n = qualityPerPoint.index(min(qualityPerPoint, key=abs))

    #Creating a transformation Matrix with the best fitted position
    flange=CreateTransMatrix(spX[n], spY[n], spZ[n], srZ[n], srY[n], srX[n])

    #Calculating the TCP from the product of the inversed "flange" matrix and
    #the positon "base" matrix
    tcp=np.linalg.inv(flange).dot(base)
    upperFunc=fitQualityUpper(spX, spY, spZ, bestFitBase, bestFitRadius)
    upper=sum(fitQualityUpper(spX, spY, spZ, bestFitBase, bestFitRadius))
    lower=fitQualityLower(spZ)

    quality=1-(sum(fitQualityUpper(spX, spY, spZ, bestFitBase, bestFitRadius))/fitQualityLower(spZ))

    return bestFitBase, tcp, quality, bestFitRadius

#Main program
def main():
    #Reading each file in the datalist / folder:"Einlesen"
    for path in datalist:
        #Initialisation of necessary lists for each cycle
        xList = []
        yList = []
        zList = []
        aList = []
        bList = []
        cList = []
        if ".dat" in path and not ".swp" in path:
            #Reading a file in the datalist
            #eingang=open(_datalist + path)
            with open(_datalist + path) as eingang:
                for line in eingang:

                    #Adding the read lines to a list
                    CompleteList.append(line)

                    #Each line, where e6pos exists will be splitted in defined parts
                    #so that the true X / Y / Z / A / B / C values can be put in
                    #seperate lists
                    if "e6pos" in line.lower() and "decl " in line.lower():
                        list=line.replace(","," ").replace("="," ").replace("{"," ").replace("}"," ").split()
                        xList.append(eval(list[4]))
                        yList.append(eval(list[6]))
                        zList.append(eval(list[8]))
                        aList.append(eval(list[10]))
                        bList.append(eval(list[12]))
                        cList.append(eval(list[14]))

                #Closing the read file
                #eingang.close
                print(path + " is finshed")

                #Calculating an Base and a TCP for each file
                Base, TCP, Quality, Radius = TCP_Calc(xList, yList, zList, aList, bList, cList)

                for i,item in enumerate(xList):
                    QualityPerPoint.append(functionZ(xList[i], yList[i], zList[i], Base, Radius)-zList[i])

                #Printing the Quality, Base and the TCP for each file
                print("\n")
                print("Quality(To consider with caution)")
                print(Quality)
                print("\n")
                print("Calculated Base")
                print("X = ",  Base[0])
                print("Y = ",  Base[1])
                print("Z = ",  Base[2])
                print("\n")
                print("Calculated TCP")
                print("X = ",  TCP[0])
                print("Y = ",  TCP[1])
                print("Z = ",  TCP[2])
                print("\n")
                print("Radius of the sphere: ", Radius)
                print("\n")
                print("Mininmal distance to sphere surface: ", abs(min(QualityPerPoint, key=abs)))
                print("Maximal distance to sphere surface:  ", abs(max(QualityPerPoint, key=abs)))
                print("Average distance to sphere surface:  ", (sum(abs(item) for item in QualityPerPoint)/len(QualityPerPoint)))
                print("\n")

                u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
                x = np.cos(u)*np.sin(v)*Radius
                y = np.sin(u)*np.sin(v)*Radius
                z = np.cos(v)*Radius
                # x = Base[0]
                # y = Base[1]
                # z = Base[2]
                x = x + Base[0]
                y = y + Base[1]
                z = z + Base[2]

                #   3D plot of Sphere
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                ax.scatter(xList, yList, zList, zdir='z', s=20, c='b',rasterized=True)
                ax.scatter(Base[0], Base[1], Base[2], zdir='z', s=40, c='r',rasterized=True)
                ax.plot_wireframe(x, y, z, color="r")
                # ax.set_aspect("equal")
                # ax.set_xlim3d((Base[0] - Radius * 1.2),(Base[0] + Radius * 1.2))
                # ax.set_ylim3d((Base[1] - Radius * 1.2),(Base[1] + Radius * 1.2))
                # ax.set_zlim3d((Base[2] - Radius * 1.2),(Base[2] + Radius * 1.2))
                ax.autoscale_view()
                ax.set_xlabel('$x$ (mm)',fontsize=16)
                ax.set_ylabel('\n$y$ (mm)',fontsize=16)
                zlabel = ax.set_zlabel('\n$z$ (mm)',fontsize=16)
                plt.show(block=False)
                # plt.savefig('steelBallFitted.pdf', format='pdf', dpi=300, bbox_extra_artists=[zlabel], bbox_inches='tight')

if __name__ == '__main__':
    main()
