#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import talib as tb

#%%
df = pd.read_excel("C:\\Users\\l_cry\\Desktop\\data\\中债国开债到期收益率.xls")
df.columns = ['date', 'yield_5', 'yield_10']
# df.set_index(["date"], inplace=True)
df['yield_diff'] = (df['yield_10'] - df['yield_5'])*100
df['yield_diff_chg'] = (df['yield_diff']-df['yield_diff'].shift(1))


#%%
down_list,re1_list,up_list,re2_list,profits = max_L(38, 20, 2, 0, 0.4, 0.2, 1.251251802718635, 0.9889443968553655,df)
fig,(ax1,ax2) = plt.subplots(2,sharex=True,figsize=(1200/72,480/72))

ax1.plot(df.date, df.yield_diff)
ax1.plot(df.date, ma_define(df.yield_diff, df.yield_diff_chg.abs(),20))


ax1.plot(df['date'].iloc[down_list], df.yield_diff.iloc[down_list],'o')
ax1.plot(df['date'].iloc[re1_list], df.yield_diff.iloc[re1_list],'o')
ax2.plot(df.date, df.yield_diff_chg)

plt.show()



#%%
def vola(arr,n):
    # res = np.zeros(len(arr))
    # for i in range(0, len(arr), 1):
    #     if i < n-1:
    #
    #         res[i] = np.NaN
    #     else:
    #         res[i] = np.std(arr[i-n+1:i])
    # return res
    return tb.EMA(arr**2, n)


def ma_define(arr, weigh,n):
    res = np.zeros(len(arr))
    for i in range(0, len(arr), 1):
        if i < n-1:
            res[i] = np.NaN
        else:
            res[i] = arr[i-n+1:i].dot(weigh[i-n+1:i])/sum(weigh[i-n+1:i])
    return res


#%%
def max_L(MA_n, vola_n, th1, re1, th2, re2, a, b, df, start=100, end=900):
    df['diff_chg_vola'] = vola(df.yield_diff_chg, vola_n)
    # df['diff_SMA'] = tb.SMA(df.yield_diff, SMA_n)
    df['diff_MA'] = ma_define(df.yield_diff, a*(df.yield_diff_chg.abs())**b, MA_n)
    down_list = []
    up_list = []
    re1_list = []
    re2_list = []
    profits = 0
    down_set = set()
    up_set = set()
    for i in range(start,end,1):
        if df.loc[i, 'yield_diff'] > df.loc[i, 'diff_MA'] and (df.loc[i, 'yield_diff'] - df.loc[i, 'diff_MA'])/df.loc[i, 'diff_chg_vola'] > th1:
            down_list.append(i)
            down_set.add(df.loc[i, 'yield_diff'])
        elif (df.loc[i, 'yield_diff'] - df.loc[i, 'diff_MA'])/df.loc[i, 'diff_chg_vola'] < re1:
            if len(down_set) > 0:
                re1_list.append(i)
                profits += sum(np.array([price for price in down_set])-df.loc[i, 'yield_diff'])
                down_set.clear()
        elif df.loc[i, 'yield_diff'] <= df.loc[i, 'diff_MA'] and (df.loc[i, 'diff_MA'] - df.loc[i, 'yield_diff'])/df.loc[i, 'diff_chg_vola'] > th2:
            up_list.append(i)
            up_set.add(df.loc[i, 'yield_diff'])
        elif (df.loc[i, 'diff_MA'] - df.loc[i, 'yield_diff'])/df.loc[i, 'diff_chg_vola'] < re2:
            if len(up_set) > 0:
                re2_list.append(i)
                profits += sum(df.loc[i, 'yield_diff'] - np.array([price for price in up_set]))
                up_set.clear()
    return down_list,re1_list,up_list,re2_list,profits

#%%
def max_L1(MA_n, vola_n, a, b, df, start=100, end=900):
    df['diff_chg_vola'] = vola(df.yield_diff_chg, vola_n)
    # df['diff_SMA'] = tb.SMA(df.yield_diff, SMA_n)
    df['diff_MA'] = ma_define(df.yield_diff, a*(df.yield_diff_chg.abs())**b, MA_n)
    down_list = []
    up_list = []
    re1_list = []
    re2_list = []
    profits = 0
    down_set = set()
    up_set = set()
    for i in range(start,end,1):
        if df.loc[i-1, 'yield_diff'] > df.loc[i, 'diff_MA'] and df.loc[i, 'yield_diff'] <= df.loc[i, 'diff_MA']:
            down_list.append(i)
            down_set.add(df.loc[i, 'yield_diff'])
            if len(up_set) > 0:
                re2_list.append(i)
                profits += sum(df.loc[i, 'yield_diff'] - np.array([price for price in up_set]))
                up_set.clear()
        elif df.loc[i-1, 'yield_diff'] < df.loc[i, 'diff_MA'] and df.loc[i, 'yield_diff'] >= df.loc[i, 'diff_MA'] :
            up_list.append(i)
            up_set.add(df.loc[i, 'yield_diff'])
            if len(down_set) > 0:
                re1_list.append(i)
                profits += sum(np.array([price for price in down_set])-df.loc[i, 'yield_diff'])
                down_set.clear()
    return down_list,re1_list,up_list,re2_list,profits

#%%
import random
from deap import tools
from deap import base, creator

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register('SMA_n',random.randint,10,60)
toolbox.register('vola_n',random.randint,10,30)
toolbox.register('th1',random.uniform,2,4)
toolbox.register('re1',random.uniform,-2,2)
toolbox.register('th2',random.uniform,2,4)
toolbox.register('re2',random.uniform,-2,2)
toolbox.register('a',random.uniform,0.5,2)
toolbox.register('b',random.uniform,0.5,2)

toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.SMA_n,
                  toolbox.vola_n,
                  toolbox.th1,
                  toolbox.re1,
                  toolbox.th2,
                  toolbox.re2,
                  toolbox.a,
                  toolbox.b
                  ), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def evaluate(x):
    return abs(max_L(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],df)[-1])
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
                if child[0] > 60:
                    child[0] = 60
                elif child[0] <10:
                    child[0] = 10
                child[0] = int(child[0])
                if child[1] > 40:
                    child[1] = 40
                elif child[1] < 10:
                    child[1] = 10
                child[1] = int(child[1])
                if child[2] > 4:
                    child[2] = 4
                elif child[2] < 2:
                    child[2] = 2

                if child[3] > 2:
                    child[3] = 2
                elif child[3] < -2:
                    child[3] = -2
                if child[4] > 4:
                    child[4] = 4
                elif child[4] < 2:
                    child[4] = 2
                if child[5] > 2:
                    child[5] = 2
                elif child[5] < -2:
                    child[5] = -2
                if child[6] > 4:
                    child[6] = 4
                elif child[6] < 0.5:
                    child[6] = 0.5
                if child[7] > 4:
                    child[7] = 4
                elif child[7] < 0.5:
                    child[7] = 0.5
            return offspring
        return wrapper
    return decorator
toolbox.decorate("mate", checkBounds(3, 20))
toolbox.decorate("mutate", checkBounds(3, 20))


def main():
    pop = toolbox.population(n=100)
    CXPB, MUTPB, NGEN = 0.5, 0.2, 50

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























