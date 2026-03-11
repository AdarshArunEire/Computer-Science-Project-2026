# Computer-Science-Project-2026
My submission for the Leaving certificate computer science project.



Some notes to self i might need later:

    The coordinate areas of my FIRMS and nasa POWER data selections are: 
        W: -8.5
        N: 40.3
        E: -6.8
        S: 39.0
        This is a central portugal/west ish area that should have both many fire condtions in summer and not too many in winter, so should be good for learning boundaries or even regression if i want aslong as i exclude date to prevent seasonal shortcuts learned.

    limitations:
        trained on portugal data, differing in vegetiation land cover human acitivty and a generally different climate. 
        FIRMS is going to be a binary fire/nofire, and the model trains on that. Does it even
        repersent risk????? gulp.. FIXED (not...) went for classes 0-3 instead of 0/1
        SMAP is coming back as some wierd file format. Only points come back as csvs, so im gonna have to average a few to prevent bias.... ARGH

    SMAP points: ITS LATITUDE, LONGITUDE this used to be reversed...
        centre, none, 39.65, -7.65
        northwest, none, 40.0, -8.15
        northeast, none, 40.0, -7.15
        southwest, none, 39.3, -8.15
        southeast, none, 39.3, -7.15

    smap came back, alot of points are flagged for qual. going to only filter empty rows out (-9999) and keep qual == any:
    Proportions of qual flags:
    Qual_Flag - (7 is NOT 7 times worse than 1)
    7.0    51%
    0.0    38%
    1.0    10%
    5.0    <1%
    smap unit value meaning is cm3 of water per cm3 of soil proportion: remeber to figure out how this maps back to 3v analoug of microbit

    POWER: i chose to only take the center point of 39.65, -7.65 and run with it czu temp doenst fvary much within that small area

    fire_risk_class from firms proportions after seeing it with the 0s;
    0.0    0.729138
    1.0    0.209302
    3.0    0.031464
    2.0    0.030096
    think ill merge 3 and 2 for the sake of a balenced distribution, and change thresholds 

    fire_risk_class
    0.0    0.729138
    .0    0.176471
    2.0    0.094391
    Name: proportion, dtype: float64
    fire_risk_class
    0.0    533
    1.0    129
    2.0     69
    Name: count, dtype: int64
    0==0, 1==1, else==2, pros are; this is trainable, cons are; this is not low med high anymore, more like none, low, med. More meaningful to model, and more accurate in ireland though!
    
    INSTREAD of 1 model, make 2; one that can only use light temp and mositure, one that can do LOADS. This way i can actually target a real fire index isntead of making fake classes from the fire count of a day. the first model will not be a ml model, just a index calcultor. it will take many more inpiut sensor data, tso the model two value is a ml model trained only on the sneros avlible in micribit
    https://cwfis.cfs.nrcan.gc.ca/background/summary/fwi is model 1. Model 2 will be a ml model that predicts my calculated fwi index, using only mositure temp humidiy columns. that way, this model can be applied to the microbit sensor data. i dont wanna use senro and simulated mixed, as i belive muicrobit should be a standalone functionality that works without external data.

    decided on dropping ml.... picking up tmrw 

problem: battery pack wasnt enough for gpps... fixed

GPS HUGE ISSUE FIXED NOW
radio max char was 19, srial max char is laso 19. read character by character, then split into 19 for radio, reconstructed in python. isues where the start and end headers not appearing due to buufer limits, and other values writing at the same time. now all thats left is to parse reconstructed gps lines and put al back into working... datalogger got reset..



BASE VALUE RESULT WEIGHT SETTINGS:
###############################################################################

# Weights for the different factors
                 # How much:                            for instant risk:
w_heat = 0.30    #          current temperature matters 
w_soil = 0.35    #          dry soil matters right now
w_air = 0.15     #          dry air matters right now
w_wind = 0.15    #          wind matters right now
w_rain = 0.05    #          rain pulls current risk down

                 # How much:                built-up dryness over time:
d_soil = 0.50    #          dry soil drives
d_heat = 0.25    #          heat builds 
d_air = 0.15     #          dry air builds 
d_rain = 0.10    #          rain reduces 

m_memory = 0.80  # how much the last hour still matters
m_input = 0.20   # how much this hour feeds into carryover

f_instant = 0.55 # how much current conditions matter in the final risk
f_memory = 0.45  # how much built-up dryness matters in the final risk

###############################################################################

# Bands for final risk
moderate_risk = 0.25
high_risk = 0.5
extreme_risk = 0.75

###############################################################################

The correlation heatmap and time-series graph showed that soil dryness was dominating both the instant and carry-over parts of the model, while rainfall had too little effect in lowering risk. The model was therefore tuned by slightly reducing soil-related weights, increasing rainfall influence, and reducing memory persistence so that ordinary baseline conditions would not be overstated

version 1 settings
###############################################################################

# Weights for the different factors
                 # How much:                            for instant risk:
w_heat = 0.35    #          current temperature matters 
w_soil = 0.25    #          dry soil matters right now
w_air = 0.15     #          dry air matters right now
w_wind = 0.15    #          wind matters right now
w_rain = 0.10    #          rain pulls current risk down

                 # How much:                built-up dryness over time:
d_soil = 0.40    #          dry soil drives
d_heat = 0.25    #          heat builds 
d_air = 0.15     #          dry air builds 
d_rain = 0.20    #          rain reduces 

m_memory = 0.65  # how much the last hour still matters
m_input = 0.35   # how much this hour feeds into carryover

f_instant = 0.65 # how much current conditions matter in the final risk
f_memory = 0.35  # how much built-up dryness matters in the final risk

###############################################################################

# Bands for final risk
moderate_risk = 0.25
high_risk = 0.5
extreme_risk = 0.75

###############################################################################

i think the magor issue is the base score itself is at 30, lets offset it keeping ordinary values aka ordinary weather at 0, change:
    Instead of using:
    FinalRiskScore = FinalRisk_t * 100
    use :
    AdjustedRisk = max(0, FinalRisk_t - 0.30)
    FinalRiskScore = AdjustedRisk / (1 - 0.30) * 100

Also, lets make final risk scale off and instead of or aka * isntead of +