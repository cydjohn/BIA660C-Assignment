import csv
import ast
from dateutil import parser

from collections import OrderedDict
from collections import defaultdict

class DataFrame(object):

    @classmethod
    def from_csv(cls, file_path, delimiting_character=',', quote_character='"'):
        with open(file_path, 'rU') as infile:
            reader = csv.reader(infile, delimiter=delimiting_character, quotechar=quote_character)
            data = []

            for row in reader:
                data.append(row)

            return cls(list_of_lists=data)


    def __init__(self, list_of_lists, header=True):
        if header:
            self.header = list_of_lists[0]
            self.data = list_of_lists[1:]
        else:
            self.data = list_of_lists
            self.header = ['column' + str(index + 1) for index, column in enumerate(self.data[0])]
           

        for i in range(len(self.header)):
            for j in range(len(self.data)):
                try:
                    tmp=ast.literal_eval(self.data[j][i])
                    if isinstance(tmp, type(self.data[0][i])):
                        self.data[j][i]=tmp
                    else:
                        self.data[j][i] = float(self.data[j][i].replace(',',''))
                except:
                    try:
                        self.data[j][i] = parser.parse(self.data[j][i])
                    except:
                         pass

        self.data = [OrderedDict(zip(self.header, row)) for row in self.data]

 
    def __getitem__(self, item):
        # this is for rows only
        if isinstance(item, (int, slice)):
            return self.data[item]

        # this is for columns only
        elif isinstance(item, str):
            return Series([row[item] for row in self.data])


        # this is for rows and columns
        
        elif isinstance(item, tuple):
            if isinstance(item[0], list) or isinstance(item[1], list):
                if isinstance(item[0], list):
                    rowz = [row for index, row in enumerate(self.data) if index in item[0]]
                else:
                    rowz = self.data[item[0]]

                if isinstance(item[1], list):
                    if all([isinstance(thing, int) for thing in item[1]]):
                        return [[column_value for index, column_value in enumerate([value for value in row.itervalues()]) if index in item[1]] for row in rowz]
                    elif all([isinstance(thing, str) for thing in item[1]]):
                        return [[row[column_name] for column_name in item[1]] for row in rowz]
                    else:
                        raise TypeError('What the hell is this?')

                else:
                    return [[value for value in row.itervalues()][item[1]] for row in rowz]
            else:
                if isinstance(item[1], (int, slice)):
                    return [[value for value in row.itervalues()][item[1]] for row in self.data[item[0]]]
                elif isinstance(item[1], str):
                    return [row[item[1]] for row in self.data[item[0]]]
                else:
                    raise TypeError('I don\'t know how to handle this...')

        elif isinstance(item, list):
            if all([isinstance(thing, bool) for thing in item]):
                list_index = [index for index, thing in enumerate(item) if thing == True]
                return [row for index, row in enumerate(self.data) if index in list_index] 
            elif all([isinstance(thing, int) for thing in item]):
                return [row for index, row in enumerate(self.data) if index in item]
            else:
                raise TypeError('I don\'t know how to handle this...')

# Task 1 

    def sort_by(self, column_name,boo):
        
        sorted_list = [row[column_name] for row in self.data]

        if boo == True: 
            data_lst_sorted = sorted(sorted_list,reverse = True)
        else: 
            data_lst_sorted = sorted(sorted_list,reverse = False)

        return data_lst_sorted


# Task #1 Extra Credit

    def new_sort_by(self,column_name,boo):
        if type(column_name) == str:
            sorted_list = [row[column_name] for row in self.data]
        elif type(column_name) == list:
            for index in range(0, len(column_name)):
                sorted_list = [row[column_name[index]] for row in self.data]
        else:
            raise TypeError('new_sort_by argument is not valid')

        if type(boo) == bool:
            if boo == True: 
                data_lst_sorted = sorted(sorted_list,reverse = True)
            else:
                data_lst_sorted = sorted(sorted_list,reverse = False)
        elif type(boo) == list:
            for idx in range(0, len(boo)):
                if boo[idx] == True:
                    data_lst_sorted = sorted(sorted_list,reverse = True)
                else:
                    data_lst_sorted = sorted(sorted_list,reverse = False)
        else:
            raise TypeError('new_sort_by argument is not valid')

        return data_lst_sorted
        
        

# Task 3

    def group_by(self, column_name1, column_name2, function_name):
        column1 = self[column_name1]
        column2 = self[column_name2]
        lst = list((zip(column1, column2)))
        res = defaultdict(list)
        for k, v in lst: res[k].append(v)
        group_by_list = [{'column_name1':k, 'column_name2':v} for k,v in res.items()]
        
        avg_lst = []
        col_list=[]
        row = []
        header = [column_name1, 'Average']
        row.append(header)
        for idx in range(0,len(group_by_list)):
            dic_list = group_by_list[idx]
            value_list = dic_list['column_name2']
            avg_value = function_name(value_list)
            avg_lst.append(avg_value)
            key_list = dic_list['column_name1']
            col_list.append(key_list)

            row_list = [col_list[idx], avg_lst[idx]]
            row.append(row_list)
        # print(row)
        return DataFrame(list_of_lists=row, header=True)
    

def avg(list_of_values):
    return sum(list_of_values)/float(len(list_of_values))


# Task 2

class Series(list):
    def __eq__(self, other):
        ret_list = []

        for item in self:
            ret_list.append(item == other)

        return ret_list

    def __gt__(self,other):
        ret_list = []

        for item in self:
            ret_list.append(item > other)

        return ret_list 

    def __lt__(self, other):
        ret_list = []

        for item in self:
            ret_list.append(item < other)

        return ret_list
    
    def __le__(self, other):
        ret_list = []

        for item in self:
            ret_list.append(item <= other)

        return ret_list 

    def __ge__(self, other):
        ret_list = []

        for item in self:
            ret_list.append(item >= other)

        return ret_list


print("********************* Path ***************************")

file = open('/Users/admin/Desktop/BIA660/Video/SalesJan2009.csv')
lines = file.readlines()
data = [l.split(',') for l in lines]
things = lines[559].split('"')
data[559] = things[0].split(',')[:-1] + [things[1]] + things[-1].split(',')[1:]
df = DataFrame(list_of_lists = data)
Ser = Series(df['Price'])
a = [index for index,value in enumerate(Ser) if type(value)!=float]



print("*********************Task 1***************************")

Task1  = df.sort_by('Price', boo =True)
print(Task1)

print("********************* Task1 #1 Extra credit ***************************")

Extra_Task1 = df.new_sort_by(['Price', 'Latitude'] , boo = [True, False])
print(Extra_Task1)

print("*********************Task 2***************************")

bool_list = Ser>1400
# print(bool_list)
Task2 = df[bool_list]
print(Task2)


print("*********************Task 3***************************")

Task3 = df.group_by('Payment_Type', 'Price', avg)
print(Task3)
print(Task3.data)







