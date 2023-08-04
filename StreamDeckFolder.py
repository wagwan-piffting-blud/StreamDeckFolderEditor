import os
import sys
import getpass
import json
import re
from fnmatch import fnmatch
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
import argparse

parser = argparse.ArgumentParser(description="Moves a Stream Deck folder's back button to where you want it.\n\nThis script works by looking for a Hotkey with a Title field of \"editmepls\" and edits the containing folder's back button's location. This script is VERY basic, and could possibly cause PERMANENT data loss if used improperly. Every effort has been made to ensure this will not happen, but it is up to YOU to make YOUR own backup of your profile before running this script.\n\nNOTE: This program should ONLY be used to edit one folder at a time. It will exit after the first folder is edited.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-v', '--version', action='version', version='1.0.0')
args = parser.parse_args()
config = vars(args)

def print_layout(rows, cols):
	print("\n---------- STREAM DECK LAYOUT ----------")
	for rownum in range(rows):
		for colnum in range(cols):
			print("   " + str(colnum) + "," + str(rownum) + "  ", end = "")
		print("", end = "\n")
	print("----------------------------------------\n")

print("Stream Deck Folder Editor By Wags\n\nMAKE SURE YOU HAVE MADE A BACKUP OF ALL RELEVANT PROFILES FIRST!!! THIS SCRIPT OR ITS AUTHOR ARE NOT RESPONSIBLE IF ANY DATA LOSS OCCURS!!!\n\nPlease review the list below and choose the profile you wish to edit.\n\n(ctrl+c to exit, pass --help in the command line if you need a basic explanation)\n")

i = 0;

path = "C:\\Users\\" + getpass.getuser() + "\\AppData\\Roaming\\Elgato\\StreamDeck\\ProfilesV2\\"

os.chdir(path)

list_subfolders_with_paths = [f.path for f in os.scandir(path) if f.is_dir()]

for profile in list_subfolders_with_paths:
	i += 1
	os.chdir(profile)
	f = open('manifest.json')
	data = json.load(f)
	name = data["Name"]
	f.close()
	print(str(i) + ": " + name + "\n")
	os.chdir(path)

selected = int(input("Enter profile number to edit: "))

if(str(selected).isnumeric() and selected <= i and selected > 0):
	os.chdir(list_subfolders_with_paths[selected - 1])
	
	f = open('manifest.json')
	data = json.load(f)
	
	model = data["Device"]["Model"]
	match model:
		case "20GAA9901":
			type = "classic"
			rows = 3
			cols = 5
		case "20GAT9901":
			type = "xl"
			rows = 4
			cols = 8
		case "20GAI9901":
			type = "mini"
			rows = 2
			cols = 3
		case _:
			type = "app"
			rows = 0
			cols = 0
	
	f.close()
	
	print_layout(rows, cols)
	
	if(type != "app"):		
		coords = input("Enter new coords for back button in the format above (col,row): ")
		
		colnum = coords[0:1]
		rownum = coords[2:3]
		
		if(re.search("^\d,\d$", coords) and 0 <= int(rownum) < rows and 0 <= int(colnum) < cols):
			pattern = "*.json"
			
			i2 = 0
			
			file_count = sum(len(list(f for f in fs if f.lower().endswith('.json'))) for _, _, fs in os.walk(os.getcwd()))
			
			#print(file_count)
			
			for path, subdirs, files in os.walk(os.getcwd()):
				for name in files:
					if fnmatch(name, pattern):
						i2 += 1
						
						f4 = open(path + '\manifest.json')
						
						contents = f4.read()
						
						if(re.search("editmepls", str(contents))):
							f4.close()
							
							f5 = open(path + '\manifest.json', "r+")
							data = json.load(f5)
							
							jsonpath_expr = parse('$..[Actions].[*][?(@.UUID == "com.elgato.streamdeck.profile.backtoparent")]')
							semifinal = [match.value for match in jsonpath_expr.find(data)]
							
							#print(str(semifinal))
							
							replacements = re.sub(r'\-', '\-', str(semifinal))
							replacements = re.sub(r'^\[', '', replacements)
							replacements = re.sub(r']$', '', replacements)
							replacements = re.sub(r'\{', '\{', replacements)
							replacements = re.sub(r'\[', '\[', replacements)
							replacements = re.sub(r'\}', '\}', replacements)
							replacements = re.sub(r'\]', '\]', replacements)
							replacements = re.sub(r'\.', '\.', replacements)
							
							#print(str(replacements))
							
							replacements2 = re.search(str(replacements), str(data))
							#print(str(replacements2))
							substr = replacements2.start() - 6
							plain = f5.read()
							editme = plain[substr:replacements2.start()]
							afteredit = plain[replacements2.start():]
							afteredit = re.sub(r'\'', '"', afteredit)
							
							f5.seek(substr - 2)
							f5.write(coords + '":' + afteredit)
							f5.close()
							
							print("\nOperation successful. Please open the Stream Deck program and check to make sure no data loss occurred and the folder back button was moved to where you want it, and make sure to also delete the extraneous hotkey.")
							sys.exit()
					elif(i2 >= file_count):
						print("\nCould not find marker in any folder! Did you add a hotkey called \"editmepls\" to the folder you wish to edit?")
						sys.exit()
		else:			
			print("\nCoordinates invalid!")
			sys.exit()
	
	else:
		print("\nYour Stream Deck is unsupported/too new! Please open a new GitHub issue if you believe this is a mistake.")
		sys.exit()

else:
	print("\nPlease enter a number between 1 and " + str(i) + ".")
	sys.exit()
