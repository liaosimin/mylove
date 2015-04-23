# __author__ = 'lsm'
# import xlrd
# import json
# data = xlrd.open_workbook('/home/lsm/Documents/university.xls')
# table = data.sheets()[0]
# nrows = table.nrows
# schools = []
# city = '省'
# for i in range(nrows):
#     row = table.row_values(i)
#     if not row[4]:
#         city = row[0].split('（')[0]
#     else:
#         schools.append([row[1], row[3], city])
# f = open('university.py', 'w')
# f.write(json.dumps({'s': schools}))
# f.close()