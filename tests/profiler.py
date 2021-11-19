import cProfile

import seed
import test_util


def __main__():
    print('mmmmm')


def run_test():
    source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
    seed.convert(source, f'{test_util.current_directory()}/netcdf1_fdsnws-dataselect_2021-10-16t19_00_21z.hdf5',
                 data_format='netcdf')
    #print('Hello')


def run():
    pr = cProfile.Profile()
    pr.enable()
    run_test()
    pr.disable()
    # after your program ends
    pr.print_stats(sort="calls")


def main():
    #print("Hello World!")
    pr = cProfile.Profile()
    pr.enable()
    run_test()
    pr.disable()
    # after your program ends
    pr.print_stats(sort="time")




if __name__ == "__main__":
    main()

print("Guru99")
