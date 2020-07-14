class KukaLocation:
    """
    Erstelle ein Objekt KukaLocation
    """
    def __init__(self, n="leer", x=0.0, y=0.0, z=0.0, a=0.0, b=0.0, c=0.0, s=99, t=99, e1=0.0, e2=0.0, e3=0.0, e4=0.0, e5=0.0, e6=0.0):
        """
        Initialisiere ein neues Objekt KukaLocation
        Argumente:
        * Name(String): Name der Location
        * XKoordinate(float): Koordinate auf der X-Achse
        * YKoordinate(float): Koordinate auf der Y-Achse
        * ZKoordinate(float): Koordinate auf der Z-Achse
        * AWinkel(float): Winkel des A-Winkels
        * BWinkel(float): Winkel des B-Winkels
        * CWinkel(float): Winkel des C-Winkels
        * Status(int): Status der Achskonfiguration
        * Turn(int): Turn der Achskonfiguration
        * EAchse1(float): Werte der externen Achse 1
        * EAchse2(float): Werte der externen Achse 2
        * EAchse3(float): Werte der externen Achse 3
        * EAchse4(float): Werte der externen Achse 4
        * EAchse5(float): Werte der externen Achse 5
        * EAchse6(float): Werte der externen Achse 6
        """
        self.Name = n
        self.XKoordinate = round(float(x),2)
        self.YKoordinate = round(float(y),2)
        self.ZKoordinate = round(float(z),2)
        self.AWinkel = round(float(a),2)
        self.BWinkel = round(float(b),2)
        self.CWinkel = round(float(c),2)
        self.Status = s
        self.Turn = t
        self.EAchse1 = round(float(e1),2)
        self.EAchse2 = round(float(e2),2)
        self.EAchse3 = round(float(e3),2)
        self.EAchse4 = round(float(e4),2)
        self.EAchse5 = round(float(e5),2)
        self.EAchse6 = round(float(e6),2)

    def LocationInString(location):
        locationString="DECL E6POS " + location.Name + "={X " + str(location.XKoordinate) + ",Y " +  str(location.YKoordinate) + ",Z " +  str(location.ZKoordinate)\
        + ",A " +  str(location.AWinkel) + ",B " +  str(location.BWinkel) + ",C " + str(location.CWinkel)\
        + ",S " +  str(location.Status) + ",T " +  str(location.Turn)\
        + ",E1 " +  str(location.EAchse1)  + ",E2 " +  str(location.EAchse2) + ",E3 " +  str(location.EAchse3)\
        + ",E4 " +  str(location.EAchse4) + ",E5 " + str(location.EAchse5) + ",E6 " +  str(location.EAchse6) + "}" + "\n"
        return locationString

