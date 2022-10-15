COLORS={
	'strings':34,
	'file':33,
	'binwalk':33

}

class Display(object):
	def __init__(self,**kwargs):
		for (k, v) in kwargs.items():
			if v is not None:
				setattr(self, k, v)
		if not hasattr(self,'DEBUG'):
			self.DEBUG=False
		if not hasattr(self,'VERBOSE'):
			self.VERBOSE=False


	def Show_Info(self,message):
		if self.VERBOSE:
			print(f"\033[1;36m[i]INFO:{message}\033[0m",end='\n') 

	def Show_Alert(self,message):
		if self.VERBOSE:
			print(f"\033[1;33m[!]ALERT:{message}\033[0m",end='\n')

	def Show_Error(self,message):
		print(f"\033[1;31m[x]ERROR:{message}\033[0m",end='\n') 

	def Show_Debug(self,message):
		if self.DEBUG:
			print(f"\033[1;32m[d]DEBUG:{message}\033[0m",end='\n') 

	def Show_Method(self,method_tuple,success=False):
		try:
			if success:
				print(f"\033[1;35m{','.join(method_tuple[:5])}                  \033[0m",end='\n')
			else:
				print(f"\033[1;30m{','.join(method_tuple[:5])}                  \033[0m",end='\r')
		except:
			return

	def Show_Result(self,result):
		#self.Show_Debug(result)
		for (k,l) in result.items():
			if k != 'hexdump':
				color=COLORS[k] if k in COLORS.keys() else 38
				if self.VERBOSE:
					show_hexdump_list=[0,1,2,3,4,5]
					max_len=len(result['hexdump'])
				for v in l:
					print(f'\t\033[1;{color}m{k}\t:{v[1]}\033[0m',end='\n')
					if self.VERBOSE:
						for i in range(-1,3):
							if int(v[0]/16)+i>0 and int(v[0]/16)+i not in show_hexdump_list and int(v[0]/16)<max_len-1:
								show_hexdump_list.append(int(v[0]/16)+i)
				
				if self.VERBOSE:
					show_hexdump_list.append(max_len-1)
					for i in show_hexdump_list:
						print(f'\t{result["hexdump"][i]}')
						if i+1 not in show_hexdump_list and i!=max_len-1:
							print(f'\t*')