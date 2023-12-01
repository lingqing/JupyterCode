import os, sys
import can
from can.io import BLFReader
from canlib import canlib, kvadblib, Frame

filename = '/home/andy/yh_share205_1/问题数据/20220302 86#soc0225_mcu17B8_ICA/canoedata/2022-03-02_16-18-07.blf'
database = '/media/andy/Y/06_Datong_Data/大通5R7V CANoe环境/dbc/CVTC_MIFA_ICE_CANCMX_V2.4.8_C_20220418_ADU.DBC'
# database = '/media/andy/F/大通5R7V CANoe环境/大通5R7V CANoe环境/dbc/ICM_CVTC_MIFA_ICE_CANCMX_V2.4.5_I_20211225_ICU.dbc'
db = kvadblib.Dbc(filename=database)


def parser_msg_with_db(frame, db):
    try:
        bmsg = db.interpret(frame)
    except kvadblib.KvdNoMessage:
        print("<<< No message found for frame with id %s >>>" % frame.id)
        return
    
    if not bmsg._message.dlc == bmsg._frame.dlc:
        print(
            "<<< Could not interpret message because DLC does not match for"
            f" frame with id {frame.id} >>>"
        )
        print(f"\t- DLC (database): {bmsg._message.dlc}")
        print(f"\t- DLC (received frame): {bmsg._frame.dlc}")
        return

    msg = bmsg._message
    
    # 根据信号名 赋值 给object 成员变量
    for bsig in bmsg:
        # if bsig.name == 'AEBSta' or bsig.name == 'VehSpd':
        #     print(bsig.name, bsig.value)
        # name_type = bsig.name[6:]  
        # if name_type in switch.keys():
        #     # print(bsig.name, bsig.value)
        #     index = int(msg.name[16])-1

        #     if name_type == 'sync_Frame_Index':
        #         last_index = eyeq_objs.objs[index].get_value(switch[name_type])
        #         eyeq_objs.objs[index].set_value(switch[name_type + '_last'], last_index)
        #         # print('update -----> ',last_index, bsig.value)
        #     eyeq_objs.objs[index].set_value(switch[name_type], bsig.value)

        print('┏', msg.name)
        try:
            if msg.comment:
                print('┃', '"%s"' % msg.comment)

            for bsig in bmsg:
                print('┃', bsig.name + ':', bsig.value, bsig.unit)
        except Exception as e:
            print(e)
        print('┗')

def get_unvalid_aebsta(filename):
    with can.BLFReader(filename) as reader:
        
        for msg in reader:
            if msg.arbitration_id == 0x150:
            # if msg.arbitration_id in [0x189]:
                if ((msg.data[4] & 0xE0) >> 5) == 0:
                    print('\033[31m AEBSta Unvalid : %s\033[0m'%filename)
                    return True
                    # break
                
                # print(msg)
                # frame       = Frame(msg.arbitration_id, data=msg.data, dlc=msg.dlc)
                # # print(msg.arbitration_id)
                # # print(msg)
                # parser_msg_with_db(frame, db)
                # print(int.from_bytes(msg.data[37:40], 'big'))
                # print(((msg.data[4] & 0xE0) >> 5))
    return False

def print_aebsta(filename):
    with can.BLFReader(filename) as reader:
        
        for msg in reader:
            if msg.arbitration_id == 0x150:
            # if msg.arbitration_id in [0x189]:
                aeb_sta = (msg.data[4] & 0xE0) >> 5
                if aeb_sta == 0:
                    print('\033[31m AEBSta Unvalid : %d\033[0m'%aeb_sta)
                else:
                    print(' AEBSta   valid : %d'%aeb_sta)
                    # break

def gen_blf_filelists(out_file, in_path):
    out_names = open(out_file, 'w')
    for root, dirs, files in os.walk(in_path):
        for name in files:
            if name.endswith('.blf'):
                print(name)
                out_names.write('%s\n' % os.path.join(root, name))
    out_names.close()
    
if __name__ == '__main__':
    if len(sys.argv) >= 2:
        ##
        # gen_blf_filelists('blf_filelist.txt', sys.argv[2])
        # for fn in open('blf_filelist1.txt', 'r').readlines():
        #     print(fn.strip())
        #     get_unvalid_aebsta(fn.strip())
        
        print_aebsta(sys.argv[1])
        
                