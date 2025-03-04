#!/usr/bin/env python3

# This script demonstrates the usage, capability and features of the library.

import argparse
import sys
import time
from datetime import datetime

from bluepy.btle import BTLEDisconnectError

from constants import MUSICSTATE
from miband import miband
import config


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mac', required=False, help='Set mac address of the device')
parser.add_argument('-k', '--authkey', required=False, help='Set Auth Key for the device')
args = parser.parse_args()


# if args.mac:

    
# Convert Auth Key from hex to byte format
AUTH_KEY = bytes.fromhex(config.AUTH_KEY)



# Needs Auth
def get_step_count():
    binfo = band.get_steps()
    print ('Number of steps: ', binfo['steps'])
    print ('Fat Burned: ', binfo['fat_burned'])
    print ('Calories: ', binfo['calories'])
    print ('Distance travelled in meters: ', binfo['meters'])
    input('Press a key to continue')


def general_info():
    print ('MiBand')
    print ('Soft revision:',band.get_revision())
    print ('Hardware revision:',band.get_hrdw_revision())
    print ('Serial:',band.get_serial())
    print ('Battery:', band.get_battery_info()['level'])
    print ('Time:', band.get_current_time()['date'].isoformat())
    input('Press a key to continue')


def send_notif():
    title = input ("Enter title or phone number to be displayed: ")
    print ('Reminder: at Mi Band 4 you have 10 characters per line, and up to 6 lines. To add a new line use new line character \n')
    msg = input ("Enter optional message to be displayed: ")
    ty= int(input ("1 for Mail / 2 for Message / 3 for Missed Call / 4 for Call: "))
    if(ty > 4 or ty < 1):
        print ('Invalid choice')
        time.sleep(2)
        return
    a=[1,5,4,3]
    band.send_custom_alert(a[ty-1],title,msg)


def activity_log_callback(timestamp,c,i,s,h):
    print("{}: category: {}; intensity {}; steps {}; heart rate {};\n".format( timestamp.strftime('%d.%m - %H:%M'), c, i ,s ,h))

#Needs auth    
def get_activity_logs():
    #gets activity log for this day.
    temp = datetime.now()
    band.get_activity_betwn_intervals(datetime(temp.year,temp.month,temp.day),datetime.now(),activity_log_callback)
    while True:
        band.waitForNotifications(0.2)

# Needs Auth
def get_heart_rate():
    print ('Latest heart rate is : %i' % band.get_heart_rate_one_time())
    input('Press a key to continue')


def heart_logger(data):
    print ('Realtime heart BPM:', data)


# Needs Auth
def get_realtime():
    band.start_heart_rate_realtime(heart_measure_callback=heart_logger)
    input('Press Enter to continue')


# Needs Auth
def restore_firmware():
    print("This feature has the potential to brick your Mi Band 4. You are doing this at your own risk.")
    path = input("Enter the path of the firmware file :")
    band.dfuUpdate(path)

# Needs Auth
def update_watchface():
    path = input("Enter the path of the watchface .bin file :")
    band.dfuUpdate(path)



# Needs Auths
def set_time():
    now = datetime.now()
    print ('Set time to:', now)
    band.set_current_time(now)


# default callbacks        
def _default_music_play():
    print("Played. key press 101", flush=True)
    # sys.stdout.write("Played... key press 111")
    # sys.stdout.flush()

def _default_music_pause():
    print("Paused. key press 102", flush=True)
    band.track="paused"
    band.setMusic()

def _default_music_forward():
    print("Forward. key press 104", flush=True)
    band.track="new title"
    band.setMusic()

def _default_music_back():
    print("Backward. key press 103", flush=True)

def _default_music_vup():
    print("volume up. key press 106", flush=True)
    
def _default_music_vdown():
    print("volume down. key press 105", flush=True)

def _default_music_focus_in():
    print("Music focus in. key press 121", flush=True)

def _default_music_focus_out():
    print("Music focus out. key press 122", flush=True)

def mb_event_find_device_start():
    print("find_device_event start. key press 123", flush=True)

def mb_event_find_device_end():
    print("event_find_device end. key press 124", flush=True)

def mb_event_watchface_changed():
    print("event_watchface_changed. key press 125", flush=True)


def set_music(): 
    band.setMusicCallback(_default_music_play,_default_music_pause,_default_music_forward,_default_music_back,_default_music_vup,_default_music_vdown,_default_music_focus_in,_default_music_focus_out)
    fi = input("Set music track artist to : ")
    fj = input("Set music track album to: ")
    fk = input("Set music track title to: ")
    fl = int(input("Set music volume: "))
    fm = int(input("Set music position: "))
    fn = int(input("Set music duration: "))
    band.setTrack(MUSICSTATE.PLAYED,fi,fj,fk,fl,fm,fn)
    while True:
        if band.waitForNotifications(0.5):
            continue
    input("enter any key")


def mb_test_set_music():
    band.event_watchface_changed = mb_event_watchface_changed
    band.setLostDeviceCallback(mb_event_find_device_start, mb_event_find_device_end)
    band.setMusicCallback(_default_music_play,_default_music_pause,_default_music_forward,_default_music_back,_default_music_vup,_default_music_vdown,_default_music_focus_in,_default_music_focus_out)
    fi = "ar"
    fj = "l"
    fk = "title track"
    fl = int(1)
    fm = int(9)
    fn = int(55)
    band.setTrack(MUSICSTATE.PLAYED,fi,fj,fk,fl,fm,fn)
    band.waitForNotifications(0.5)



def mb_notifications():
    from constants import UUIDS
    band._desc_music_notif.write(b'\x01\x00')
    band._cccd_chunked = band._char_chunked.getDescriptors(forUUID=UUIDS.NOTIFICATION_DESCRIPTOR)[0]
    band._cccd_chunked.write(b'\x01\x00')

    char_0007 = band.svc_1.getCharacteristics(UUIDS.CHARACTERISTIC_STEPS)[0]
    cccd_0007 = char_0007.getDescriptors(forUUID=UUIDS.NOTIFICATION_DESCRIPTOR)[0]
    cccd_0007.write(b'\x01\x00')



if __name__ == "__main__":
    success = False
    while not success:
        try:
            if (AUTH_KEY):
                band = miband(config.MAC_ADDRESS, AUTH_KEY, debug=True)
                success = band.initialize()
                # band.mb_notifications(True)
                mb_test_set_music()
                while True:
                    band.waitForNotifications(1.1)
            else:
                print("no AUTH_KEY")
                band = miband(config.MAC_ADDRESS, debug=True)
                success = True            
            break
        except BTLEDisconnectError:
            print('Connection to the MIBand failed. Trying out again in 3 seconds')
            time.sleep(11)
            continue
        except KeyboardInterrupt:
            print("\nExit.")
            exit()


    


    
