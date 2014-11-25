#!/usr/bin/python

__author__ = 'bingli'

import csv
import os
import sys
import time

from testlink import TestlinkAPIClient, TestLinkHelper
from testlink.testlinkerrors import TestLinkError

csvFile = sys.argv[1]  # 'OTC-329.csv'

new_dir = 'executionLog'
test_project = 'Kenandy'
test_plan = 'Indian Summer 14 Release'
test_build = 'BPH11'

# Use this function to get test case name.
def get_testcase():
    csv_data = csv.reader(open(csvFile, 'rU'))
    testcase = []
    for index, row in enumerate(csv_data):
        if not row[2] == '':
            testcase.append((row[0], row[1], row[2], index))  # return a list of tuples (execution,notes,testcase,index)
    return testcase[1:]


def run_report():
    failed_list = []
    tls = TestLinkHelper().connect(TestlinkAPIClient)  # connect to Testlink
    testplan_id_result = tls.getTestPlanByName(test_project, test_plan)  # get test plan id
    testplan_id = testplan_id_result[0]['id']
    testcases = get_testcase()

    for i in testcases:
        test_result = i[0]
        test_notes = i[1]
        testcase_name = i[2]
        index = i[3]
        #
        # testcase_id_result = tls.getTestCaseIDByName(testcase_name)  # get test case id
        # testcase_id = testcase_id_result[0]['id']
        # tls.reportTCResult(testcase_id, testplan_id, test_build, test_result, test_notes)

        try:
            testcase_id_result = tls.getTestCaseIDByName(testcase_name)  # get test case id
            testcase_id = testcase_id_result[0]['id']
            tls.reportTCResult(testcase_id, testplan_id, test_build, test_result, test_notes)
        except TestLinkError:
            failed_list.append((index, testcase_name))

    if len(failed_list) > 0:
        log_name = 'logFile_%s.txt' % time.time()
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        dest_dir = os.path.join(curr_dir, new_dir)
        try:
            os.makedirs(dest_dir)
        except OSError:
            pass
        log_file = os.path.join(dest_dir, log_name)
        with open(log_file, 'w') as f:
            for item in failed_list:
                f.write(','.join(str(i) for i in item) + '\n')

if __name__ == '__main__':
    run_report()

