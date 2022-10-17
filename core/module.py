import os,hexdump
import binwalk

class IDENTIFIER(object):
	def __init__(self,**kwargs):
		'''
		'''
		#读配置
		for (k, v) in kwargs.items():
			if v is not None:
				setattr(self, k, v)
	
	def make_tmp_file(self,bytes_str):
		#self.DISPLAY.Show_Debug(bytes_str)
		self.tempfile_name=self.BINDIR+'binfile'
		open(self.tempfile_name,'wb').write(bytes_str)
		self.bytes_str=bytes_str
		self.result={}
		if self.VERBOSE or self.FORCE:
			self.result['hexdump']=hexdump.hexdump(bytes_str,result='return').split('\n')
		if self.FORCE:
			self.result['force extract']=[(0,'show first 100 bytes')]

	def check_strings(self):
		result_text=os.popen(f'strings -td -{self.STRINGLENGTH} {self.tempfile_name}').read()
		if len(result_text):
			templist=[]
			for x in result_text.rstrip('\n').split('\n'):
				templist.append((int(x[:8]),x[8:]))

			self.result['strings']=templist
			

	def check_file(self):
		IGNORES = [
		'data',
		'empty',
		'Sendmail frozen configuration',
		'DBase 3 data file',
		'DOS executable',
		'Dyalog APL',
		'8086 relocatable',
		'SysEx File',
		'COM executable',
		'Non-ISO extended-ASCII text',
		'ISO-8859 text',
		'very short file',
		'International EBCDIC text',
		'lif file',
		'AmigaOS bitmap font',
		'a python script text executable', # common false positive
		    #modified
		'ddis/dtif table data',
		'COM executable for DOS',
		'PGP\\011Secret Sub-key -',
		'AIX core file fulldump 32-bit',
		'PGP\\011Secret Key -',
		'VAX-order2 68k Blit mpx/mux executable',
		'Applesoft BASIC program data, first line number 1',
		'PGP symmetric key encrypted data -',
		'SysEx File - AKG',
		'SysEx File - Passport'
		
    ]
		result_text=os.popen(f'file -b {self.tempfile_name}').read()
		for x in IGNORES:
			if x in result_text.rstrip('\n').split(','):
				return
		if len(result_text):
			self.result['file']=[(0,result_text.rstrip('\n'))]
			self.DISPLAY.Show_Debug(self.result)

	def check_binwalk(self):
		try:
			binwalk_restlts=binwalk.scan(self.tempfile_name, signature=True,quiet=True)
			if binwalk_restlts:
				templist=[]
				for module in binwalk_restlts:
					for result in module.results:
						templist.append((result.offset,result.description))
			
				if templist:
					self.result['binwalk']=templist
		except:
			self.DISPLAY.Show_Alert(f'binwalk API运行失败,请检查环境')

	def check_all(self):
		self.check_strings()
		if self.FORMARTDETECTER=='binwalk':
			self.check_binwalk()
		else:
			self.check_file()
		return(self.result)