__author__ = 'lsm'
import math

Prefer = {"tommy":{'War':2.3,'The lord of wings':3.0,'Kongfu':5.0},
       "lily":{'War':2.0,'The lord of wings':3.6,'Kongfu':4.1},
       "jim":{'War':1.9,'The lord of wings':4.0,'Beautiful America':4.7,'the big bang':1.0},
       'jack':{'War':2.8,'The lord of wings':3.5,'Kongfu':5.5}
       }
user = {1: {2: 1, 3: 1},
        2: {1:1, 3:1},
        3: {1:1,2:1,4:1},
        4: {1:1,2:1,3:1}}

def sim_distance(prefer, person1, person2):
    sim = {}
    for item in prefer[person1]:
        if item in prefer[person2]:
            sim[item] = 1       # 添加共同项到字典中#无共同项，返回0
    if len(sim) == 0:
        return 0
    # 计算所有共有项目的差值的平方和
    sum_all = sum([pow(prefer[person1][item]-prefer[person2][item], 2)for item in sim])
    # 计算欧几里得距离
    distance = math.sqrt(sum_all)
    # 返回改进的相似度函数
    return 1/(1+distance)


def sim_pearson(prefer, person1, person2):
    sim = {}
    # 查找双方都评价过的项
    for item in prefer[person1]:
        if item in prefer[person2]:
            sim[item] = 1           # 将相同项添加到字典sim中
    # 元素个数
    n = len(sim)
    if len(sim) == 0:
        return -1
    # 所有偏好之和
    sum1 = sum([prefer[person1][item] for item in sim])
    sum2 = sum([prefer[person2][item] for item in sim])
    # 求平方和
    sum1Sq = sum([pow(prefer[person1][item], 2) for item in sim])
    sum2Sq = sum([pow(prefer[person2][item], 2) for item in sim])
    # 求乘积之和 ∑XiYi
    sumMulti = sum([prefer[person1][item]*prefer[person2][item] for item in sim])

    num1 = sumMulti - (sum1*sum2/n)
    num2 = math.sqrt((sum1Sq-pow(sum1, 2)/n)*(sum2Sq-pow(sum2, 2)/n))

    if num2 == 0:
        return 0
    return num1/num2


def sim_tanimoto(prefer, person1, person2):
    sim = {}
    for item in prefer[person1]:
        if item in prefer[person2]:
            sim[item] = 1       # 添加共同项到字典中#无共同项，返回0
    n = len(sim)
    if n == 0:
        return 0
    return n/(len(prefer[person1])+len(prefer[person2])-n)


def top_k(prefer, person, k=2, sim_name=sim_pearson):
    scores = [(sim_name(prefer, person, other), other) for other in prefer if other != person]

    scores.sort(reverse=True)   # 对scores列表排序,从高到底
    return scores[0:k]          # 返回排序列表， [0:n]表示仅返回前n项

def getRecommend(prefer, person, sim_name=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefer:
        if other == person:
            continue
        else:
            sim = sim_name(prefer, person, other)    #计算比较其他用户的相似度
        # 相似度>0
        if sim <= 0:
            continue
        for item in prefer[other]:
            if item not in prefer[person]:
                # 加权平均值： 相似度*评分
                totals.setdefault(item, 0)  # 每轮循环开始时,若不存在则初始化为0
                totals[item] += prefer[other][item]*sim
                # 相似度之和
                simSums.setdefault(item, 0)
                simSums[item] += sim
    #建立归一化列表
    ranks = [(total/simSums[item], item) for item, total in totals.items()]
    #返回经排序后的列表
    ranks.sort(reverse=True)
    return ranks

if __name__ == '__main__':
    # while 1:
    #     p1 = int(input("p1:"))
    #     p2 = int(input("p2:"))
    #     print(sim_distance(user, p1, p2))
    #     print(sim_pearson(user, p1, p2))
    #     print(sim_tanimoto(user, p1, p2))

    # print(top_k(Prefer, 'tommy'))
    print(getRecommend(Prefer, 'tommy'))
    print(getRecommend(user, 1, sim_tanimoto))