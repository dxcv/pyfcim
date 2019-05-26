import numpy as np

def ga(FITNESSFCN,NVARS,A,b,Aeq,beq,lb,ub,NONLCON,INTCON,eps=0.01,popsize=100,NGEN=50,CXPB=0.8,MUTPB=0.3):
    n = np.ceil(np.log2((ub-lb)/eps))
    gelens = 2**n
    totalgelen = np.sum(n)
    pop = np.random.randint(0,2,size=(popsize,totalgelen))

    def bi2num(bis):
        num = np.zeros(bis.shape)
        index = np.cumsum(n)
        for i in np.arange(n):
            num[:,i] = np.sum(bis[index[i] - n[i], index[i] - 1][j] * 2**j for j in np.arange(len(bis[index[i] - n[i], index[i] - 1])))/gelens*(ub[i]-lb[i])+lb[i]
        return num

    pop.fitness = list(map(FITNESSFCN,bi2num(pop)))

    def selectBest(self, pop):
        '''
        select the best individual from pop
        '''
        s_inds = sorted(pop, key=pop.fitness, reverse=False)
        return s_inds[0]

    bestindividual = selectBest(pop)

    def selection(self, individuals, k):
        '''
        select two individuals from pop
        '''
        s_inds = sorted(individuals, individuals.fitness,
                        reverse=True)  # sort the pop by the reference of 1/fitness
        sum_fits = sum(1 / ind.fitness for ind in individuals)  # sum up the 1/fitness of the whole pop

        chosen = []
        for i in np.arange(k):
            u = np.random.random() * sum_fits  # randomly produce a num in the range of [0, sum_fits]
            sum_ = 0
            for ind in s_inds:
                sum_ += 1 / ind.fitness  # sum up the 1/fitness
                if sum_ > u:
                    # when the sum of 1/fitness is bigger than u, choose the one, which means u is in the range of [sum(1,2,...,n-1),sum(1,2,...,n)] and is time to choose the one ,namely n-th individual in the pop
                    chosen.append(ind)
                    break
        return chosen

    def crossoperate(self, offspring):
        '''
        cross operation
        '''
        dim = len(offspring[0])
        geninfo1 = offspring[0] # Gene's data of first offspring chosen from the selected pop
        geninfo2 = offspring[1] # Gene's data of second offspring chosen from the selected pop
        pos1 = np.random.randint(1, dim)  # select a position in the range from 0 to dim-1,
        pos2 = np.random.randint(1, dim)

        temp = np.zeros(dim)

        temp[0:min(pos1,pos2)] = geninfo1[0:min(pos1,pos2)]
        temp[max(pos1, pos2):dim] = geninfo1[min(pos1, pos2):dim]
        temp[min(pos1,pos2),max(pos1,pos2)] = geninfo2[min(pos1,pos2),max(pos1,pos2)]
        temp.fitness = FITNESSFCN(bi2num(temp))

        return temp

    def mutation(self, offspring):
        '''
        mutation operation
        '''

        dim = len(offspring)
        temp = np.zeros(dim)
        pos = np.random.randint(1, dim)  # chose a position in crossoff to perform mutation.
        temp = offspring
        temp[pos] = 1-temp[pos]
        temp.fitness = FITNESSFCN(bi2num(temp))
        return temp


    ###############

    print("Start of evolution")

    # Begin the evolution
    for g in range(NGEN):

        print("-- Generation %i --" % g)

        # Apply selection based on their converted fitness
        selectpop = selection(pop, popsize)

        nextoff = selectpop
        while len(nextoff) != popsize:
            # Apply crossover and mutation on the offspring

            # Select two individuals
            offspring = [np.random.choice(selectpop) for i in np.arange(2)]

            if np.random.random() < CXPB:  # cross two individuals with probability CXPB
                crossoff = crossoperate(offspring)
                nextoff.append(crossoff)

            if np.random.random() < MUTPB:  # mutate an individual with probability MUTPB
                muteoff = mutation(np.random.choice(selectpop))
                nextoff.append(muteoff)

        # The population is entirely replaced by the offspring
        pop = nextoff

        # Gather all the fitnesses in one list and print the stats
        fits = [ind['fitness'] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5
        best_ind = selectBest(pop)

        if best_ind.fitness < bestindividual.fitness:
            bestindividual = best_ind

        print("Best individual found is %s, %s" % (bestindividual, bestindividual.fitness))
        print("  Min fitness of current pop: %s" % min(fits))
        print("  Max fitness of current pop: %s" % max(fits))
        print("  Avg fitness of current pop: %s" % mean)
        print("  Std of currrent pop: %s" % std)

    print("-- End of (successful) evolution --")



