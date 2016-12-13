from socket import *
import sqlite3
import sys
import datetime

# convert seconds to a string representing date and time
def _string_time(s):
	return  datetime.datetime.fromtimestamp(float(s)).strftime('%b %d %H:%M:%S')
def _string_time_2(s):
	return  datetime.datetime.fromtimestamp(float(s)).strftime('%A %b %d %H:%M:%S')
	
# check if args are all integers	
def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def check_int_args(args):
	for i in range(0, len(cmds) -1):
				if not isInt(cmds[i]): 
					print 'Invalid arguments \n'
					return False
	return True

# Important: data is stored as a stack.
# read messages from socket with delimiter and store result in an array.
def _readData(sock, buff_size, delim):
	result = []
	data = sock.recv(buff_size).decode()
	while data.find(delim) != -1:
		line, data = data.split(delim, 1)
		result.append(line)
	return result
	
# PRINT FUNCTION
def _print(next, n, mode, data, new = []):
	if next == True:
		if len(data) > n:
			for i in range(0, n):
				data.pop()
		else:
			if len(new) > 0:
				while len(data) != 0:
					data.pop()
				while len(new) != 0:
					data.append(new.pop())
			else:
				print 'No more to display'
				return		
	
	temp = []
	if mode == 'ag':
		for i in range (0, min(n, len(data))):
			e = data.pop()
			temp.append(e)
			print str(i+1) + '. (' + e[2] + ') ' + e[1]
		
	if mode == 'sg':
		for i in range (0, min(n, len(data))):
			e = data.pop()
			temp.append(e)
			if e[2] == 0:
				num_posts = ' '
			else:
				num_posts = str(e[2])
			print str(i+1) + '. ' + num_posts + '  ' + e[1]
			
	if mode == 'rg':
		for i in range (0, min(n, len(data))):
			e = data.pop()
			temp.append(e)
			print str(i+1) + '. ' + e[3] + '  ' + _string_time(e[2]) + '    ' + e[1]
			
	if mode == 'rgv':
		for i in range (0, min(n, len(data))):
			e = data.pop()
			temp.append(e)
			print e
	
	while len(temp) != 0:
		data.append(temp.pop())
	
# ag sub-commands handlers
# data is an array of (groupId, groupName, subOrNot)
def _ag(data, n, conn):
	while 1:
		cmd = raw_input()
		if cmd == 'q':
			#quit from ag command mode
			print 'Quitting from ag mode\n'
			break
			
		elif cmd == 'n':
			# Print the next n line
			_print(True, n, 'ag', data)
		
		else:
			cmds = cmd.split()
			if len(cmds) >= 2 and cmds[0] == 's':
				# If all argument are integers, insert indicated groups into user history
				if check_int_args:
					cur = conn.cursor()
					for i in range(1, len(cmds)):
						k = len(data) - int(cmds[i])
						if k < len(data) and k >= 0:
							cur.execute('insert or replace into group_subs values (?, ?, ?)'
								, (data[k][0], data[k][1], '',))
					# Saving the changes
					conn.commit()
				
			elif len(cmds) >= 2 and cmds[0] == 'u':
				# If all argument are integers, delete indicated groups from user history
				if check_int_args:
					cur = conn.cursor()
					for i in range(1, len(cmds)):
						k = len(data) - int(cmds[i])
						if k < len(data) and k >= 0:
							cur.execute('delete from group_subs where id = ?', (data[k][0],))
					conn.commit()

# sg sub-commands handlers		
# data is an array of (groupId, groupName, new_num_posts)		
def _sg(data, n, conn):
	while 1:
		cmd = raw_input()
		if cmd == 'q':
			#quit from ag command mode
			print 'Quitting from sg mode\n'
			break		
		elif cmd == 'n':
			# Print the next n line
			_print(True, n, 'sg', data)
		else:
			cmds = cmd.split()
			if len(cmds) >= 2 and cmds[0] == 'u':
				# If all argument are integers, delete indicated groups from user history
				if check_int_args:
					cur = conn.cursor()
					for i in range(0, len(cmds) -1):
						k = len(data) - int(cmds[i-1])
						if k < len(data) and k >= 0:
							cur.execute('delete from group_subs where id = ?', (data[k][0]))
					conn.commit()	
		
# Handling n subcommand of rg mode
def _rgn(gname, data, n, sock):
	message = 'RGN ' + gname + '\r\n'
	sock.send(message.encode())
	dataNew = _readData(sock, 4096, '\n')
	new = []
	if len(dataNew) > 0 and dataNew[0] == '200 OK':
		dataNew.pop(0)
		for i in range(0, len(dataNew), 3):
			new.append((dataNew[i], dataNew[i + 1], int(dataNew[i + 2]), 'N'))
	# Print the next n line
	_print(True, n, 'rg', data, new)
		
# data is an array of (postId, postName, timeStamp, readOrNot)
def _rg(gname, data, n, conn, sock, userid):
	while 1:
		cmd = raw_input()
		#quit from ag command mode
		if cmd == 'q':		
			print 'Quitting from rg mode\n'
			break
		
		# n sub-command
		elif cmd == 'n':
			_rgn(gname, data, n, sock)
		
		# p sub-command
		elif cmd == 'p':
			print 'Enter the post subject:'
			subject = raw_input()
			author = userid
			content = ''
			print '\nEnter the content of the post: \n'
			while 1:
				line = raw_input()
				if line == '.':
					break
				content += line + '\n'
			message = 'RGP\r\n' + gname + '\r\n' + subject + '\r\n' + author + '\r\n' + content + '\r\n'
			sock.send(message.encode())
			mess = _readData(sock, 4096, '\n')
			if mess[0] == '200 OK':
				print('Your post is received.')
			_rgn(gname, data, n, sock)
		
		# id sub-command:
		elif isInt(cmd) and int(cmd) >=1 and int(cmd) <= n:
			print 'Reading mode'
			i = len(data) - int(cmd)
			message = 'RGV ' + data[i][0] + '\r\n'
			sock.send(message.encode())
			post = _readData(sock, 4096, '\r\n')
			print('\nGroup: ' + post[1])
			print('Subject: ' + post[2])
			print('Author: ' + post[3])
			print('Date: ' + _string_time(int(post[4])))
			# Printing first n lines of content
			content = post[5].split('\n')
			_print(False, n, 'rgv', content)
			while 1:
				cmd = raw_input()
				if (cmd == 'n'):
					# Printing next n lines of content 
					_print(True, n, 'rgv', content)
				if (cmd == 'q'):
					print('Quitting from reading post mode\n')
					break
		
		# r sub-command
		else:
			cmds = cmd.split()
			if len(cmds) >= 2 and cmds[0] == 'r':
				# If all argument are integers, insert indicated groups into user history
				if check_int_args:
					cur = conn.cursor()
					cur.execute('select post_read from group_subs where name = ?', (gname,))
					post_read = cur.fetchone()[0]
					for i in range(1, len(cmds)):
						k = len(data) - int(cmds[i])
						if k < len(data) and k >= 0:
							if post_read != '':
								post_read += ' ' + data[k][0].split('g')[0]
							else:
								post_read += data[k][0].split('g')[0]
							cur.execute('update group_subs set post_read = ? where name = ?',
								(post_read, gname,))
					# Saving the changes
					conn.commit()
										
### MAIN FUNCTION FOR HANDLING LOGIN ###

def _login(userid):
	#Connect to the server 
	global clientSocket
	serverName = 'allv25.all.cs.sunysb.edu'
	serverPort = 6292
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((serverName,serverPort))
	try:
		# Initialize user history database
		conn = sqlite3.connect(userid + '_history.db')
		cur = conn.cursor()
		# create cur, which is the table of groups subscribed in the user history information
		cur.execute('create table if not exists '
			+ 'group_subs(id text, name text, post_read text, primary key(id))')
	except sqlite3.Error:
		print 'Problem with database in client computer'
		sys.exit(1)
	print 'Logged in. Please enter the subcommands \n'
	#Get command from command-line
	while 1:
		cmd = raw_input()
		if cmd == 'logout':
			print ('Logging out...')
			clientSocket.close()
			conn.close()
			sys.exit()
			
		cmd = cmd.split()
		
		### HANDLING AG MODE ###
		
		if len(cmd) <= 2 and cmd[0] == 'ag':
			N = 5
			if len(cmd) == 2 and isInt(cmd[1]): 
				N = int(cmd[1])
			# Request the server for a list of all available groups
			message = 'AG\r\n\r\n'
			clientSocket.send(message.encode())
			
			# Get list of available groups (with id and name) from the server
			data, srv_errAG = [], False
			# reading the first line
			dataAG = _readData(clientSocket, 4096, '\n')
			if dataAG[0] != '200 OK':
				print 'Problem from the server'
			else:
				dataAG.pop(0)
				for line in dataAG:			
					parts = line.split()
					cur.execute('select * from group_subs where id = ?', (parts[0],))
					if cur.fetchone() != None:
						subs = 's'
					else:
						subs = ' '
					data.append((parts[0], parts[1], subs))
				data.sort(key = lambda e: e[1], reverse = True)
			# Print the first N groups	
			_print(False, N, 'ag', data)	
			# Handle subcommands in ag mode
			_ag(data, N, conn)
		
		
		### HANDLING SG MODE ###
		
		if len(cmd) <= 2 and cmd[0] == 'sg':
			N = 5 							# DEFAULT N argument
			if len(cmd) == 2 and isInt(cmd[1]): 
				N = int(cmd[1])
			# Request the server for a list of all available groups
			message = 'SG\r\n'
			result_set = cur.execute('select id from group_subs')
			for rec in result_set:
				message += rec[0] + '\r\n'
			clientSocket.send(message.encode())
			
			# Get list of subscribed groups with id, name and number of posts from the server
			data, srv_errSG = [], False
			dataSG = _readData(clientSocket, 4096, '\n')
			if dataSG[0] != '200 OK':	
				print 'Problem from the server'
			else:
				dataSG.pop(0)
				for line in dataSG:
					parts = line.split()
					# new post = total posts from server - total posts(read) from user history
					cur.execute('select post_read from group_subs where id = ?', (parts[0],))	
					numPost = int(parts[2]) - (len(cur.fetchone()[0]) + 1)/2
					data.append((parts[0], parts[1], numPost))
				data.sort(key = lambda e: e[1], reverse = True)
			# Print the first n groups			
			_print(False, N, 'sg', data)	
			
			# Handle subcommands in sg mode
			_sg(data, N, conn)
				
		## HANDLING RG MODE
		if len(cmd) >= 2 and len(cmd) <= 3 and cmd[0] == 'rg':
			N = 5
			gname = cmd[1]
			# Check if gname is a subscribed group
			cur.execute('select * from group_subs where name = ?', (gname,))
			if cur.fetchone() == None:
				print 'You haven\'t subscribed group' + gname + '. Quitting from rg mode'
				continue
			
			if len(cmd) == 3 and isInt(cmd[2]):	
				N = int(cmd[2])
			message = 'RG ' + gname + '\r\n'
			clientSocket.send(message.encode())
			dataRG = _readData(clientSocket, 4096, '\r\n')
			if dataRG[0] != '200 OK':	
				print 'Problem from the server'
			else:
				data = []
				dataRG.pop(0)						
				for line in dataRG:				
					parts = line.split('\n')
					ordinal = parts[0].split('g')[0]
					groupId = parts[0].split('g')[1]
					cur.execute('select post_read from group_subs where id = ?', groupId)
					post_read = cur.fetchone()[0]
					if post_read.startswith(' ' + ordinal) or post_read.endswith(' ' + ordinal) or ((' ' + ordinal + ' ') in post_read):
						read = ' '
					else:
						read = 'N'
					data.append((parts[0], parts[1], int(parts[2]), read))
				data.sort(key = lambda e: (e[3], e[2]))
			# Print the first n groups			
			_print(False, N, 'rg', data)	
			_rg(gname, data, N, conn, clientSocket, userid)

# To be updated: just instruct users how to use the commands			
def _help():
	print 'help'

# Main
clientSocket = 0
while 1:
	cmdLogin = raw_input()
	if cmdLogin == 'help':
		_help();
	cmdLogin = cmdLogin.split()
	if len(cmdLogin) == 2 and cmdLogin[0] == 'login':
		_login(cmdLogin[1]);
	
