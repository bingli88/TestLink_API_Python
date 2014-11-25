#!/usr/bin/python

__author__ = 'bingli'

import csv
import os
import sys
import time

new_dir = 'converterLog'
tags1 = ['summary', 'preconditions']
tags2 = ['Regression', 'Smoke', 'Jira No.', 'Automated Test']
tags3 = ['step_number', 'actions', 'expectedresults']
space = '    '
special_char = {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;'}


def pre_check(e):
    for k, v in special_char.items():
        e = e.replace(k, v)
    return e


def read_from_csv():
    csv_data = csv.reader(open(csvFile, 'rU'))  # Open csv file
    ret_list = []
    invalid_list = []

    # Read from csv and append each valid line in to tem_list.
    for index, row in enumerate(csv_data):
        # If name > 100 char, then append the (line number, testcase, length) into invalid_list.
        if len(row[2]) > 100:
            invalid_list.append((index, row[2], len(row[2])))
            continue

        # If the row doesn't contain a test case name then this row is just a 'step' of the last test case.
        if row[2] == '':
            ret_list[-1].extend(row[-3:])

        # Otherwise, append the row into tem_list.
        else:
            ret_list.append(row)

    # If invalid_list not null, then write (line number, test case name, length) into a log file.
    if len(invalid_list) > 0:
        log_name = 'logFile_%s.txt' % time.time()
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        dest_dir = os.path.join(curr_dir, new_dir)

        try:
            os.makedirs(dest_dir)
        except OSError:
            pass
        log_file = os.path.join(dest_dir, log_name)

        with open(log_file, 'w') as f:
            for item in invalid_list:
                f.write(','.join(str(i) for i in item) + '\n')
    return ret_list


def write_to_xml():
    xmlData = open(xmlFile, 'w')
    xmlData.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n')
    xmlData.write('<testcases>' + '\n')

    data = read_from_csv()

    # Read from the second row.
    for row in data[1:]:
        xmlData.write('<testcase name=' + '"' + pre_check(row.pop(2)) + '"' + '>' + '\n')  # <testcase> ... </testcase>
        for i in tags1:  # ['summary', 'preconditions']
            elem = pre_check(row.pop(2))
            elem_list = elem.split('\n')
            xmlData.write(space + '<' + i + '>' + '<![CDATA[' + '\n')
            for k in elem_list:  # read multiple lines of in a cell
                xmlData.write(space + '<p>' + k + '</p>' + '\n')
            xmlData.write(space + ']]>' + '</' + i + '>' + '\n')

        num = 2
        xmlData.write(space + '<custom_fields>' + '\n')
        for i in tags2:  # ['Regression', 'Smoke', 'Jira No.', 'Automated Test']
            xmlData.write(space*num + '<custom_field>' + '\n')
            xmlData.write(space*num + '<name>' + '<![CDATA[' + i + ']]>' + '</name>' + '\n')
            xmlData.write(space*num + '<value>' + '<![CDATA[' + pre_check(row.pop(2)) + ']]>' + '</value>' + '\n')
            xmlData.write(space*num + '</custom_field>' + '\n')
        xmlData.write(space + '</custom_fields>' + '\n')

        xmlData.write(space + '<steps>' + '\n')
        for k in xrange(len(row)/3):
            xmlData.write(space*num + '<step>' + '\n')
            for i in tags3:  # ['step_number', 'actions', 'expectedresults']
                xmlData.write(space*num + '<' + i + '>' + '<![CDATA[' + pre_check(row.pop(2)) + ']]>' + '</' + i + '>' + '\n')
            xmlData.write(space*num + '</step>' + '\n')
        xmlData.write(space + '</steps>' + '\n')
        xmlData.write('</testcase>' + '\n')

    xmlData.write('</testcases>' + '\n')
    xmlData.close()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        csvFile = sys.argv[1]  # 'OTC-8.csv', read from csv file
        xmlFile = sys.argv[2]  # 'OTC-8.xml', output xml file
    else:
        csvFile = sys.argv[1]  # take second argument
        xmlFile = csvFile.replace('csv', 'xml')  # replace extension
    write_to_xml()