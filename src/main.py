import re
import os
import multiprocessing
import App
import Scheduler
import MMU

if __name__ == '__main__':
	apps = []
	scheduler = None
	mmu = None	

	r_schedule = multiprocessing.Queue()
	paging = multiprocessing.Condition()
	request_queue = multiprocessing.Queue()
	scheduler_free = multiprocessing.Semaphore(1)
	scheduler_free.acquire()
	app_release = multiprocessing.Semaphore(1)

	#configure apps
	for app in open('app_file.txt'):
		app_kwargs = {}
		app_lock = multiprocessing.Semaphore(1)
		app_lock.acquire()
		for header,value in re.findall(r'(\w+)=(["\w+]+)',app):
			app_kwargs[header]=eval(value)
		new_app = App.App(app_lock, app_release, r_schedule, scheduler_free, 
							request_queue, paging, **app_kwargs)
		apps.append((new_app.pid, app_lock))

	#configure scheduler
	with open('scheduler_file.txt') as fil:
		config_scheduler = {}
		for header,value in re.findall(r'(\w+)=(["\w+]+)',fil.read()):
			config_scheduler[header]=eval(value)
		scheduler = Scheduler.Scheduler(app_release, r_schedule, scheduler_free, 
											request_queue, apps, **config_scheduler)

	#configure mmu
	with open('mmu_file.txt') as fil:
		config_mmu = {}
		for header,value in re.findall(r'(\w+)=(["\w+]+)',fil.read()):
			config_mmu[header]=eval(value)
		mmu = MMU.MMU(scheduler.C, app_release, paging, request_queue,
						 scheduler_free, r_schedule, **config_mmu)

	#schedule first app
	scheduler.schedule_one()
