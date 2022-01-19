from collections import defaultdict
non_terminals=set()
terminals=set()
grammar=[]
f=open("test1.txt","r")
first_table=defaultdict(set)
follow_table=defaultdict(set)

for production in f:
    grammar.append(production.strip())
    non_terminals.add(production[0])

start_symbol=grammar[0].split("->")[0]

for production in grammar:
    for token in production.strip().replace("->", ""):
        if token not in non_terminals:
            terminals.add(token)

def first_cal(x):
    if x in first_table:
        return first_table[x]
    if x in non_terminals:
        first=set()
        s=[]
        for i in grammar:
            temp=i.split("->")
            if temp[0]==x:
                for k,j in enumerate(temp[1]):
                    if j==x:
                        if k+1<len(temp[1]):
                            s.append(temp[1][k+1:])
                            break
                    else:
                        fst=first_cal(j)
                        if j!=temp[1][-1]:
                            fst.discard("@")
                            first|=fst
                        else:
                            first|=fst
                        if "@" not in fst:
                            break
        if "@" in first:
            for i in s:
                for j in i:
                    first|=first_cal(j)
                    if "@" not in first:
                        break
                    if j!=i[-1]:
                        first.discard("@")
        return first
    else:
        return {x}

def follow_cal(x):
    if x in terminals:
        print("Follow of a terminals don't exist")
        return
    if x in follow_table:
        return follow_table[x]
    follow_table[x]=set()
    if x==start_symbol:
        follow_table[x].add("$")
    for i in grammar:
        temp = i.split("->")
        pos=temp[1].find(x)
        if pos!=-1:
            for j in temp[1][pos+1:]:
                follow_table[x]|=first_cal(j)
                if '@' not in follow_table[x] and (j!=x):
                    break
                follow_table[x].discard("@")
            else:
                if temp[0]!=temp[1][-1]:
                    follow_table[x]|=follow_cal(temp[0])
    return follow_table[x]

for i in non_terminals:
    first_table[i]=first_cal(i)
    print(i,first_table[i])

for i in non_terminals:
    follow_table[i]=follow_cal(i)
    print(i,follow_table[i])