import ipaddress
import json
import time
import csv
import whatportis
import os
from art import  *


def setSubnetDictionary():
    with open('subnets.csv', 'r') as subnet:
        reader = csv.reader(subnet, delimiter=',')
        for row in reader:
            combine = row[1] + "/" + row[2]
            mydict[row[0]] = combine
    for x in mydict:
        subnetIP = mydict[x]
        source_address = ipaddress.ip_address(u"10.3.17.55")
        subnet_address = ipaddress.ip_network(str(subnetIP))

        if source_address in subnet_address:
            break

def getSubnet(ip_address):
    ip_address = str(ip_address)
    for key in mydict:
        subnetIP = mydict[key]
        ip_address = ipaddress.ip_address(str(ip_address))
        subnet_address = ipaddress.ip_network(str(subnetIP))
        if ip_address in subnet_address:
            return subnet_address

def getSubnetName(ip_address):
    ip_address = str(ip_address)
    for key in mydict:
        subnetIP = mydict[key]
        ip_address = ipaddress.ip_address(str(ip_address))
        subnet_address = ipaddress.ip_network(str(subnetIP))
        if ip_address in subnet_address:
            return str(key)

def locateCommunications(subset):

    with open('sample-netflow.csv', 'r') as sample:
        reader = csv.reader(sample, delimiter=',')
        source_subnetIP = subset
        associated_ips = ""
        time = 0
        for row in reader:
            check =  row[0]
            check_for_dups = associated_ips

            if "#" in check:
                ##checks to see if there was a comment or not
                pass
            else:
                source_address = ipaddress.ip_address(str(row[0]))
                destination_address = ipaddress.ip_address(str(row[1]))
                subnet_address = ipaddress.ip_network(str(source_subnetIP))
                if source_address in subnet_address:
                    if str(destination_address) in check_for_dups:
                        ## We want to ignore duplicates
                        pass
                    else:
                        associated_ips = associated_ips + str(destination_address) + ","
                        prettyText(row, time)
                        time = time + 1

        return associated_ips

def determineSubnet(list_of_ips):
    list_of_destination_subnets = ""
    reader = csv.reader([list_of_ips], delimiter=',')
    list = list_of_ips.split(',')
    print(list)
    for ip in list:
        for key in mydict:
            if ip == "":
                pass
            else:
                source_subnetIP = mydict[key]
                source_address = ipaddress.ip_address(str(ip))
                subnet_address = ipaddress.ip_network(str(source_subnetIP))
                if source_address in subnet_address:
                    if str(subnet_address) in list_of_destination_subnets:
                        bytes = bytes_traveled[str(ip)]
                        temp = list_of_destination_subnets
                        tag = "Bytes for " + str(subnet_address) + ":"
                        temp1 = temp.split(tag)
                        temp1 =  ''.join(temp1)
                        temp1 = temp1.split(",")
                        old_byte = temp1[1]
                        old_byte = old_byte.replace(",","")
                        new_byte = int(old_byte) + int(bytes)
                        old_text = key + ":" + str(subnet_address) + "," + "Bytes for " + str(subnet_address) + ":" + str(old_byte) + ", "
                        new_text = key + ":" + str(subnet_address) + "," + "Bytes for " + str(subnet_address) + ":" + str(new_byte) + ", "
                        list_of_destination_subnets = list_of_destination_subnets.replace(str(old_text),str(new_text))
                    else:
                        bytes = bytes_traveled[str(ip)]
                        list_of_destination_subnets = key + ":" +  str(subnet_address) + "," + "Bytes for " + str(subnet_address) + ":" + str(bytes) + ", " + list_of_destination_subnets
    return list_of_destination_subnets

def prettyText(row, time):

    title = input + " Instance " + str(time)
    source_ip = str(row[0])
    destination_ip = str(row[1])
    source_ports = str(row[2])
    destination_ports = str(row[3])
    protocol = str(row[4])
    bytes = str(row[6])
    sensor = str(row[11])
    header = str(input)
    print("Source IP: " + str(source_ip))
    print("Destination IP: " + str(destination_ip))
    print("Destination Subnet: " + str(getSubnet(destination_ip)))
    print("Destination Subnet corresponding Building: " + str(getSubnetName(destination_ip)))
    print("Source Port: " + str(source_ports))
    print("Verifying what the port is being used for........")
    ##print(str(os.system("whatportis " + source_ports)))
    print("Destination Port: " + str(destination_ports))
    print("Verifying what the port is being used for.........")
    ##print(str(os.system("whatportis " + destination_ports)))
    print("Protocol used: " + str(protocol))
    print("Bytes sent: " + str(bytes))
    print("Sensor Triggered: "+ str(sensor))
    print("================================================================================================")
    ##nothing yet

    json_dict[title] = [source_ip]
    json_dict[title].append({
        'SourceIP': str(source_ip),
        "Destination IP": str(destination_ip),
        "Destination Subnet": str(getSubnet(destination_ip)),
        "Destination Subnet corresponding Building": str(getSubnetName(destination_ip)),
        "Source Port": str(source_ports),
        "Destination Port": str(destination_ports),
        "Protocol used": str(protocol),
        "Bytes sent": str(bytes),
        "Sensor Triggered": str(sensor)
    })



def writeToFile():
    with open("Subnet.json", 'a') as outfile:
        json.dump(json_dict,outfile, indent=2)
    outfile.close()


mydict = {}
json_dict = {}

start = time.time()
tprint("WireShark")

print("")
print("")
print("")


setSubnetDictionary()

print("Let's examine what subnets are talking to each other.")

print("We are going to check what Subnets IP has spoken to in the last 2 hours, enter an IP Subnet")
input = input()
file_name = "Subnet.json"

open(file_name,'x').close()
locateCommunications(str(input))
writeToFile()



end = time.time()

##print(f"Runtime of the program is {end - start}")