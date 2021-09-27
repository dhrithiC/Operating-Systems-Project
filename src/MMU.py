import multiprocessing
import time
import collections


class MMU(multiprocessing.Process):
	def __init__(self, C, app_release, paging, request_queue, scheduler_free, r_schedule, **kwargs):
		super().__init__()
		self.P = kwargs['P'] #no of pages
		self.Phit = kwargs['Phit'] #time to acess ram
		self.Pmiss = kwargs['Pmiss']
		self.T = kwargs['T'] #no of entries in pg table
		self.Taccess = kwargs['Taccess'] #time to access tlb
		self.C = C

		self.paging = paging
		self.request_queue = request_queue
		self.scheduler_free = scheduler_free
		self.r_schedule = r_schedule
		self.app_release = app_release
		self.tlbdict = dict()
		self.request_count = 0
		self.hit_count = 0
		self.total_access_time = 0
		self.service_start_time = 0
		self.updated_count = False
		self.display()		
		self.start()

	def run(self):
		print('MMU started, pid', self.pid)
		while True:			
			target_page = self.request_queue.get()
			if target_page == -1:
				self.flush_tlb()
			elif target_page == -2:
				print('mmu log: stopping mmu')
				print('\nResults:\n')
				print('page faults recorded         =',self.request_count-self.hit_count)
				print('page requests recorded       =',self.request_count)
				print('total access time recorded   =',self.total_access_time)
				print('\n')
				print('page fault rate              =',round((self.request_count-self.hit_count)/self.request_count,2),'fault/request')
				print('effective memory access time =',round(self.total_access_time/self.request_count,2))
				print('number of page faults        =',self.request_count - self.hit_count)
				break
			else:
				if not self.updated_count:
					self.update_counts(target_page)
					self.updated_count = True
				if self.check_tlb(target_page):
					self.task_tlb_access(target_page)
					if self.request_count % self.C == 0:
						self.scheduler_free.acquire()
						self.app_release.acquire()				
						self.flush_tlb()
						self.generate_physical_address(target_page)						
						self.r_schedule.put(-1)
					else:
						self.generate_physical_address(target_page)
				
				else:
					self.task_disk_access(target_page)
					self.update_page_table(target_page)
					self.request_queue.put(target_page)

	def check_tlb(self,target_page):
		self.total_access_time += self.Taccess
		if target_page in self.tlbdict:
			print('tlb hit on page',target_page)		
			return True			
		else: 
			print('tlb miss on page',target_page)
			return False

	def task_tlb_access(self, target_page):	
		self.tlbdict[target_page] = time.time()		
		self.total_access_time += self.Phit
		print('total_access_time =',self.total_access_time)	

	def flush_tlb(self):
		#print('mmu log: tlb flushed')
		self.tlbdict = dict()

	def task_disk_access(self, target_page):
		self.total_access_time += self.Pmiss
		print('total_access_time =',self.total_access_time)		

	def update_page_table(self, target_page):		
		if len(self.tlbdict) < self.T:
			self.tlbdict[target_page] = time.time()
		else:
			evicted_entry = collections.OrderedDict(sorted(self.tlbdict.items(),reverse = True)).popitem()
			del self.tlbdict[evicted_entry[0]]
			self.tlbdict[target_page] = time.time()
		print('updated tlb with page',target_page)

	def update_counts(self,target_page):
			
		self.service_start_time = self.total_access_time
		self.request_count += 1
		if target_page in self.tlbdict:
			self.hit_count += 1

	def generate_physical_address(self, target_page):
		print('serviced page request',target_page,'in',self.total_access_time-self.service_start_time)
		self.updated_count = False
		with self.paging:
			self.paging.notify()

	def display(self):
		print('Details of MMU (P, Phit, Pmiss, T, Taccess):', self.P, self.Phit, self.Pmiss, self.T, self.Taccess)
		pass
