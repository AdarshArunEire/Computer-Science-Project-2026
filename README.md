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


