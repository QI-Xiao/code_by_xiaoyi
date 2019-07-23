from multiprocessing import Process
from Data import data_run, fun_test
from GUI import gui_run
from Car_API import api_run


if __name__ == '__main__':

    gui_process = Process(target=gui_run)
    #data_process = Process(target=data_run)
    data_process = Process(target=fun_test)
    api_process = Process(target=api_run)

    gui_process.start()
    data_process.start()
    api_process.start()

    gui_process.join()
    data_process.join()
    api_process.join()
