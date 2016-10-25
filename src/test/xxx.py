#! /usr/bin/python2.6
#-*- encoding:UTF-8 -*-

count = 0
total_byte_read_now = 0          #目前为止共读取的字符数量，作为下一次ftell的参数
allrady_max_count = 0            #判断文件是否读取完毕
sql_mail_out = []
sql_statement = ""              #拼接所有的sql语句，因为长的sql语句是跨行的
unique_sql = []
IS_UNIQUE = True
any_new_proc = False             #本次循环是否新处理内容
#thefile = open("/home/mysql/data/slow-query.log", 'rb')
thefile = open(".\\test.txt", 'rb')

try:
    out_count_file = open(".\\out_count.txt", 'rb')    #会有异常出现
    total_byte_read_now = int(out_count_file.read(100))
    allrady_max_count = total_byte_read_now
    out_count_file.close()
    #print(str(total_byte_read_now))
except:
    total_byte_read_now = 0
    allrady_max_count = 0

select_loop = 1024
for loop_count in range(select_loop):
    
    if total_byte_read_now == 0:
        start_proc_pos = 0
    else:
        start_proc_pos = total_byte_read_now + 1
    
    thefile.seek(start_proc_pos, 0)      #跳转到上一次操作的字符后一位，seek函数是否需要处理异常
    buffer = thefile.read(1*1024*1024)     #继续从上一次的位置操作数据，每次操作1M大小
    total_byte_read_now = total_byte_read_now + len(buffer)
    
    if total_byte_read_now > allrady_max_count:    #如果没有新增的读取内容表示文件读取完毕
        allrady_max_count = total_byte_read_now
        any_new_proc = True
        read_line_list = buffer.splitlines()  #讲读取出来的内容按行分割到list中，后续按行处理基于此list
        #print(read_line_list)
        read_line_count = len(read_line_list)
        for i in range(read_line_count):    #对我们本次取到的数据块进行处理
            if read_line_list[i].find('# Query_time:') >= 0:     #判断是否是# Query_time:行
                #print(read_line_list[i])
                start_index = read_line_list[i].find(':')
                end_index = read_line_list[i].find('Lock_time:')
                spend_time = read_line_list[i][start_index+2:end_index-2]
                #print(spend_time)    #打印慢查询消耗的时间
                try:
                    float_query_time = float(spend_time)
                except:
                    #print(read_line_list[i])
                    float_query_time = 4.0
                if float_query_time > 4.0:
                    for j in range(i, read_line_count):
                        set_find = read_line_list[j].find('SET timestamp=')
                        if set_find >= 0:
                            set_pos = j
                            break

                    for p in range(j, read_line_count):
                        time_find = read_line_list[p].find('# Time: ')
                        if time_find >= 0:
                            time_pos = p
                            break

                    for k in range(j, read_line_count):
                            host_find = read_line_list[k].find('# User@Host:')
                            if host_find >= 0:
                                host_pos = k
                                break
                        
                    IP_start = read_line_list[k].rfind('[')
		    IP_end = read_line_list[k].rfind(']')
                    IP_name = read_line_list[k][IP_start+1:IP_end]
		    black_ip_list=['172.16.10.27'] #这里是IP黑名单，过略掉这些IP地址的sql语句	
		    if IP_name not in black_ip_list:        #所有在名单的IP地址都是需要过滤的
                        if p < k:         #判断是否有属性# Time: 出现，如果有的话，sql语句读取的位置是从SET timestamp到# Time: 之间的
                            for l in range(j+1, p):
                                sql_statement = sql_statement + read_line_list[l] + "\r\n"
                        else:
                            for l in range(j+1, k):
                                sql_statement = sql_statement + read_line_list[l]  + "\r\n"
                        
                        for q in range(len(unique_sql)):
                            if unique_sql[q] == sql_statement.strip():
                                IS_UNIQUE = False
                                break                 #找到该元素就退出循环
                            else:
                                IS_UNIQUE = True
							
                        if IS_UNIQUE == True:
                            #print(sql_statement)
                            unique_sql.append(sql_statement.strip())
                            IS_UNIQUE = False
                        
                        if p < k:    #判断是否有属性# Time: 出现，如果有的话，sql语句读取的位置是从SET timestamp到# Time: 之间的
                            #print('SQL语句所消耗的时间： ' + read_line_list[i] + '\r\n出问题的SQL语句： ' + sql_statement + 'SQL语句出现问题的时间： ' + read_line_list[p] + \
                            #      '\r\nSQL语言来源位置： ' + read_line_list[k])
                            sql_mail_out.append('SQL语句所消耗的时间： ' + read_line_list[i] + '\r\n出问题的SQL语句： ' + sql_statement + 'SQL语句出现问题的时间： ' + read_line_list[p] + \
                                                '\r\nSQL语言来源位置： ' + read_line_list[k])
                        else:    #没有出现Time
                            #print('SQL语句所消耗的时间： ' + read_line_list[i] + '\n出问题的SQL语句： ' + sql_statement + 'SQL语言来源位置： ' + read_line_list[k])
                            sql_mail_out.append('SQL语句所消耗的时间： ' + read_line_list[i] + '\r\n出问题的SQL语句： ' + sql_statement + 'SQL语言来源位置： ' + read_line_list[k])
                            
                        sql_statement = ""     #输出完毕清空
                    
                    #当前是直接将该SQL语句输出，后面可以考虑放在一个队列中进行后续处理
        
        #输出有问题的sql语句
        out_mail_file = open(".\\out_mail.txt", 'ab')
        for m in range(len(sql_mail_out)):
        	out_mail_file.write(sql_mail_out[m])
        	out_mail_file.write("\r\n")
        out_mail_file.close()
        
        unique_sql_file = open(".\\unique_sql.txt", 'ab')
        for r in range(len(unique_sql)):
            unique_sql_file.write(unique_sql[r])
            unique_sql_file.write("\r\n")
        unique_sql_file.close()
        
        sql_mail_out = []    #清空队列，下次继续
        unique_sql = []
        IS_UNIQUE = True      #重新接受新的元素
                        
        if (loop_count == (select_loop - 1)):
            print('loop end!')    #这里要做的事情是把信息发送出去，把变量初始化
            
            out_count_file = open(".\\out_count.txt", 'wb')
            if any_new_proc == False:
                total_byte_read_now = start_proc_pos - 1
            out_count_file.write(str(total_byte_read_now))
            out_count_file.close()

            #应该是加入sleep的语句
            
    else:
        print('file end!')    #这里要做的事情是把信息发送出去，把变量初始化
        
        #输出有问题的sql语句
        out_mail_file = open(".\\out_mail.txt", 'ab')
        for n in range(len(sql_mail_out)):
            out_mail_file.write(sql_mail_out[n])
            out_mail_file.write("\r\n")
        out_mail_file.close()

        unique_sql_file = open(".\\unique_sql.txt", 'ab')
        for r in range(len(unique_sql)):
            unique_sql_file.write(unique_sql[r])
            unique_sql_file.write("\r\n")
        unique_sql_file.close()
        
        sql_mail_out = []    #清空队列，下次继续
        unique_sql = []
        IS_UNIQUE = True      #重新接受新的元素
        
        out_count_file = open(".\\out_count.txt", 'wb')
        if any_new_proc == False:
            total_byte_read_now = start_proc_pos - 1
        out_count_file.write(str(total_byte_read_now))
        out_count_file.close()
        #应该是加入sleep的语句
        break
thefile.close( )
