######################################################################################
                                  Copyright 2020                                            
                      Author: Vedant Sethia <vsethia@infoblox.com>                         
  For any issues/suggestions please write to vsethia@infoblox.com , kvasudevan@infoblox.com           
######################################################################################

# Bridging the DTC Gap

## Introduction

Infoblox DNS Traffic Control(DTC) integrates GSLB functionality with core DDI network services.
Highly automated, it provides the performance, scalability, and availability that organizations require.
DTC load balances DNS traffic based on various parameters such as client location, server location and server availability.

## About the project

This project aims at dynamically changing the DTC pool ratios based on parameters which can be polled using 
SNMP such as CPU Utilization, NIC Usage, Memory, RAM etc. 
Please note that the current version of the project focusses on CPU Utilization.
The solution takes a CPU Utilization threshold as an input. The DTC servers are polled for their current CPU Utilization and consolidated at the DTC pool level. Once the CPU threshold is reached, the algorithm calculates the optimum configuration according to the current utilization metrics and modifies the ratios accordingly.

## Pre-requisites

 - System, on which you plan to run the solution, should have python version 3+ with a working pip command.
 - All the DTC servers need to have snmpd configured and running.
A sample snmpd.conf file has been uploaded with the project for reference.

## Installation

Step 1: Navigate to the Project

	cd firstsite

Step 2: Install all the dependencies

	python setup.py build
	python setup.py install

## Running the Application

Step 1: Run the Django server

	cd firstsite
	python manage.py runserver

Step 2: Open Browser: http://127.0.0.1:8000/

## Instructions

 - Login page:
   Enter the grid master IP address, username and password

 - LBDN Page:
   The table on this page contains all the LBDNs. However, the dropdown only contains those LBDNs whose Load Balancing method is set to 'RATIO'. Select the LBDN that needs to be monitored from the dropdown.

 - Pool Page:
   This page displays all the pools with their CPU Utilization and initial ratios. 
Specify the CPU Utilization threshold beyond which the ratios need to be modified. This should be an integer value in range(0-100). 
Also select the checkbox to allow for restarting the grid once the modifications have been made. If it is unchecked, everytime the ratio is modified, you would need to manually restart the services on the grid for the new configuration to take effect.

 - Polling Page:
   This page displays the current CPU utilization and configurations. This page is refreshed every 3 seconds and the values are re calculated. As per the values, the ratios are either maintained or modified to suit the optimum configuration.
