from copy import deepcopy
from collections import defaultdict
# Declaring All Variables

grammar = []
new_grammar = []
terminals = []
non_terminals = []
first_table = defaultdict(set)
follow_table = defaultdict(set)
Item = {}
shift_list = []
reduce_list = []
action_list = []
rule_dict = {}
SR = []
RR = []
start_symbol = ""


def read_grammar():
    file_name = input("Enter Input Grammar File Name: ")
    # open input grammar file
    try:
        grammar_file = open(file_name, "r")
    except:
        print("Cannot Find Input Grammar File With Name", file_name)
        exit(0)
    # adding garmmar to grammar container
    for production in grammar_file:
        grammar.append(production.strip())
        # adding non-terminals to non_terminals container
        if production[0] not in non_terminals:
            non_terminals.append(production[0])

    # adding terminals to terminals container
    for production in grammar:
        temp=production.strip().replace(" ", "").replace("->", "")
        for token in temp:
            if token in terminals:
                continue
            if token  in non_terminals:
                continue
            terminals.append(token)

    # rules of grammar
    for l in range(1, len(grammar) + 1):
        rule_dict[l] = grammar[l - 1]


def augment_grammar():
    #Adding new start symbol
    if "'" not in grammar[0]:
        grammar.insert(0, grammar[0][0] + "'" + "->" + grammar[0][0])
    # Adding. in fornt of each rule
    for production in grammar:
        idx = production.index(">")
        production = production[:idx + 1] + "." + production[idx + 1:]
        new_grammar.append(production)


def Item0():
    temp = []
    # add first rule to I(0)
    temp.append(new_grammar[0])
    # check for terminals in new_grammar[0]
    for each_item in temp:
        curr_var = each_item[each_item.index(".")+ 1]
        if curr_var in non_terminals:
            for each_item in new_grammar:
                if each_item[0] == curr_var and each_item not in temp:
                    temp.append(each_item)
    Item[0] = temp

def Collection():
    Item0()
    variables = non_terminals + terminals
    i,curr,done = 0,0,False
    while not done:
        for each_variable in variables:
            temp = []
            try:
                for each_production in Item[curr]:
                    if each_production[-1] == ".":
                        continue
                    idx = each_production.index(".")
                    if each_production[idx + 1] == each_variable:
                        rule = deepcopy(each_production).replace(".", "")
                        rule = rule[:idx + 1] + "." + rule[idx + 1:]
                        temp.append(rule)
                        for rule in temp:
                            idx = rule.index(".")
                            if rule[-1] == ".":
                                pass
                            else:
                                curr_var = rule[idx + 1]
                                if curr_var in non_terminals:
                                    for each_production in new_grammar:
                                        if each_production[0] == curr_var and each_production[
                                            1] != "'" and each_production not in temp:
                                            temp.append(each_production)
            except:
                done = True
                break
            if temp:
                if temp not in Item.values():
                    i += 1
                    Item[i] = temp

                for k, v in Item.items():
                    if temp == v:
                        idx = k
                shift_list.append([curr, each_variable, idx])
        curr += 1

def Conflict():
    conflict = False
    # RR conflict arises if 2 Reduce occurs for the same condition
    for i in reduce_list:
        for j in reduce_list:
            if i == j:
                continue
            if i[:2] == j[:2]:
                RR.append(i)
                conflict = True
    # SR conflict arises if shift and Reduce occurs for same condition
    for i in shift_list:
        for j in reduce_list:
            if i[:2] == j[:2]:
                SR.append([i, j])
                conflict = True
    return conflict

def first_cal(x):
    if x in first_table:
        return first_table[x]
    # if x is terminals then we don't need to go further
    if x in non_terminals:
        first = set()
        ''' s is a temporary list to store the production of type in which the variable for which we want to find first
            is repeated on the left side like A->BAC, so we have to wait to go to C non-terminal only and only if the 
            first of A contains a null symbol that is @
        '''
        s = []
        for i in new_grammar:
            temp = i.replace(".","").split("->")
            if temp[0] == x:
                for k, j in enumerate(temp[1]):
                    if j == x:
                        if k + 1 < len(temp[1]):
                            s.append(temp[1][k + 1:])
                            break
                    else:
                        fst = first_cal(j)
                        if j != temp[1][-1]:
                            fst.discard("@")
                            first |= fst
                        else:
                            first |= fst
                        if "@" not in fst:
                            break
        if "@" in first:
            for i in s:
                for j in i:
                    first |= first_cal(j)
                    if "@" not in first:
                        break
                    if j != i[-1]:
                        first.discard("@")
        return first
    else:
        return {x}


def follow_cal(x):
    global start_symbol
    if x in terminals:
        print("Follow of a terminals don't exist")
        return
    if x in follow_table:
        return follow_table[x]
    follow_table[x] = set()
    if x == start_symbol:
        follow_table[x].add("$")
    for i in new_grammar:
        temp = i.replace(".","").split("->")
        pos = temp[1].find(x)
        if pos != -1:
            for j in temp[1][pos + 1:]:
                follow_table[x] |= first_cal(j)
                if '@' not in follow_table[x] and (j != x):
                    break
                follow_table[x].discard("@")
            else:
                if temp[0] != temp[1][-1]:
                    follow_table[x] |= follow_cal(temp[0])
    return follow_table[x]


def reduction():
    reduce_list.append([1, "$", "Accept"])
    for i in Item.items():
        try:
            for each_production in i[1]:
                if each_production[-1] == ".":
                    lhs = each_production[:len(each_production) - 1]
                    for rule in rule_dict.items():
                        if lhs == rule[1]:
                            f = follow_cal(lhs[0])
                            for each_var in f:
                                reduce_list.append([i[0], each_var, "R" + str(rule[0])])
        except:
            pass


def test(string):
    done = False
    stack = []
    stack.append(0)
    print("\n\nSTACK\t\tSTRING\t\tACTION")
    while not done:
        Reduce = False
        Shift = False
        # Check for reduction
        for i in reduce_list:
            # Reduce
            if i[0] == int(stack[-1]) and i[1] == string[0]:
                Reduce = True
                print(''.join(str(j) for j in stack), f"\t\t {string}\t\t Reduce {i[2]}")
                if i[2] == 'Accept':
                    return 1
                var = rule_dict[int(i[2][1])]
                sp = var.split("->")
                lhs = sp[0]
                rhs = sp[1]

                for x in range(len(rhs)):
                    stack.pop()
                    stack.pop()
                stack.append(lhs)

                for a in shift_list:
                    if a[0] == int(stack[-2]) and a[1] == stack[-1]:
                        stack.append(str(a[2]))
                        break
                break
        # Check for shift
        for i in shift_list:
            if i[0] == int(stack[-1]) and i[1] == string[0]:
                Shift = True
                print(''.join(str(j) for j in stack), f"\t\t {string} \t\t Shift S{i[2]}")
                stack.extend([string[0],str(i[2])])
                string = string[1:]
        if not Reduce and not Shift:
            print(''.join(str(p) for p in stack), f"\t\t {string}")
            # print "---NOT ACCEPTED---"
            return 0

def main():
    read_grammar()
    print("\n--------------------GRAMMAR PRODUCTIONS------------------------------\n")
    for item in rule_dict.items():
        print(item)
    augment_grammar()

    print("\n--------------------AUGMENTED GRAMMAR PRODUCTIONS--------------------\n")
    for item in new_grammar:
        print(item.replace(".", ""))

    global start_symbol
    start_symbol=new_grammar[0].split("->")[0]
    non_terminals.append(start_symbol)

    for i in non_terminals:
        first_table[i] = first_cal(i)

    for i in non_terminals:
        follow_table[i] = follow_cal(i)

    Collection()
    print("\n--------------------COLLECTION OF ITEMS------------------------------\n")
    for item in Item.items():
        print(item)

    print("\n--------------------GOTO OPERATIONS----------------------------------\n")
    for item in shift_list:
        print(item)

    reduction()
    print("\n--------------------REDUCTION----------------------------------------\n")
    for item in reduce_list:
        print(item)
    action_list.extend(shift_list)
    print("")
    print("Terminals:", terminals)
    print("NonTerminals:", non_terminals)
    print("")
    print("First Table")
    for i in first_table:
        print(i, ":", first_table[i])
    print("")
    print("Follow Table")
    for i in follow_table:
        print(i, ":", follow_table[i])
    print("")
    if Conflict():
        if RR != []:
            print("RR conflict")
            for item in RR:
                print(item)
            print("")
        if SR != []:
            print("SR conflict")
            for item in SR:
                print(item)
            print("")
        exit(0)
    else:
        print("NO CONFLICT")
    action_list.extend(reduce_list)
    string = input("\nEnter Test String: ")
    try:
        if string[-1] != "$":
            string = string + "$"
    except:
        print("InputError")
        exit(0)
    result = test(string)
    if result == 1:
        print("---ACCEPTED---")
    elif result == 0:
        print("---NOT ACCEPTED---")
    return 0

if __name__ == '__main__':
    main()
