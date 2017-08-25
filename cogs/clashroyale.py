def join2(l:list, joiner:str):
    newl = []
    for x in l:
        newl.append(str(x))
    return joiner.join(newl)

challenge = {
    'cc' : {
        'gold':[130,180,240,310,390,480,590,720,880,1080,1330,1630,2000], 
        'cards':[2,3,5,8,12,17,23,30,38,48,61,78,100],
        'goldratio':[],
        'cardsratio':[],
        'goldpercard':[],
        'goldpercardratio':[]
    },
    'gc' :{
        'gold':[1400,1900,2500,3200,4000,5000,6200,7600,9300,11500,14200,17500,22000], 
        'cards':[20,30,50,85,130,185,250,330,420,530,670,860,1100],
        'goldratio':[],
        'cardsratio':[],
        'goldpercard':[],
        'goldpercardratio':[]
    }
}
{'gold':[1400,1900,2500,3200,4000,5000,6200,7600,9300,11500,14200,17500,22000], 
    'cards':[20,30,50,85,130,185,250,330,420,530,670,860,1100],
    'goldratio':[]
}
for name in challenge:
    for index, gold in enumerate(challenge[name]['gold']):
        if index!=0:
            cgold = challenge[name]['gold']
            challenge[name]['goldratio' ].append(round(cgold[index]/cgold[index-1],3))

    for index, gold in enumerate(challenge[name]['cards']):
        if index!=0:
            ccards = challenge[name]['cards']
            challenge[name]['cardsratio'].append(round(ccards[index]/ccards[index-1],3))

    for index, gold in enumerate(challenge[name]['cards']):
        if index!=0:
            ccards = challenge[name]['cards'][index]
            cgold = challenge[name]['gold'][index]
            challenge[name]['goldpercard'].append(round(cgold/ccards,3))

for name in challenge:
    for index, gold in enumerate(challenge[name]['goldpercard']):
        if index!=0:
            cgoldpercard = challenge[name]['goldpercard']
            challenge[name]['goldpercardratio'].append(round(cgoldpercard[index]/cgoldpercard[index-1],3))

for name in challenge:
    goldratio  = challenge[name]['goldratio' ]
    cardsratio = challenge[name]['cardsratio']
    goldpercard = challenge[name]['goldpercard']
    goldpercardratio =  challenge[name]['goldpercardratio']
    print("{} gold ratio:  {}".format(name, join2(goldratio, ', ')))
    print("{} gold ratio average:  {}\n".format(name, round(sum(goldratio )/len(goldratio ),3)))
    print("{} cards ratio: {}".format(name, join2(cardsratio, ', ')))
    print("{} cards ratio average: {}\n".format(name, round(sum(cardsratio)/len(cardsratio),3)))
    print("{} goldpercard: {}".format(name, join2(goldpercard, ', ')))
    print("{} goldpercard average: {}\n".format(name, round(sum(goldpercard)/len(goldpercard),3)))
    print("{} goldpercard ratio: {}".format(name, join2(goldpercardratio, ', ')))
    print("{} goldpercard ratio average: {}\n".format(name, round(sum(goldpercardratio)/len(goldpercardratio),3)))

input()