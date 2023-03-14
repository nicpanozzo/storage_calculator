
from math import ceil

class Disk(object):
    def __init__(self, name, rpm, avarage_seek_time_ms, data_tranfer_Gb_per_s, capacity_GB):
        self.name = name
        self.rpm = rpm
        self.avarage_seek_time_ms = avarage_seek_time_ms
        self.data_tranfer_Gb_per_s = data_tranfer_Gb_per_s
        self.capacity_GB = capacity_GB
        self.avarage_rotational_latency_s = self.calculate_avarage_rotational_latency_s()

    def calculate_avarage_rotational_latency_s(self):
        return 60 / self.rpm * 0.5
    
    def IOPS_disk(self,data_block_size_KB):
        return 0.7 * 1 / self.disk_service_time(data_block_size_KB)
    
    def disk_service_time(self, data_block_size_KB):
        return (self.avarage_seek_time_ms / 1000) + self.avarage_rotational_latency_s + self.data_tranfer_time(data_block_size_KB)
    
    def data_tranfer_time(self, data_block_size_KB):
        return (data_block_size_KB * 8 / 1000000) / self.data_tranfer_Gb_per_s
    
class Requirements(object):
    def __init__(self, block_size_KB, capacity_required_TB, IOPS_peak_required, writes_percentage):
        self.block_size_KB = block_size_KB
        self.capacity_required_TB = capacity_required_TB
        self.IOPS_peak_required = IOPS_peak_required
        self.writes_percentage = writes_percentage
        

class Solver(object):

    def __init__(self, disk: Disk, requirements: Requirements):
        self.disk = disk
        self.requirements = requirements

    def number_of_disks_capacity_required(self, raid = 0):
        total_disks = self.requirements.capacity_required_TB / (self.disk.capacity_GB/1000)
        if raid == 5:
            total_disks = total_disks + 1
        elif raid == 6:
            total_disks = total_disks + 2
        return total_disks

    def minimum_number_of_disks(self, raid = 0):
        return ceil(max(self.number_of_disks_capacity_required(raid), self.number_of_disks_performance_required(raid)))
    

    def disk_service_time(self,avarage_rotational_latency, data_block_size, data_transfer_rate, seek_time):
        return seek_time + avarage_rotational_latency + self.data_tranfer_time(data_block_size, data_transfer_rate)

    def number_of_disks_performance_required(self, raid = 0):
        IOPS_writing = self.requirements.IOPS_peak_required * self.requirements.writes_percentage / 100
        IOPS_reading = self.requirements.IOPS_peak_required * (100 - self.requirements.writes_percentage) / 100
        if raid == 5:
            IOPS_writing = IOPS_writing * 4
        elif raid == 6:
            IOPS_writing = IOPS_writing * 6
        peakIOPS = IOPS_writing+ IOPS_reading
        return peakIOPS / self.disk.IOPS_disk(self.requirements.block_size_KB)  #IOPS_peak_required / IOPS_disk
    
    def percentage_capacity_available(self, raid = 0):
        if raid == 0:
            k = 0
        elif raid == 5:
            k = 1
        elif raid == 6:
            k = 2
        return (self.number_of_disks_capacity_required(raid) - k ) / self.number_of_disks_capacity_required(raid) * 100


    def report(self):
        for raid in [0, 5, 6]:
            
            print("RAID: ", raid)
            print("Number of disks required for capacity: ", self.number_of_disks_capacity_required(raid))
            print("Number of disks required for performance: ", self.number_of_disks_performance_required(raid))
            print("Minimum number of disks required: ", self.minimum_number_of_disks(raid))
            print("Difference between number of disks required performance and capacyty: ", self.number_of_disks_performance_required(raid) - self.number_of_disks_capacity_required(raid))
            print("Total available capacity percentage: ", self.percentage_capacity_available(raid) , "%")
            print("Total capacity: ", self.minimum_number_of_disks(raid) * self.disk.capacity_GB , "GB")
            print("Total capacity available: ", self.minimum_number_of_disks(raid) * self.disk.capacity_GB * self.percentage_capacity_available(raid) / 100, "GB")
            print("")




# My parameters
# TOSHIBA MK3276GSX-50PK LEAFLET

# rpm = 5400
# avarage_seek_time_ms = 12
# data_tranfer_Gb_per_s = 3
# capacity_GB = 320 
# ======================

# EXAMPLE 
#  block_size_KB = 32
#  transfer_rate_MBperS = 40
#  capacity_required_TB = 1.46
#  IOPS_peak_required = 9000
#  IOPS_disk = 180
#  capacity_disk_GB = 146
#  rpm_disk = 15000

# print(number_of_disks_performance_required(9000,IOPS_disk(disk_service_time(15000, 0.032, 40, 0.00275))))
# print(number_of_disks_capacity_required(1.46 * 1024, 146))
# print(minimum_number_of_disks(number_of_disks_performance_required(9000,IOPS_disk(disk_service_time(15000, 0.032, 40, 0.00275))), number_of_disks_capacity_required(1.46 * 1024, 146)))

# print(number_of_disks_performance_required(1600,IOPS_disk(disk_service_time(5400, 0.004, 375, 0.012))))
# print(number_of_disks_capacity_required(7.5 * 1024, 146))
# print(minimum_number_of_disks(number_of_disks_performance_required(1600,IOPS_disk(disk_service_time(5400, 0.004, 375, 0.012))), number_of_disks_capacity_required(7.5 * 1024, 146)))
# # dovrebbe fare 53

# print(avarage_rotational_latency(5400))

# example slides
# diskRequiredPerformance = number_of_disks_performance_required(5200,IOPS_disk(disk_service_time(15000, 0.004, 80, 0.0042)))
# diskRequiredCapacity = number_of_disks_capacity_required(1.5 * 1024, 250)
# print(diskRequiredPerformance)
# print(diskRequiredCapacity)
# print(minimum_number_of_disks(diskRequiredPerformance, diskRequiredCapacity))
# if writing percentage is 21% and reading percentage is 79%
# dovrebbe fare 47 per RAID 0
# dovrebbe fare 77 per RAID 5
# dovrebbe fare 96 per RAID 6


exampledisk = Disk("Example", 15000, 4.2, 40 * 0.008, 146)
exampleRequirements = Requirements(4, 1.5, 5200, 21)

myDisk = Disk("TOSHIBA MK3276GSX", 5400, 12, 3, 320)
myRequirements = Requirements(4, 7.5, 1600, 11)

solver = Solver(exampledisk, exampleRequirements)
# print(solver.number_of_disks_performance_required())
# print(solver.number_of_disks_capacity_required())
# print(solver.minimum_number_of_disks())
# print(solver.number_of_disks_performance_required(5))
# print(solver.minimum_number_of_disks(6))
solver.report()

solver = Solver(myDisk, myRequirements)
solver.report()
# IOPS peak lo moltiplico per la percentuale di scrittura poi mooltiplico per 4 se raid 5 e 6 se raid 6, lo sommo alla percentuale di lettura e questo è il mio nuovo peak IOPS required