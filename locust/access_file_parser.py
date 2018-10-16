import re

l_regex = re.compile(r'''.*:\d+ (\d+\.\d+\.\d+\.\d+) .* .* \[(.*)\] "(.*)" \d+ \d+ ".*" ".*"''')

p_regex = re.compile(r'''GET /puzzle/(\d+)/(.*)''')

AJAX = []

ip_dict = {}
urls = {}
with open("access.log") as infile:
    for line in infile:
        l = l_regex.match(line)
        if(l):
            # if("f18meta" not in l.group(3)):
            #     try:
            #         query = l.group(3).split("?")
            #         is_query = len(query) > 1
            #         s = query[0].split(" ")
            #         s = s[0] + s[1]
            #     except:
            #         continue
            #     if s[-1] == "/":
            #         s = s[0:-1]
            #     if is_query:
            #         s = s + " AJAX"

            #     if(s not in urls):
            #         urls[s] = 0
            #     urls[s] += 1

            # p = p_regex.match(l.group(3))
            # if(p):
            #     if(l.group(1) not in ip_dict):
            #         ip_dict[l.group(1)] = {}
            #     if(p.group(1) not in ip_dict[l.group(1)]):
            #         ip_dict[l.group(1)][p.group(1)] = [0]
            #     if("last_date" in p.group(2)):
            #         if(ip_dict[l.group(1)][p.group(1)][-1] == "BASE"):
            #             ip_dict[l.group(1)][p.group(1)].append(1)
            #         else:
            #             ip_dict[l.group(1)][p.group(1)][-1] = ip_dict[l.group(1)][p.group(1)][-1] + 1
            #     else:
            #         if(ip_dict[l.group(1)][p.group(1)][-1] != 0):
            #             if(ip_dict[l.group(1)][p.group(1)][-1] == "BASE"):
            #                 AJAX.append(0)
            #             else:
            #                 AJAX.append(ip_dict[l.group(1)][p.group(1)][-1])
            #         ip_dict[l.group(1)][p.group(1)].append("BASE")