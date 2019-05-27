# 转债数据
from scripts.波动率计算 import *
df1 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113009广汽转债")
df2 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113021中信转债")
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="110053苏银转债")
df['Mean'] = SMA(df.close.values, 30)
df['Std'] = STD(df.close.values, 30)
a = 60
df2 = df2.fillna(method='ffill')
df['Mean'] = SMA(df.close.values, a)
df['Std'] = STD(df.close.values, 20, a)
df['KAMA'] = talib.KAMA(df.close, 30)
df1['KAMA'] = talib.KAMA(df1.close, 30)
df2['KAMA'] = talib.KAMA(df2.close, 120)
temp = (df.close - df['KAMA'].shift(1)).dropna()
temp1 = (df1.close - df1['KAMA'].shift(1)).dropna()

# GA计算
from gaft import GAEngine
from gaft.components import BinaryIndividual, Population
from gaft.operators import RouletteWheelSelection, UniformCrossover, FlipBitMutation
from scripts.波动率计算 import *
# Analysis plugin base class.
from gaft.plugin_interfaces.analysis import OnTheFlyAnalysis
from gaft.analysis.fitness_store import FitnessStore
from math import sin, cos



def ga(df, start, end, _positionList, ranges=[(20,100),(0.01, 1),(0.01, 1),(0.01, 1),(1, 5)], eps=0.01):
    indv_template = BinaryIndividual(ranges=ranges, eps=eps)
    population = Population(indv_template=indv_template, size=100)
    population.init()  # Initialize population with individuals.
    # Use built-in operators here.
    selection = RouletteWheelSelection()
    crossover = UniformCrossover(pc=0.8, pe=0.5)
    mutation = FlipBitMutation(pm=0.3)
    engine = GAEngine(population=population, selection=selection,
                      crossover=crossover, mutation=mutation,
                      analysis=[FitnessStore])

    @engine.fitness_register
    def fitness(indv):
        n, upper, lower, adds, cutoff = indv.solution
        df['KAMA'] = talib.KAMA(df.close, int(n))
        df['VAR'] = talib.VAR(df.close-df.KAMA.shift(1) - df.close.shift(1)+df.KAMA.shift(2),10)
        profitsList, buypriceList, sellpriceList, fits,positionList = profitsCal(df, start, end, _positionList, upper=upper, lower=lower, adds = adds, cutoff=cutoff)
        return float(fits)

    @engine.analysis_register
    class ConsoleOutput(OnTheFlyAnalysis):
        master_only = True
        interval = 1
        def register_step(self, g, population, engine):
            best_indv = population.best_indv(engine.fitness)
            msg = 'Generation: {}, best fitness: {:.3f}'.format(g, engine.fmax)
            print(best_indv.solution)
            engine.logger.info(msg)
    engine.run(ng=30)

    return population.best_indv(engine.fitness).solution, _positionList

yieldList = []
positionList = []
for i in range(4000,6500,500):
    best_ind, _positionList = ga(df2, i-2900, i, positionList)
    n, upper, lower, adds, cutoff = best_ind
    df2['KAMA'] = talib.KAMA(df2.close, int(n))
    profitsList, buypriceList, sellpriceList, fits, positionList = profitsCal(df2, i, i+500, positionList, upper=upper, lower=lower, adds=adds,
                                                                cutoff=cutoff)
    yieldList.append(fits)

#df1
# [55.390625, 0.70609375, 0.3503125, 0.01, 4.265625]
# [64.90234375, 0.73703125, 0.3503125, 0.14921875, 4.875]
# [86.89453125, 0.55140625, 0.24203125, 0.64421875, 2.953125]
# [99.78515625, 0.52046875, 0.5978125, 0.79890625, 1.125]

df2
[97.55859375, 0.9071875, 0.38125, 0.10281249999999999, 3.1875]
[66.46484375, 0.86078125, 0.01, 0.08734375, 4.359375]
[62.75390625, 0.4740625, 0.27296875, 0.01, 4.109375]
[61.015625, 0.4121875, 0.30390625, 0.05640625, 2.828125]
[30.37109375, 0.4740625, 0.02546875, 0.87625, 1.640625]





##statmodels序列平稳性计算
import statsmodels.formula.api as smf
import statsmodels.api as sm

# 广汽转债
# n, upper, lower, adds, cutoff = [82.98828125, 0.984375, 0.3109375, 0.21109375, 4.1875]
# df1['KAMA'] = talib.KAMA(df1.close, int(n))
# profitsList, buypriceList, sellpriceList, fits = profitsCal(df1, 1000, 7000, upper=upper, lower=lower, adds = adds, cutoff=cutoff)
#
# 苏银转债
n, upper, lower, adds, cutoff = [30.37109375, 0.4740625, 0.02546875, 0.87625, 1.640625]
df2['KAMA'] = talib.KAMA(df2.close, int(n))
profitsList, buypriceList, sellpriceList, fits, positionList = profitsCal(df2, 4000, 6000, [], upper=upper, lower=lower, adds = adds, cutoff=cutoff)
#
# 中信转债
# n, upper, lower, adds, cutoff = [80.8203125, 0.609375, 0.453125, 0.02546875, 2.96875]
# df2['KAMA'] = talib.KAMA(df2.close, int(n))
# profitsList, buypriceList, sellpriceList, fits = profitsCal(df2, 100, 3000, upper=upper, lower=lower, adds = adds, cutoff=cutoff)


temp2 = STD(df2.close.values,100)
plt.plot(temp2)
plt.show()


#####
# 波动率建模
temp = (df.close - df.KAMA.shift(1)).dropna().values
plt.hist(temp,100)
plt.show()

plt.plot(temp)
plt.show()

temp1 = talib.VAR(df.close-df.KAMA.shift(1) - df.close.shift(1)+df.KAMA.shift(2), 60)
plt.plot(temp1)
plt.show()

temp = df.close - df.KAMA.shift(1)
df['VAR'] = talib.VAR(temp,30)
temp/np.sqrt(df.VAR)
temp2 = scipy.stats.norm.cdf((temp/np.sqrt(df.VAR)).dropna())

scipy.stats.probplot((temp/np.sqrt(df.VAR)).dropna(), plot=plt)
plt.show()