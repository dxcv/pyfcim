#%%
import pandas as pd
import numpy as np
import talib as tb
import matplotlib.pyplot as plt
import mpl_finance as mpf
import matplotlib.dates as mdates


#%%
data = pd.read_csv('C:/Users/l_cry/Desktop/data/MLtimingdata150107_181120TFCFE.csv')
data.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
data = data.fillna(method="ffill", axis=0)
data['HIGH1'] = data.HIGH.shift(-1)
data['HIGH2'] = data.HIGH.shift(-2)
data['HIGH3'] = data.HIGH.shift(-3)
data['HIGH4'] = data.HIGH.shift(-4)
data['HIGH5'] = data.HIGH.shift(-5)
data['HIGH6'] = data.HIGH.shift(-6)
data['HIGH7'] = data.HIGH.shift(-7)
data['maxHigh'] = data[['HIGH1', 'HIGH2', 'HIGH3', 'HIGH4', 'HIGH5', 'HIGH6']].max(axis=1)
data['HIGH_CHG'] = np.log(data['maxHigh']/data.CLOSE)*100
data['CLOSE7'] = data.CLOSE.shift(-7)
data['CLOSE1'] = data.CLOSE.shift(-1)
data['CLOSE_CHG_7'] = np.log(data.CLOSE7/data.CLOSE)*100
data['CLOSE_CHG'] = np.log(data.PCT_CHG/100+1)*100
data['CLOSE_CHG_1'] = np.log(data.CLOSE1/data.CLOSE)*100
data['LOW1'] = data.LOW.shift(-1)
data['LOW2'] = data.LOW.shift(-2)
data['LOW3'] = data.LOW.shift(-3)
data['LOW4'] = data.LOW.shift(-4)
data['LOW5'] = data.LOW.shift(-5)
data['LOW6'] = data.LOW.shift(-6)
data['minLOW'] = data[['LOW1','LOW2','LOW3','LOW4','LOW5','LOW6']].max(axis=1)
data['LOW_CHG'] = np.log(data['minLOW']/data.CLOSE)*100
data = data[data.CLOSE_CHG_7.notnull()].reset_index(drop=True)
#all_factorlist = "atr,bias,cci,dma,dmi,dpo,macd,mtm,priceosc,roc,rsi,sar,si"
all_factorlist = "PCT_CHG,atr,bias,dma,dmi,dpo,macd,mtm,priceosc,roc,rsi,sar,si"
factorlist = all_factorlist.upper().replace(' ', '').split(",")
datelist = data['date']


# #%%
# data['EMA'] = tb.SMA(data['CLOSE'],20)
#
# def find_localmax(arr1):
#     return np.array([arr1[i] for i in range(1,len(arr1)-1,1) if arr1[i]>arr1[i-1] and arr1[i]>arr1[i+1]])
#
#
# res = (data['HIGH']-data['EMA'])/tb.ATR(data['HIGH'],data['LOW'],data['CLOSE'])
# localmaxarr = find_localmax(res.dropna().values)
#
#
# #%%
# plt.plot(localmaxarr[localmaxarr>0])
# plt.show()
# #%%
# plt.hist(localmaxarr[localmaxarr>0],20)
# plt.show()
#
# #%%
# diff = data['HIGH']-data['EMA']
# plt.plot(diff[diff>0]/tb.ATR(data['HIGH'],data['LOW'],data['CLOSE']))
# plt.show()
# #%%
# plt.hist((diff[diff>0]/tb.ATR(data['HIGH'],data['LOW'],data['CLOSE'])).dropna().values,20)
# plt.show()
# #%%
# plt.figure(figsize=(10,5))
# plt.plot(diff/tb.ATR(data['HIGH'],data['LOW'],data['CLOSE']))
# plt.twinx()
# plt.plot(data['CLOSE'],'r')
# plt.show()
#
# #%%
# plt.figure(figsize=(10,5))
# plt.plot(tb.ATR(data['HIGH'],data['LOW'],data['CLOSE']))
# plt.twinx()
# plt.plot(data['CLOSE'],'r')
# plt.show()
#
#
#%%
data["date"]=pd.to_datetime(data["date"])
data['SMA_l'] = tb.SMA(data['CLOSE'],20)
data['SMA_s'] = tb.SMA(data['CLOSE'],5)

#将时间数据转换为matplotlib的时间格式
data['date'] = data['date'].apply(lambda d: mdates.date2num(d.to_pydatetime()))

#%%
fig,(ax1,ax2) = plt.subplots(2,sharex=True,figsize=(1200/72,480/72))
fig.subplots_adjust(bottom=0.1)
mpf.candlestick_ochl(ax1, data[['date','OPEN','CLOSE','HIGH','LOW']].dropna(1).values,colordown='#53c156', colorup='#ff1717',width=0.3,alpha=1)
ax1.plot(data['date'],data['SMA_l'])
ax1.plot(data['date'],data['SMA_s'])
ax1.grid(True)
ax1.xaxis_date()
#
ax2.stem(data['date'].iloc[in_point+in_point2],[1 for i in in_point+in_point2])

#ax2.plot(data['date'],tb.ATR(data['HIGH'],data['LOW'],data['CLOSE']))
plt.show()


#%%
# 超跌买入策略
def max_L(MA_period_s,MA_period_l,atr_period,threshold1,threshold2,data,start=100,end=600):
    data['SMA_s'] = tb.SMA(data['CLOSE'], int(MA_period_s)).shift(1)
    data['SMA_l'] = tb.SMA(data['CLOSE'], int(MA_period_l)).shift(1)
    data['ATR'] = tb.ATR(data['HIGH'], data['LOW'], data['CLOSE'],int(atr_period)).shift(1)
    # data['SMA_s'] = tb.SMA(data['CLOSE'], int(MA_period_s))
    # data['SMA_l'] = tb.SMA(data['CLOSE'], int(MA_period_l))
    # data['ATR'] = tb.ATR(data['HIGH'], data['LOW'], data['CLOSE'], int(atr_period))
    data['MA_percentile'] = ((data['SMA_s']-data['SMA_l'])/data['ATR']).apply(lambda x:x if x<0 else 0)
    data['percentile'] = ((data['LOW']-data['SMA_s'])/data['ATR']).apply(lambda x:x if x<0 else 0)
    num = 0
    wins = 0
    in_point = []
    for i, row in data.iloc[start:end,:].iterrows():
        if row['MA_percentile'] < threshold1 and row['percentile'] < threshold2:
            in_point.append(i)
            num += 1
            if data.iloc[i:i+3,:]['LOW'].max()>row['LOW']:
                wins += 1
    return wins/num if num!=0 else 0,num,wins,2*wins-num,in_point
#%%
import random
from deap import tools
from deap import base, creator

IND_SIZE = 10
creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register('MA_period_s',random.randint,3,10)
toolbox.register('MA_period_l',random.randint,10,20)
toolbox.register('atr_period',random.randint,10,20)
toolbox.register('threshold1',random.uniform,1,-0.01)
toolbox.register('threshold2',random.uniform,1,-0.01)
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.MA_period_s,
                  toolbox.MA_period_l,
                  toolbox.atr_period,
                  toolbox.threshold1,
                  toolbox.threshold2,
                  ), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def evaluate(x):
    return abs(max_L(x[0],x[1],x[2],x[3],x[4],data)[0]-0.71)
    # return max_L(x[0],x[1],x[2],x[3],x[4],data)[-1]

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)
def checkBounds(min, max):
    def decorator(func):
        def wrapper(*args, **kargs):
            offspring = func(*args, **kargs)
            for child in offspring:
                for i in range(len(child)-2):
                    if child[i] > max:
                        child[i] = max
                    elif child[i] < min:
                        child[i] = min
                    else:
                        child[i] = int(child[i])

                    if child[-2] > -0.01:
                        child[-2] = -0.01
                    elif child[-2] < -5:
                        child[-2] = -5

                    if child[-1] > -0.01:
                        child[-1] = -0.01
                    elif child[-1] < -5:
                        child[-1] = -5
            return offspring
        return wrapper
    return decorator
toolbox.decorate("mate", checkBounds(3, 20))
toolbox.decorate("mutate", checkBounds(3, 20))


def main():
    pop = toolbox.population(n=100)
    CXPB, MUTPB, NGEN = 0.5, 0.2, 5

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit,

    for g in range(NGEN):
        print("-- Generation %i --" % g)
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = list(map(toolbox.evaluate, invalid_ind))
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit,

        # The population is entirely replaced by the offspring
        pop[:] = offspring

        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)
        print("  best %s" % pop[fits.index(max(fits))])

    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))

    return best_ind


if __name__ == "__main__":
    main()



